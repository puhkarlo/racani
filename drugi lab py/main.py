from pyglet.gl import *
from pyglet.window import key
import numpy as np
from OpenGL import GL as gl

window = pyglet.window.Window(700, 800, 'Dimni SOS signal')
dt = 1 / 30.0
teksture = []
brojac = 0
kratkiSignali = True
reset = 1
brzina = 2
X = 0
Y = -500
Z = -500
Y_ROT = 0


class Tekstura:
    def __init__(self, x=-27.5, y=0):
        self.x = x
        self.y = y
        self.zivot = 0
        self.width = 55
        self.height = 55
        self.tekstura = pyglet.image.load('smoke.bmp').get_texture()

    def provjeriZivot(self):
        return self.zivot < 12

    def azurirajZivotIPoziciju(self):
        self.zivot += dt
        self.y += brzina

        if 440 < self.y < 480:
            self.width += 0.2
            self.height += 0.2
            self.x -= 1
        elif 200 < self.y < 320 or 480 < self.y < 520:
            self.width += 0.2
            self.height += 0.2
            self.x += 1
        elif 320 < self.y < 440 or 520 < self.y < 630:
            self.x -= 1

    def crtaj(self):
        glEnable(self.tekstura.target)
        glBindTexture(self.tekstura.target, self.tekstura.id)



        glPushMatrix()
        matrica = (gl.GLfloat * 16)()
        gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, matrica)
        matrica = list(matrica)
        pocetna_orijentacija = np.array([0, 0, 1])
        ciljna_orijentacija = np.array([matrica[2], matrica[6], matrica[10]])
        os_rotacije = np.cross(pocetna_orijentacija, ciljna_orijentacija)
        skalarni_produkt = np.dot(pocetna_orijentacija, ciljna_orijentacija)

        kut_rotacije = np.rad2deg(
            np.arccos(skalarni_produkt / (np.linalg.norm(pocetna_orijentacija) * np.linalg.norm(ciljna_orijentacija))))
        gl.glRotate(kut_rotacije, os_rotacije[0], os_rotacije[1], os_rotacije[2])
        self.tekstura.blit(self.x, self.y, width=self.width, height=self.height)

        # print(kut_rotacije, os_rotacije)
        glPopMatrix()


def azuriraj(pom):
    global reset
    for tekstura in teksture:
        if tekstura.provjeriZivot():
            tekstura.azurirajZivotIPoziciju()
        else:
            teksture.remove(tekstura)
    if teksture and reset < 9:
        stvoriNiz(teksture[-1].y)


def stvoriNiz(y):
    global brojac, kratkiSignali, reset
    if (kratkiSignali and y == 84) or (not kratkiSignali and y == 132):
        teksture.append(Tekstura())
        reset += 1
        brojac += 1
        if brojac == 2:
            kratkiSignali = not kratkiSignali
            brojac = -1


@window.event
def on_key_press(symbol, modifiers):
    global X, Y, Z, Y_ROT
    if symbol == key.UP:
        Z += 10
    if symbol == key.DOWN:
        Z -= 10
    if symbol == key.A:
        X -= 10
    if symbol == key.D:
        X += 10
    if symbol == key.W:
        Y += 10
    if symbol == key.S:
        Y -= 10
    if symbol == key.E:
        Y_ROT += 5
    if symbol == key.Q:
        Y_ROT -= 5
    # print(Y_ROT)


@window.event()
def on_draw():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 1, 700)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    pos = [X, Y, Z]
    glTranslatef(*pos)
    glRotatef(Y_ROT, 0, 1, 0)

    for tekstura in teksture:
        tekstura.crtaj()
    # print('---')


if __name__ == '__main__':
    teksture.append(Tekstura())
    pyglet.clock.schedule_interval(azuriraj, dt)
    pyglet.app.run()

import ctypes

import numpy as np
from pyglet.gl import *

putanja = 'putanja.obj'
objekt = 'F16.obj'
vrhovi = []
poligoni = []
cvorovi = []
s = np.array([0.0, 0.0, 1.0])

t = 0.0
delta = 0.08
segment = 0

width = 1300
height = 890
window = pyglet.window.Window(width, height)
cameraPositon = (1.0, 1.0, 1.3)
lookAt = (0.0, 0.0, 0.0)
upVector = (0.0, 1.0, 0.0)

B = np.array(
    [[-1.0 / 6, 0.5, -0.5, 1.0 / 6],
     [0.5, -1.0, 0.5, 0.0],
     [-0.5, 0.0, 0.5, 0.0],
     [1.0 / 6, 2.0 / 3, 1.0 / 6, 0.0]])


def parserPutanje():
    xPom = []
    yPom = []
    zPom = []
    obj = open(putanja, 'r')
    for linija in obj:
        pom = linija.split()
        pom1 = float(pom[1])
        pom2 = float(pom[2])
        pom3 = float(pom[3])
        cvorovi.append([pom1, pom2, pom3])
        xPom.append(pom1)
        yPom.append(pom2)
        zPom.append(pom3)
    obj.close()

    rez =  max(max(xPom) - min(xPom), max(yPom) - min(yPom), max(zPom) - min(zPom))
    #print(rez)
    return rez


def parserObjekta():
    obj = open(objekt, 'r')
    for linija in obj:
        if linija.startswith('#') or linija.startswith('g'):
            pass
        elif linija.startswith('v'):
            pom = linija.split()
            pom1 = [float(pom[1]), float(pom[2]), float(pom[3])]
            vrhovi.append(pom1)
        elif linija.startswith('f'):
            pom2 = linija.split()
            pom3 = [int(pom2[1]), int(pom2[2]), int(pom2[3])]
            poligoni.append(pom3)
    obj.close()


def rotacija(e):
    kutRad = np.arccos(np.dot(s, e) / (np.linalg.norm(s) * np.linalg.norm(e)))
    return np.cross(s, e), np.rad2deg(kutRad)  # vracam os i kut u stupnjevima


def tangenta(t, R):
    T = np.array([3 * t ** 2, 2 * t, 1, 0])
    pom = np.dot(T, B)
    return np.dot(pom, R)


def dr_der(t, R):
    T = np.array([6 * t, 2, 0, 0])
    pom = np.dot(T, B)
    return np.dot(pom, R)


def normala(t, R):
    return np.cross(tangenta(t, R), dr_der(t, R))
    # return dr_der(t, R)


def racunajSegment(t, R):
    T = np.array([t ** 3, t ** 2, t, 1])
    pom = np.dot(T, B)
    return np.dot(pom, R)


def krivulja(skaliranje):
    glBegin(GL_LINE_STRIP)
    for i in range(len(cvorovi) - 3):
        R = np.array([cvorovi[i], cvorovi[i + 1], cvorovi[i + 2], cvorovi[i + 3]])
        for j in np.linspace(0, 1, 18):
            pom = racunajSegment(j, R)
            pom2 = tangenta(j, R)
            glVertex3f(pom[0] / skaliranje, pom[1] / skaliranje, pom[2] / skaliranje)
            glVertex3f(pom[0] / skaliranje + pom2[0] / skaliranje, pom[1] / skaliranje + pom2[1] / skaliranje,
                       pom[2] / skaliranje + pom2[2] / skaliranje)
    glEnd()


def crtajObjekt():
    glBegin(GL_TRIANGLES)
    for pol in poligoni:
        for tocka in pol:
            glColor3f(0.0, 0.0, 1.0)
            glVertex3f(vrhovi[tocka - 1][0], vrhovi[tocka - 1][1], vrhovi[tocka - 1][2])
    glEnd()


def dcm(t, R):
    norm = normala(t, R)
    tan = tangenta(t, R)
    bi_norm = np.cross(tan, norm)
    rez = np.array([[tan[0], norm[0], bi_norm[0], 0],
                    [tan[1], norm[1], bi_norm[1], 0],
                    [tan[2], norm[2], bi_norm[2], 0],
                    [0, 0, 0, 1]])
    rezInv = np.linalg.inv(rez)
    pom = []
    for i in range(4):
        for j in range(4):
            pom.append(rezInv[j][i])
    pom = (ctypes.c_float * len(pom))(*pom)
    return pom


def azuriraj(x, d_t):
    global t
    global segment
    global delta
    t += delta
    if t >= 1.0:
        t = 0
        segment += 1
    if segment >= len(cvorovi) - 3:
        segment = 0


@window.event
def on_draw():
    R = np.array([cvorovi[segment], cvorovi[segment + 1], cvorovi[segment + 2], cvorovi[segment + 3]])

    vrh = racunajSegment(t, R)
    tan = tangenta(t, R)
    os, kut = rotacija(tan)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, float(width) / float(height), 0.5, 100)
    gluLookAt(cameraPositon[0], cameraPositon[1], cameraPositon[2],
              lookAt[0], lookAt[1], lookAt[2],
              upVector[0], upVector[1], upVector[2])
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    krivulja(skaliranje)

    glTranslatef(vrh[0] / skaliranje, vrh[1] / skaliranje, vrh[2] / skaliranje)
    glScalef(1 / 7, 1 / 7, 1 / 7)
    glRotatef(kut, os[0], os[1], os[2])
    crtajObjekt()


if __name__ == '__main__':
    parserObjekta()

    skaliranje = parserPutanje()

    pyglet.clock.schedule(azuriraj, 1 / 20.0)

    pyglet.app.run()

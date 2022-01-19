from pyglet.gl import *
from pyglet.window import key
import math

window = pyglet.window.Window(1100, 650, 'Air hockey')
bg = pyglet.resource.image("field.png")
dt = 1 / 60.0
keys = {}
speed = 9.5
next_player = 1
game_on = False
game_over = False


class Player:
    def __init__(self, x, y, player, color, radius):
        self.x = x
        self.y = y
        self.player = player
        self.score = 0
        self.radius = radius
        self.color = color

    def move_player(self, dx=0, dy=0):
        if (self.x + self.radius + dx > 454 or self.x - self.radius + dx < 12) and self.player == 1:
            dx = 0
        if (self.x - self.radius + dx < 646 or self.x + self.radius + dx > 1088) and self.player == 2:
            dx = 0
        if self.y - self.radius + dy < 12 or self.y + self.radius + dy > 638:
            dy = 0
        self.x += dx
        self.y += dy

    def update_score(self):
        self.score += 1

    def draw_player(self):
        player = pyglet.shapes.Circle(x=self.x, y=self.y, radius=self.radius, color=self.color[0])
        player_inside = pyglet.shapes.Circle(x=self.x, y=self.y, radius=24, color=self.color[1])
        player_inside_deep = pyglet.shapes.Circle(x=self.x, y=self.y, radius=14, color=self.color[0])
        player.draw()
        player_inside.draw()
        player_inside_deep.draw()

    def reset_player(self, x, y):
        self.x = x
        self.y = y


class Ball:
    def __init__(self, x, y, color, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.alpha = math.radians(180)
        self.color = color

    def draw_ball(self):
        ball = pyglet.shapes.Circle(x=self.x, y=self.y, radius=self.radius, color=self.color)
        ball_inside = pyglet.shapes.Circle(x=self.x, y=self.y, radius=6, color=(255, 255, 255))
        ball.draw()
        ball_inside.draw()

    def update_position(self):
        cosinus = math.cos(self.alpha)
        ball_dx = abs(cosinus) * speed

        if self.alpha < 0:
            self.alpha += 2 * math.pi
        if 0 <= self.alpha < math.pi / 2 or 3 * math.pi / 2 < self.alpha < 2 * math.pi:
            self.y += math.sin(self.alpha) / cosinus * ball_dx
            self.x += ball_dx
        elif self.alpha == math.pi / 2:
            self.y += ball_dx
        elif self.alpha == 3 * math.pi / 2:
            self.y -= ball_dx
        else:
            self.y += math.sin(self.alpha) / cosinus * ball_dx * (-1)
            self.x -= ball_dx

        return self.check_walls()

    def check_walls(self):
        if (self.x + self.radius >= 1092 or self.x - self.radius <= 8) and (250 < self.y < 415):
            if self.x > 500:
                return 1
            else:
                return 2
        if self.y + self.radius >= 642 or self.y - self.radius <= 8:
            self.alpha *= -1
        if self.x + self.radius >= 1092 or self.x - self.radius <= 8:
            self.alpha = math.pi - self.alpha
        if self.alpha < 0:
            self.alpha += 2 * math.pi

        if self.x < 0 or self.y < 0 or self.x > 1100 or self.y > 650:
            ball.reset_ball(math.radians(45))

        return 0

    def reset_ball(self, angle):
        self.x = 500
        self.y = 325
        self.alpha = angle


@window.event
def on_key_press(symbol, modifiers):
    keys[symbol] = True


@window.event
def on_key_release(symbol, modifiers):
    try:
        del keys[symbol]
    except:
        pass


@window.event()
def on_draw():
    global game_over, game_on
    window.clear()
    bg.blit(0, 0)

    if game_on:
        ball.draw_ball()
    player_1.draw_player()
    player_2.draw_player()

    if player_1.score == 5:
        score_label.text = 'Player 1 won!'
        score_label.x = 410
        game_over = True
    elif player_2.score == 5:
        score_label.text = 'Player 2 won!'
        score_label.x = 410
        game_over = True
    else:
        score_label.text = str(player_1.score) + '  ' + str(player_2.score)
    score_label.draw()
    score_label.x = 510

    if not game_on or game_over:
        play_label.draw()


def check_collision(player, ball):
    if math.sqrt((ball.x - player.x) ** 2 + (ball.y - player.y) ** 2) <= player.radius + ball.radius:
        if ball.x > player.x and ball.y >= player.y:
            if abs(ball.x - player.x) == 0:
                ball.alpha = math.atan(0)
            else:
                ball.alpha = math.atan((ball.y - player.y) / (ball.x - player.x))
        elif ball.x < player.x and ball.y < player.y:
            if abs(ball.x - player.x) == 0:
                ball.alpha = math.pi + math.atan(0)
            else:
                ball.alpha = math.pi + math.atan(abs(ball.y - player.y) / abs(ball.x - player.x))
        elif ball.x < player.x and ball.y >= player.y:
            if abs(ball.x - player.x) == 0:
                ball.alpha = math.pi - math.atan(0)
            else:
                ball.alpha = math.pi - math.atan(abs(ball.y - player.y) / abs(ball.x - player.x))
        else:
            if abs(ball.x - player.x) == 0:
                ball.alpha = - math.atan(0)
            else:
                ball.alpha = - math.atan(abs(ball.y - player.y) / abs(ball.x - player.x))
        return True
    return False


def update_position(var):
    global next_player, game_on, game_over
    goal = 0

    # moving of the ball
    if game_on:
        goal = ball.update_position()

    if goal == 1:
        player_1.score += 1
        ball.reset_ball(0)
        next_player = 2
        player_1.reset_player(x=50, y=325)
        player_2.reset_player(x=1050, y=325)
        game_on = False
    elif goal == 2:
        player_2.score += 1
        ball.reset_ball(math.pi)
        player_1.reset_player(x=50, y=325)
        player_2.reset_player(x=1050, y=325)
        next_player = 1
        game_on = False

    # moving players with keyboard
    if key.UP in keys:
        player_2.move_player(dy=7)
    if key.DOWN in keys:
        player_2.move_player(dy=-7)
    if key.LEFT in keys:
        player_2.move_player(dx=-7)
    if key.RIGHT in keys:
        player_2.move_player(dx=7)
    if key.W in keys:
        player_1.move_player(dy=7)
    if key.S in keys:
        player_1.move_player(dy=-7)
    if key.A in keys:
        player_1.move_player(dx=-7)
    if key.D in keys:
        player_1.move_player(dx=7)

    # play game
    if key.SPACE in keys:
        game_on = True
        if game_over:
            player_1.score = 0
            player_2.score = 0
            game_over = False

    # reset ball manually
    if key.R in keys:
        ball.reset_ball(math.radians(33))

    # check if players are in collision with the ball
    if next_player == 1 and check_collision(player_1, ball):
        next_player = 2
    if next_player == 2 and check_collision(player_2, ball):
        next_player = 1


if __name__ == '__main__':
    player_1 = Player(x=50, y=325, player=1, color=[(20, 100, 244), (255, 255, 255)], radius=34)
    player_2 = Player(x=1050, y=325, player=2, color=[(255, 226, 59), (255, 255, 255)], radius=34)
    ball = Ball(x=500, y=325, color=(245, 42, 42), radius=17)
    score_label = pyglet.text.Label(text=str(player_1.score) + '  ' + str(player_2.score), x=510, y=590,
                                    color=(245, 42, 42, 255), font_size=33)
    play_label = pyglet.text.Label(text='Press SPACE to play!', x=370, y=180,
                                   color=(245, 42, 42, 255), font_size=28)
    pyglet.clock.schedule_interval(update_position, dt)
    pyglet.app.run()

from pygame import image, display, init, quit, event as events, K_ESCAPE, K_DOWN, K_LEFT, K_RIGHT, K_UP
from pygame import KEYDOWN, QUIT, KEYUP, Surface, SRCALPHA, gfxdraw, time
from generate_orbits_diagram import draw_orbits, orbitas, radiuses
from pygame.sprite import Sprite, LayeredUpdates
from math import sin, cos, radians
from os import getcwd, path
from decimal import Decimal
from sys import exit
from random import randint

init()
fps = time.Clock()
fondo = display.set_mode((1200, 600))
bg_rect = fondo.get_rect()

bg_stars = image.load(path.join(getcwd(), 'data', 'estrellas.png'))
w, h = bg_stars.get_size()
rect = bg_stars.get_rect(topleft=(0, 0))
draw_orbits(bg_stars, orbitas, radiuses)

fondo.blit(bg_stars, (0, 0))

planets = LayeredUpdates()


class Planet(Sprite):
    centerx = 0
    centery = h//2
    speed = 0

    def __init__(self, r):
        super().__init__()
        is_a_planet = False
        radio = int(Decimal(r) * Decimal(100.0))
        self.radius = radio
        self.angle = randint(0, 360)
        self.speed = radio
        if orbitas['habitable zone'][0] < r < orbitas['habitable zone'][1]:  # main planet
            self.image = Surface((6, 6), SRCALPHA)
            gfxdraw.filled_circle(self.image, 3, 3, 3, (255, 0, 255))
            is_a_planet = True

        elif r in orbitas['inner']:  # terrestial planets
            self.image = Surface((6, 6), SRCALPHA)
            gfxdraw.filled_circle(self.image, 3, 3, 3, (255, 0, 0))
            is_a_planet = True

        elif r in orbitas['outer']:  # gas giants
            self.image = Surface((22, 22), SRCALPHA)
            gfxdraw.filled_circle(self.image, 11, 11, 11, (0, 0, 255))
            is_a_planet = True

        if is_a_planet:
            width_2 = self.image.get_width() // 2
            self.rect = self.image.get_rect(topleft=(radio - width_2, h // 2))

        self.is_a_planet = is_a_planet

    @staticmethod
    def set_xy(center, radius, angle, off_x=0, off_y=0):
        x = round(off_x + center[0] + radius * cos(radians(angle)))
        y = round(off_y + center[1] + radius * sin(radians(angle)))
        return x, y

    def update(self, delta_x=0, delta_y=0):
        if 0 <= self.angle + 1 <= 360:
            self.angle += (self.radius/360)
        else:
            self.angle = 0
        self.centerx += delta_x
        self.centery += delta_y
        x, y = self.set_xy([self.centerx-1, self.centery], self.radius, self.angle, delta_x, delta_y)

        self.rect.topleft = (x, y)


for ridx in radiuses:
    p = Planet(ridx)
    if p.is_a_planet:
        planets.add(p)

dx, dy = 0, 0
while True:
    fps.tick(30)
    for e in events.get((KEYDOWN, KEYUP, QUIT)):
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            quit()
            exit()

        elif e.type == KEYDOWN:
            if e.key == K_UP:
                dy -= 1
            elif e.key == K_DOWN:
                dy += 1
            elif e.key == K_LEFT:
                dx -= 3
            elif e.key == K_RIGHT:
                dx += 3

        elif e.type == KEYUP:
            if e.key == K_UP or e.key == K_DOWN:
                dy = 0
            elif e.key == K_LEFT or e.key == K_RIGHT:
                dx = 0

    if rect.right + dx > 1200 and rect.left + dx <= 0 and rect.top + dy <= 0 and rect.bottom + dy > 600:
        rect.move_ip(dx, dy)
        planets.update(dx, dy)
    fondo.blit(bg_stars, rect.topleft)

    planets.draw(fondo)
    display.update()

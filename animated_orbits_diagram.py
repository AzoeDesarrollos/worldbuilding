from pygame import image, display, init, quit, event as events, K_ESCAPE, K_DOWN, K_LEFT, K_RIGHT, K_UP
from pygame import KEYDOWN, QUIT, KEYUP, Surface, SRCALPHA, gfxdraw, font, time
from generate_orbits_diagram import draw_orbits, abrir_json
from pygame.sprite import Sprite, LayeredUpdates
from math import sin, cos, radians
from os import getcwd, path
from decimal import Decimal
from sys import exit
from random import randint

init()
fps = time.Clock()

orbitas = abrir_json(path.join(getcwd(), 'data.json'))
radiuses = [item for sublist in orbitas.values() for item in sublist]
radiuses.sort()

bg_stars = image.load(path.join(getcwd(), 'data', 'estrellas.png'))
w, h = bg_stars.get_size()
rect = bg_stars.get_rect(topleft=(0, 0))


class RotatingPlanet(Sprite):
    centerx = 0
    centery = h // 2
    displaced = False

    def __init__(self, r):
        super().__init__()
        is_a_planet = False
        self._r = r
        self.radius = int(Decimal(self._r) * Decimal(100.0))
        self.angle = randint(0, 360)
        if orbitas['habitable zone'][0] < self._r < orbitas['habitable zone'][1]:  # main planet
            self.image = Surface((6, 6), SRCALPHA)
            gfxdraw.filled_circle(self.image, 3, 3, 3, (255, 0, 255))
            is_a_planet = True

        elif self._r in orbitas['inner']:  # terrestial planets
            self.image = Surface((6, 6), SRCALPHA)
            gfxdraw.filled_circle(self.image, 3, 3, 3, (255, 0, 0))
            is_a_planet = True

        elif self._r in orbitas['outer']:  # gas giants
            self.image = Surface((22, 22), SRCALPHA)
            gfxdraw.filled_circle(self.image, 11, 11, 11, (0, 0, 255))
            is_a_planet = True

        if is_a_planet:
            width_2 = self.image.get_width() // 2
            self.w2 = width_2
            self.rect = self.image.get_rect(topleft=(self.radius - width_2, h // 2))

        self.is_a_planet = is_a_planet

    def set_xy(self, off_x=0, off_y=0):
        x = round(off_x + (self.centerx - self.w2) + self.radius * cos(radians(self.angle)))
        y = round(off_y + self.centery + self.radius * sin(radians(self.angle)))
        self.rect.topleft = (x, y)

    def displace(self, delta_x, delta_y):
        self.centerx += delta_x
        self.centery += delta_y
        self.set_xy(delta_x, delta_y)
        self.displaced = True

    def update(self):
        delta = (1 / (self._r / 360)) / 200
        if 0 <= self.angle + delta < 360:
            self.angle += delta  # velocidad angular, pero en realidad es un mamarracho.
        else:
            self.angle = -delta

        self.set_xy()


def topdown_loop():
    blanco = 255, 255, 255
    negro = 0, 0, 0

    fondo = display.set_mode((1200, 600))
    bg_rect = fondo.get_rect()
    draw_orbits(bg_stars, radiuses, orbitas)

    f1 = font.SysFont('Verdana', 12)
    f2 = font.SysFont('Verdana', 16, bold=True)

    text = f2.render('Top-Down View', 1, blanco, negro)
    text_rect = text.get_rect()

    planets = LayeredUpdates()
    for ridx in radiuses:
        p = RotatingPlanet(ridx)
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
                    dy += 3
                elif e.key == K_DOWN:
                    dy -= 3
                elif e.key == K_LEFT:
                    dx += 3
                elif e.key == K_RIGHT:
                    dx -= 3

            elif e.type == KEYUP:
                if e.key == K_UP or e.key == K_DOWN:
                    dy = 0
                elif e.key == K_LEFT or e.key == K_RIGHT:
                    dx = 0

        if rect.right + dx > 1200 and rect.left + dx <= 0 and rect.top + dy <= 0 and rect.bottom + dy > 600:
            rect.move_ip(dx, dy)
            for planet in planets:
                # noinspection PyUnresolvedReferences
                planet.displace(dx, dy)

        fondo.blit(bg_stars, rect.topleft)
        planets.update()
        planets.draw(fondo)

        for i, planet in enumerate(planets):
            render = f1.render(str(round(planet.angle))+'°', 1, (255, 255, 255), (0, 0, 0))
            if i % 2 == 0:
                j = 11
            else:
                j = -11
            renderrect = render.get_rect(left=planet.radius + rect.x + 3, centery=rect.centery + j)
            fondo.fill((0, 0, 0), renderrect)
            fondo.blit(render, (*renderrect.topleft, 8 * 3, 21))
        fps_render = f1.render(str(round(fps.get_fps())), 1, blanco, negro)
        fps_rect = fps_render.get_rect(topright=(bg_rect.right, 0))
        fondo.blit(text, text_rect)
        fondo.blit(fps_render, fps_rect)
        display.update()


if __name__ == '__main__':
    topdown_loop()

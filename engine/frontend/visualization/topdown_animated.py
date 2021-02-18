from pygame import KEYDOWN, QUIT, KEYUP, Surface, SRCALPHA, gfxdraw, font, time, PixelArray, Color
from pygame import image, display, event as events, K_ESCAPE, K_DOWN, K_LEFT, K_RIGHT, K_UP
from engine.frontend.globales import WidgetGroup
from math import sin, cos, radians, pow, sqrt
from engine.backend import abrir_json, roll
from decimal import Decimal, getcontext
from pygame.sprite import Sprite
from os import getcwd, path
from random import randint


def paint_stars(surface, i, f):
    width, height = surface.get_size()
    px_array = PixelArray(surface)
    for i in range(i, f):
        x = roll(1, width - 1)
        y = roll(1, height - 1)
        rand_color = Color([255, roll(0, 255), roll(100, 255), 255])
        rand_color_bg = rand_color
        rand_color_bg.a = 125
        if roll(0, 100) >= 50:
            px_array[x, y] = rand_color
        else:
            try:
                px_array[x - 1, y] = rand_color
                px_array[x, y] = rand_color
                px_array[x + 1, y] = rand_color

                px_array[x, y - 1] = rand_color
                px_array[x, y] = rand_color
                px_array[x, y + 1] = rand_color

            except IndexError:
                px_array[(x, y)] = rand_color

    surface = px_array.make_surface()
    px_array.close()
    return surface


def draw_orbits(fondo, radix, orbits):
    getcontext().prec = 2
    surf_rect = fondo.get_rect()

    gfxdraw.filled_circle(fondo, *surf_rect.midleft, 20, (255, 255, 0))
    for r in radix:
        e = 0.0
        b = r * sqrt(1 - pow(e, 2))
        semi_major = int(Decimal(r) * Decimal(100.0))
        semi_minor = int(Decimal(b)*Decimal(100.0))
        if r in orbits['frost line']:  # frost line
            color = 0, 0, 255
            semi_minor = semi_major
        elif r in orbits['habitable zone']:  # habitable zone
            color = 0, 255, 0
            semi_minor = semi_major
        else:
            color = 125, 125, 125
        gfxdraw.ellipse(fondo, *surf_rect.midleft, semi_major, semi_minor, color)


class RotatingPlanet(Sprite):
    centerx = 0
    centery = 384
    displaced = False

    def __init__(self, a, e=0):
        super().__init__()
        is_a_planet = False
        self._r = a
        b = a * sqrt(1 - pow(e, 2))
        self.major = int(Decimal(a) * Decimal(100.0))
        self.minor = int(Decimal(b) * Decimal(100.0))
        self.angle = randint(0, 360)

        if self._r in orbitas['inner']:  # terrestial planets
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
            self.rect = self.image.get_rect(topleft=(self.major - width_2, self.centery))
            self.set_xy()

        self.is_a_planet = is_a_planet

    def set_xy(self, off_x=0, off_y=0):
        x = round(off_x + (self.centerx - self.w2) + self.major * cos(radians(self.angle)))
        y = round(off_y + self.centery + self.minor * sin(radians(self.angle)))
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

    fondo = display.set_mode((590, 630))
    bg_rect = fondo.get_rect()
    draw_orbits(bg_stars, radiuses, orbitas)

    f1 = font.SysFont('Verdana', 12)
    f2 = font.SysFont('Verdana', 16, bold=True)

    text = f2.render('Top-Down View', 1, blanco, negro)
    text_rect = text.get_rect()

    planets = WidgetGroup()
    for ridx in radiuses:
        p = RotatingPlanet(ridx)
        if p.is_a_planet:
            planets.add(p)

    dx, dy = 0, 0
    running = True
    while running:
        fps.tick(30)
        for e in events.get((KEYDOWN, KEYUP, QUIT)):
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                running = False

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

        if rect.right + dx > 590 and rect.left + dx <= 0 and rect.top + dy <= 0 and rect.bottom + dy > 630:
            rect.move_ip(dx, dy)
            for planet in planets.widgets():
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

    display.quit()


if __name__ == '__main__':
    fps = time.Clock()

    orbitas = abrir_json(path.join(getcwd(), 'data', 'data.json'))
    radiuses = [item for sublist in orbitas.values() for item in sublist]
    radiuses.sort()

    bg_stars = image.load(path.join(getcwd(), 'data', 'estrellas.png'))
    rect = bg_stars.get_rect(topleft=(0, 0))
    topdown_loop()

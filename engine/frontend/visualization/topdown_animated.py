from pygame import image, display, event as events, K_ESCAPE, K_DOWN, K_LEFT, K_RIGHT, K_UP, SCALED, K_SPACE
from pygame import KEYDOWN, QUIT, KEYUP, Surface, SRCALPHA, gfxdraw, font, time, PixelArray
from engine.backend.eventhandler import EventHandler
from engine.frontend.globales.constantes import *
from engine.frontend.globales import WidgetGroup
from math import sin, cos, radians, ceil
from decimal import Decimal, getcontext
from pygame.sprite import Sprite
from engine.backend import roll
from os import getcwd, path


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


def draw_orbits(fondo, system):
    getcontext().prec = 2
    surf_rect = fondo.get_rect()

    if system.star_system.letter == 'P':
        for star in system.star_system:
            semi_major = int(Decimal(star.orbit.a.m) * Decimal(100.0))
            semi_minor = int(Decimal(star.orbit.b.m) * Decimal(100.0))
            gfxdraw.ellipse(fondo, *surf_rect.midleft, semi_major, semi_minor, COLOR_STARORBIT)

    for planet in system.planets:
        if planet.orbit is not None:
            semi_major = int(Decimal(planet.orbit.a.m) * Decimal(100.0))
            semi_minor = int(Decimal(planet.orbit.b.m) * Decimal(100.0))
            gfxdraw.ellipse(fondo, *surf_rect.midleft, semi_major, semi_minor, COLOR_STARORBIT)

    for radius in [system.star_system.habitable_inner.m, system.star_system.habitable_outer.m]:
        scaled = int(Decimal(radius) * Decimal(100.0))
        try:
            gfxdraw.ellipse(fondo, *surf_rect.midleft, scaled, scaled, COLOR_HABITABLE)
        except OverflowError:
            print(f' habitable radius of {scaled} exceeds the maximum?')

    scaled = int(Decimal(system.star_system.frost_line.m) * Decimal(100.0))
    try:
        gfxdraw.ellipse(fondo, *surf_rect.midleft, *[scaled]*2, (0, 0, 255))
    except OverflowError:
        print(f'frost line radius of {scaled} exceeds the maximum?')


class RotatingAstro(Sprite):
    displaced = False
    direction = 'CW'

    def __init__(self, orbit, centery):
        super().__init__()
        self.centery = centery
        self.centerx = 0  # for simmetry

        self.tracked_orbit = orbit
        self.speed = (360/orbit.period.to('day').m)/10
        self.major = int(Decimal(orbit.a.m) * Decimal(100.0))
        self.minor = int(Decimal(orbit.b.m) * Decimal(100.0))
        self.angle = self.tracked_orbit.true_anomaly.m

        self.rect = self.image.get_rect(center=(self.major, self.centery))
        self.set_direction()
        self.set_xy()

    def set_xy(self, off_x=0, off_y=0):
        x = round(off_x + self.centerx + self.major * cos(radians(self.angle)))
        y = round(off_y + self.centery + self.minor * sin(radians(self.angle)))
        self.rect.center = (x, y)

    def displace(self, delta_x, delta_y):
        self.centerx += delta_x
        self.centery += delta_y
        self.set_xy(delta_x, delta_y)
        self.displaced = True

    def set_direction(self):
        orbit = self.tracked_orbit
        direction = orbit.direction
        star_spin = orbit.star.spin

        if direction == 'prograde':
            self.direction = star_spin
        elif direction == 'retrograde':
            self.direction = 'clockwise' if star_spin == 'counter-clockwise' else 'counter-clockwise'

    def spin(self, direction):
        if direction == 'clockwise':
            if 0 <= self.angle + self.speed < 360:
                self.angle += self.speed
            else:
                self.angle = -self.speed

        elif direction == 'counter-clockwise':
            if 0 <= self.angle - self.speed < 360:
                self.angle -= self.speed
            else:
                self.angle = 360

    def update(self):
        self.spin(self.direction)
        self.tracked_orbit.set_true_anomaly(self.angle)
        self.set_xy()


class TranslatingAstro(RotatingAstro):
    def __init__(self, planet_obj, centery):
        size = 0
        color = None
        if planet_obj.clase == 'Terrestial Planet':
            if planet_obj.habitable:
                color = COLOR_HABITABLE
            else:
                color = COLOR_TERRESTIAL
            size = 4
        elif planet_obj.clase in ('Gas Giant', 'Super Jupiter'):
            color = COLOR_GASGIANT
            size = 11
        elif planet_obj.clase == 'Puffy Giant':
            color = COLOR_PUFFYGIANT
            size = 11
        elif planet_obj.clase == 'Gas Dwarf':
            color = COLOR_GASDWARF
            size = 5
        elif planet_obj.clase == 'Dwarf Planet':
            color = COLOR_DWARFPLANET
            size = 3

        self.create(size, color)
        super().__init__(planet_obj.orbit, centery)

    def create(self, size, color):
        size_2 = size * 2
        size_3 = [size] * 3
        self.image = Surface((size_2, size_2), SRCALPHA)
        gfxdraw.aacircle(self.image, *size_3, color)
        gfxdraw.filled_circle(self.image, *size_3, color)


class RotatingStar(RotatingAstro):
    def __init__(self, star, dy):
        radius = ceil(Decimal(star.radius.m) * Decimal(3.5))
        self.image = Surface([radius*2, radius*2], SRCALPHA)
        self.rect = self.image.get_rect()
        gfxdraw.aacircle(self.image, *self.rect.center, radius, star.color)
        gfxdraw.filled_circle(self.image, *self.rect.center, radius, star.color)
        self.tracked_orbit = star
        super().__init__(star.orbit, dy+ceil(star.orbit.a.m*100))
        self.direction = star.spin

    def set_direction(self):
        pass


def topdown_loop(system):
    blanco = 255, 255, 255
    negro = 0, 0, 0
    fondo = display.set_mode((ANCHO, ALTO), SCALED)
    bg_rect = fondo.get_rect()

    bg_stars = image.load(path.join(getcwd(), 'data', 'estrellas.png'))
    rect = bg_stars.get_rect(centery=bg_rect.centery)

    draw_orbits(bg_stars, system)

    f1 = font.SysFont('Verdana', 12)
    f2 = font.SysFont('Verdana', 16, bold=True)

    text = f2.render('Top-Down View', 1, blanco, negro)
    text_rect = text.get_rect()

    astros = WidgetGroup()
    t_p = TranslatingAstro
    astros.add([t_p(planet, rect.centery) for planet in system.planets if planet.orbit is not None], layer=2)

    if system.star_system.letter is None:
        astros.add(RotatingStar(system.star_system, bg_rect.centery), layer=1)

    elif system.star_system.letter == 'P':
        for star in system.star_system:
            astros.add(RotatingStar(star, bg_rect.centery), layer=1)

    fps = time.Clock()
    dx, dy = 0, 0
    running = True
    while running:
        fps.tick(30)
        for e in events.get((KEYDOWN, KEYUP, QUIT)):
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                running = False
                EventHandler.trigger('salir', 'engine', {'mensaje': 'normal'})

            elif e.type == KEYDOWN:
                if e.key == K_UP:
                    dy += 10
                elif e.key == K_DOWN:
                    dy -= 10
                elif e.key == K_LEFT:
                    dx += 10
                elif e.key == K_RIGHT:
                    dx -= 10

                elif e.key == K_SPACE:
                    running = False

            elif e.type == KEYUP:
                if e.key == K_UP or e.key == K_DOWN:
                    dy = 0
                elif e.key == K_LEFT or e.key == K_RIGHT:
                    dx = 0

        if rect.right + dx > ANCHO and rect.left + dx <= 0:
            rect.move_ip(dx, 0)
        else:
            dx = 0

        if rect.top + dy <= 0 and rect.bottom + dy > ALTO:
            rect.move_ip(0, dy)
        else:
            dy = 0

        if dx or dy:
            for planet in astros.widgets():
                planet.displace(dx, dy)

        fondo.blit(bg_stars, rect.topleft)
        astros.update()
        astros.draw(fondo)

        for i, planet in enumerate(astros.get_widgets_from_layer(2)):
            render = f1.render(str(round(planet.angle)) + '°', 1, blanco, negro)
            if i % 2 == 0:
                j = 11
            else:
                j = -11
            renderrect = render.get_rect(left=planet.major + rect.x + 3, centery=rect.centery + j)
            fondo.fill((0, 0, 0), renderrect)
            fondo.blit(render, (*renderrect.topleft, 8 * 3, 21))
        fps_render = f1.render(str(round(fps.get_fps())), 1, blanco, negro)
        fps_rect = fps_render.get_rect(topright=(bg_rect.right, 0))
        fondo.blit(text, text_rect)
        fondo.blit(fps_render, fps_rect)
        display.update()

    display.quit()
    return

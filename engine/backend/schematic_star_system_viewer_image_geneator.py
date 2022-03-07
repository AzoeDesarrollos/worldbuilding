from pygame import PixelArray, Color, draw, image, font, Rect, Surface
from engine.frontend.globales.constantes import *
from decimal import Decimal, getcontext
from random import randint
from os.path import join
from math import sin, cos, pi


def paint_stars(surf, i, f):
    w, h = surf.get_size()
    px_array = PixelArray(surf)
    for i in range(i, f):
        x = randint(1, w - 1)
        y = randint(1, h - 1)
        rand_color = Color([255, randint(0, 255), randint(100, 255)])
        rand_color_bg = rand_color
        rand_color_bg.a = 125
        if randint(0, 100) >= 50:
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


def point(radius, n, rect):
    x = rect.centerx + int(radius * cos(n * pi))
    y = rect.centery + int(radius * sin(n * pi))
    return x, y


def draw_orbits(fondo, star, orbits, planets):
    fuente = font.SysFont('Verdana', 16)
    getcontext().prec = 2
    surf_rect = fondo.get_rect()

    draw.circle(fondo, star.color, surf_rect.midleft, 100)  # star

    rect = Rect(-surf_rect.centerx, -surf_rect.centery, 100 * star.frost_line.m * 2, 100 * star.frost_line.m * 2)
    # rect.center = surf_rect.midleft
    for angle in range(0, 360):
        for i in [angle+j/10 for j in range(10)]:
            x, y = point(star.frost_line.m*10, i, rect)
            # if surf_rect.collidepoint(x, y):
            fondo.set_at((x, y), Color(255, 255, 255))

    habitable_in = star.habitable_inner.m
    radio = int(Decimal(habitable_in) * Decimal(1000.0))
    rect = Rect(0, 0, radio, radio)
    rect.center = surf_rect.midleft
    color = Color(0, 255, 0)
    draw.ellipse(fondo, color, rect, 1)

    habitable_out = star.habitable_outer.m
    radio = int(Decimal(habitable_out) * Decimal(1000.0))
    rect = Rect(0, 0, radio, radio)
    rect.center = surf_rect.midleft
    color = Color(0, 255, 0)
    draw.ellipse(fondo, color, rect, 1)

    for orbit in orbits:
        radio = int(Decimal(orbit) * Decimal(1000.0))
        rect = Rect(0, 0, radio, radio)
        rect.center = surf_rect.midleft
        color = COLOR_STARORBIT
        draw.ellipse(fondo, color, rect, 1)

    centery = surf_rect.centery
    for i, astro in enumerate(planets):
        pos = (rect.right - 1, centery)
        size = 0
        if astro.celestial_type not in ('star', 'system'):
            if astro.clase == 'Terrestial Planet':
                size = 4
                if astro.habitable:
                    color = COLOR_HABITABLE
                else:
                    color = COLOR_TERRESTIAL
            elif astro.clase in ('Gas Giant', 'Super Jupiter'):
                size = 11
                color = COLOR_GASGIANT
            elif astro.clase == 'Puffy Giant':
                size = 11
                color = COLOR_PUFFYGIANT
            elif astro.clase == 'Gas Dwarf':
                size = 6
                color = COLOR_GASDWARF
            elif astro.clase == 'Dwarf Planet':
                color = COLOR_DWARFPLANET
                size = 3
            elif astro.comp == 'Rocky':
                size = 2
                color = COLOR_ROCKYMOON
            elif astro.comp == 'Icy':
                size = 2
                color = COLOR_ICYMOON
            elif astro.comp == 'Iron':
                size = 2
                color = COLOR_IRONMOON

        draw.circle(fondo, color, pos, size)
        render = fuente.render(str(astro), True, COLOR_SELECTED)
        if i % 2 == 0:
            render_rect = render.get_rect(centerx=pos[0], centery=centery + 23)
        else:
            render_rect = render.get_rect(centerx=pos[0], centery=centery - 23)
        fondo.blit(render, render_rect)

    return fondo


def generate_diagram(ruta, star, planets):
    sequence = [(0, 901), (902, 1800), (1801, 2700), (2701, 3600), (3601, 4500)]
    surf = Surface((23000, 768))

    # for inicio, fin in sequence:
    #     surf = paint_stars(surf, inicio, fin)

    orbitas = [planet.orbit.a.to('au').m for planet in planets]
    orbitas.sort()

    surf = draw_orbits(surf, star, orbitas, planets)

    image.save(surf, join(ruta, star.id + '.png'))

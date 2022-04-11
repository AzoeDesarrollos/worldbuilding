from pygame import PixelArray, Color, draw, image, font, Rect, Surface
from engine.frontend.globales.constantes import *
from decimal import Decimal, getcontext
from random import randint
from os.path import join


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


def draw_orbits(fondo, system):
    fuente = font.SysFont('Verdana', 16)
    getcontext().prec = 2
    surf_rect = fondo.get_rect()

    planets = [planet for planet in system.planets if planet.orbit is not None]
    satellites = [sat for sat in system.satellites if sat.orbit is not None]
    orbits = [planet.orbit.a.to('au').m for planet in planets]
    sat_orb = [sat.orbit.a.to('au').m for sat in satellites]
    sats = dict(zip(satellites, sat_orb))
    orbits.sort()

    star = system.star_system
    draw.circle(fondo, star.color, surf_rect.midleft, 100)  # star

    radio = int(Decimal(star.frost_line.m) * Decimal(1000.0))
    rect = Rect(0, 0, radio * 2, radio * 2)
    rect.center = surf_rect.midleft
    color = Color(0, 125, 255)
    draw.circle(fondo, color, rect.center, radio, width=1)

    habitable_in = star.habitable_inner.m
    radio = int(Decimal(habitable_in) * Decimal(1000.0))
    rect = Rect(0, 0, radio, radio)
    rect.center = surf_rect.midleft
    color = Color(0, 255, 0)
    draw.circle(fondo, color, rect.center, radio, width=1)

    habitable_out = star.habitable_outer.m
    radio = int(Decimal(habitable_out) * Decimal(1000.0))
    rect = Rect(0, 0, radio, radio)
    rect.center = surf_rect.midleft
    color = Color(0, 255, 0)
    draw.circle(fondo, color, rect.center, radio, width=1)

    for orbit in orbits:
        radio = int(Decimal(orbit) * Decimal(1000.0))
        rect = Rect(0, 0, radio, radio)
        rect.center = surf_rect.midleft
        color = COLOR_STARORBIT
        draw.circle(fondo, color, rect.center, radio, width=1)

    for body, orbit in sats:
        radio = int(Decimal(orbit) * Decimal(1000.0))
        rect = Rect(0, 0, radio, radio)
        rect.centerx = int(Decimal(body.orbit.a.to('au').m) * Decimal(1000.0))
        rect.centery = surf_rect.centery
        color = COLOR_STARORBIT
        draw.circle(fondo, color, rect.center, radio, width=1)

    centery = surf_rect.centery
    for i, astro in enumerate(planets):
        orbit = int(Decimal(astro.orbit.a.to('au').m) * Decimal(1000.0))
        pos = (orbit, centery)
        size = 0
        if astro.celestial_type not in ('star', 'system'):
            if astro.clase == 'Terrestial Planet':
                size = 4
                if astro.habitable:
                    color = COLOR_HABITABLE
                else:
                    color = COLOR_TERRESTIAL
            elif astro.clase in ('Gas Giant', 'Super Jupiter'):
                size = 44
                color = COLOR_GASGIANT
            elif astro.clase == 'Puffy Giant':
                size = 43
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

        rect = draw.circle(fondo, color, pos, size)
        render = fuente.render(str(astro), True, COLOR_SELECTED)
        if i % 2 == 0:
            render_rect = render.get_rect(centerx=pos[0], centery=rect.top - 23)
        else:
            render_rect = render.get_rect(centerx=pos[0], centery=rect.bottom + 23)
        fondo.blit(render, render_rect)

    return fondo


def generate_diagram(ruta, system):
    sequence = [(0, 901), (902, 1800), (1801, 2700), (2701, 3600), (3601, 4500), (4501, 5000), (5001, 10000)]
    surf = Surface((system.star_system.outer_boundry.m * 1000, 768))
    fuente = font.SysFont('Verdana', 14, bold=True)
    render = fuente.render('Not to scale', True, COLOR_SELECTED)
    for inicio, fin in sequence:
        surf = paint_stars(surf, inicio, fin)

    # orbitas = [planet.orbit.a.to('au').m for planet in system.planets if planet.orbit is not None]
    # planets = [planet for planet in planets if planet.orbit is not None]
    # orbitas.sort()

    surf = draw_orbits(surf, system)
    surf.blit(render, (0, 0))

    image.save(surf, join(ruta, system.star_system.id + '.png'))

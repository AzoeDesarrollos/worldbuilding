from pygame import gfxdraw, Rect, PixelArray, Color
from decimal import Decimal, getcontext
from random import randint
from json import load


def paint_stars(surface, i, f):
    w, h = surface.get_size()
    px_array = PixelArray(surface)
    for i in range(i, f):
        x = randint(1, w - 1)
        y = randint(1, h - 1)
        rand_color = Color([255, randint(0, 255), randint(100, 255), 255])
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


def draw_orbits(fondo, radix, orbits):
    getcontext().prec = 2
    surf_rect = fondo.get_rect()

    gfxdraw.filled_circle(fondo, *surf_rect.midleft, 20, (255, 255, 0))
    for r in radix:
        radio = int(Decimal(r) * Decimal(100.0))
        rect = Rect(0, 0, radio, radio)
        rect.center = surf_rect.midleft
        if r in orbits['frost line']:  # frost line
            color = 0, 0, 255
        elif r in orbits['habitable zone']:  # habitable zone
            color = 0, 255, 0
        else:
            color = 125, 125, 125
        gfxdraw.ellipse(fondo, *surf_rect.midleft, radio, radio, color)


def abrir_json(archivo, encoding='utf-8'):
    with open(archivo, encoding=encoding) as file:
        return load(file)

from pygame import font, gfxdraw, Rect, PixelArray, Color  # , image, Surface, SRCALPHA
from decimal import Decimal, getcontext
from random import randint
from json import load
from os import getcwd, path
from math import cos, sin, radians

font.init()


def set_xy(center, radius, angle: int):
    x = round(center[0] + radius * cos(radians(angle)))
    y = round(center[1] + radius * sin(radians(angle)))
    return x, y


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


def draw_orbits(fondo, orbits, radix):
    getcontext().prec = 2
    surf_rect = fondo.get_rect()

    gfxdraw.filled_circle(fondo, *surf_rect.midleft, 20, (255, 255, 0))
    for r in radix:
        radio = int(Decimal(r) * Decimal(100.0))

        # condition = False
        # x, y = radio, surf_rect.centery
        # while not condition:
        #     a = randint(-90, 90)
        #     x, y = set_xy(surf_rect.midleft, radio, a)
        #     condition = surf_rect.collidepoint(x, y)
        rect = Rect(0, 0, radio, radio)
        rect.center = surf_rect.midleft
        if r in orbits['frost line']:  # frost line
            color = 0, 0, 255
        elif r in orbits['habitable zone']:  # habitable zone
            color = 0, 255, 0
        else:
            color = 125, 125, 125
        gfxdraw.ellipse(fondo, *surf_rect.midleft, radio, radio, color)

    #     if orbits['habitable zone'][0] < r < orbits['habitable zone'][1]:  # main planet
    #         gfxdraw.filled_circle(fondo, x, y, 3, (255, 0, 255))
    #
    #     elif r in orbits['inner']:  # terrestial planets
    #         gfxdraw.filled_circle(fondo, x, y, 3, (255, 0, 0))
    #
    #     elif r in orbits['outer']:  # gas giants
    #         gfxdraw.filled_circle(fondo, x, y, 11, (0, 0, 255))
    #
    # return fondo


def abrir_json(archivo, encoding='utf-8'):
    with open(archivo, encoding=encoding) as file:
        return load(file)


# if path.exists(path.join(getcwd(), 'data/estrellas.png')):
#     surf = image.load(path.join(getcwd(), 'data/estrellas.png'))
# else:
#     surf = Surface((4500, 768), SRCALPHA)
#     surf.fill((0, 0, 0, 255))
#
#     surf = paint_stars(surf, 0, 5000)
#     image.save(surf, path.join(getcwd(), 'data/estrellas.png'))
#
orbitas = abrir_json(path.join(getcwd(), 'data.json'))

radiuses = [item for sublist in orbitas.values() for item in sublist]
radiuses.sort()
#
# surf = draw_orbits(surf, orbitas, radiuses)
#
# image.save(surf, path.join(getcwd(), 'data/orbitas.png'))

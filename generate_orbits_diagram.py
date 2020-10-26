from pygame import font, draw, Rect, PixelArray, Color, image, Surface, SRCALPHA
from decimal import Decimal, getcontext
from random import randint, seed
from os.path import join
from json import load
from os import getcwd

font.init()
seed(1)


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
    centery = surf_rect.centery
    draw.circle(fondo, (255, 255, 0), surf_rect.midleft, 100)  # star

    fuente = font.SysFont('Verdana', 16)
    blanco = 255, 255, 255
    par = True
    for r in radix:
        radio = int(Decimal(r) * Decimal(1000.0))
        rect = Rect(0, 0, radio, radio)
        rect.center = surf_rect.midleft
        if r in orbits['frost line']:  # frost line
            color = 0, 0, 255
        elif r in orbits['habitable zone']:  # habitable zone
            color = 0, 255, 0
        else:
            color = 125, 125, 125
        draw.ellipse(fondo, color, rect, 1)

        pos = (rect.right - 1, centery)
        render = None
        if r in orbits['inner']:  # terrestial planets
            draw.circle(fondo, (255, 0, 0), pos, 3)
            render = fuente.render('Terrestial', True, blanco)

        elif r in orbits['habitable']:  # main planet
            draw.circle(fondo, (255, 0, 255), pos, 3)
            render = fuente.render('Habitable', True, blanco)

        elif r in orbits['outer']:  # gas giants
            draw.circle(fondo, (0, 0, 255), pos, 11)
            render = fuente.render('Gas Giant', True, blanco)

        if any([r in orbits['inner'], r in orbits['habitable'], r in orbits['outer']]):
            par = not par

        if render is not None:
            if par:
                render_rect = render.get_rect(centerx=pos[0], centery=centery + 23)
            else:
                render_rect = render.get_rect(centerx=pos[0], centery=centery - 23)
            fondo.blit(render, render_rect)

    return fondo


def abrir_json(archivo, encoding='utf-8'):
    with open(archivo, encoding=encoding) as file:
        return load(file)


sequence = [
    (0, 901),
    (902, 1800),
    (1801, 2700),
    (2701, 3600),
    (3601, 4500),
    (4501, 5000),
    (5001, 10000)
]

surf = Surface((20520, 768), SRCALPHA)
surf.fill((0, 0, 0, 255))
for inicio, fin in sequence:
    surf = paint_stars(surf, inicio, fin)

orbitas = abrir_json(join(getcwd(), 'data.json'))

radiuses = [item for sublist in orbitas.values() for item in sublist]
radiuses.sort()

surf = draw_orbits(surf, orbitas, radiuses)

image.save(surf, join(getcwd(), 'data/orbitas.png'))

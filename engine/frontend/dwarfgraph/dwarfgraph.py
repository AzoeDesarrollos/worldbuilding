from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_TEXTO
from pygame import KEYDOWN, QUIT, K_ESCAPE, MOUSEMOTION, K_SPACE
from pygame import display, event, font, transform, image
from engine.frontend.graph.graph import pos_to_keys
from pygame import init, quit
from math import pi, pow
from os.path import join
from os import getcwd
from sys import exit


def density(m, r):
    return m / ((4 / 3) * pi * pow(r, 3))


mass_keys = [0.1]
mass_keys += [i / 10000 for i in range(1, 10)]
mass_keys += [i / 1000 for i in range(1, 10)]
mass_keys += [i / 100 for i in range(1, 10)]
mass_keys.sort()

radius_keys = [i / 100 for i in range(3, 10)] + [i / 10 for i in range(1, 6)]

init()

fuente = font.SysFont('Verdana', 13)
mass_imgs = [fuente.render(str(mass_keys[i]), True, COLOR_TEXTO, COLOR_BOX) for i in range(len(mass_keys))]
radius_imgs = [fuente.render(str(radius_keys[i]), True, COLOR_TEXTO, COLOR_BOX) for i in range(len(radius_keys))]

exes, yes = [], []

ruta = join(getcwd(), 'engine', 'frontend', 'dwarfgraph', 'dwarfgraph.png')
bg = image.load(ruta)
bg_rect = bg.get_rect(topleft=(54, 24))


def dwarfgraph_loop():
    fondo = display.set_mode((ANCHO, ALTO))
    fondo.fill(COLOR_BOX)

    fuente2 = font.SysFont('Verdana', 13, bold=True)

    render = fuente2.render('Mass', True, COLOR_TEXTO, COLOR_BOX)
    render = transform.rotate(render, -90)
    render_rect = render.get_rect(right=ANCHO - 53, centery=ALTO / 2)
    fondo.blit(render, render_rect)

    render = fuente2.render('Radius', True, COLOR_TEXTO, COLOR_BOX)
    render_rect = render.get_rect(x=3, y=3)
    fondo.blit(render, render_rect)

    text_mass = 'Mass: N/A'
    text_radius = 'Radius: N/A'
    text_density = 'Density: N/A'
    w, h = 0, 0

    for i in [i for i in range(len(radius_keys))]:
        img = radius_imgs[i]
        rect = img.get_rect(x=i * 40 + 53, y=3)
        exes.append(rect.centerx)
        w += rect.w + 13
        fondo.blit(img, rect)

    for i in [i for i in range(len(mass_keys))]:
        img = mass_imgs[i]
        rect = img.get_rect(right=53, centery=i * 20 + 32)
        yes.append(rect.y - 16)
        h += rect.h + 3
        fondo.blit(img, rect)

    done = False
    data = {}

    while not done:
        for e in event.get([KEYDOWN, QUIT, MOUSEMOTION]):
            if (e.type == KEYDOWN and e.key == K_ESCAPE) or e.type == QUIT:
                quit()
                exit()

            elif e.type == MOUSEMOTION:
                x, y = e.pos
                if bg_rect.collidepoint(x, y):
                    mass = round(pos_to_keys(y - 26, mass_keys, yes, 'gt'), 5)
                    radius = round(pos_to_keys(x, radius_keys, exes, 'gt'), 3)
                    data.update({'mass': mass, 'radius': radius, 'clase': 'Dwarf Planet'})
                    d = density(mass, radius)
                    text_mass = 'Mass: {}'.format(mass)
                    text_radius = 'Radius: {}'.format(radius)
                    text_density = 'Density: {}'.format(d)
                else:
                    text_mass = 'Mass: N/A'
                    text_radius = 'Radius: N/A'
                    text_density = 'Density: N/A'
            elif e.type == KEYDOWN:
                if e.key == K_SPACE:
                    done = True

        render_mass = fuente.render(text_mass, True, COLOR_TEXTO, COLOR_BOX)
        render_radius = fuente.render(text_radius, True, COLOR_TEXTO, COLOR_BOX)
        render_density = fuente.render(text_density, True, COLOR_TEXTO, COLOR_BOX)

        fondo.fill(COLOR_BOX, (0, ANCHO, ALTO - 20, 50))
        fondo.blit(render_mass, (3, ALTO - 20))
        fondo.blit(render_radius, (150, ALTO - 20))
        fondo.blit(render_density, (300, ALTO - 20))

        fondo.blit(bg, bg_rect)
        display.update()

    display.quit()
    return data

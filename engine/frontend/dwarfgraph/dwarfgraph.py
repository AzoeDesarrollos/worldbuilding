from pygame import KEYDOWN, QUIT, K_ESCAPE, MOUSEMOTION, K_SPACE, KEYUP, K_LSHIFT, K_LCTRL
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_TEXTO
from engine.frontend.graph.graph import pos_to_keys, Linea, Punto
from pygame import display, event, font, transform, image
from engine.frontend.globales import WidgetGroup
from pygame.sprite import Sprite
from pygame import init, quit
from math import pi, pow
from os.path import join
from os import getcwd
from sys import exit


def density(m, r):
    return m / ((4 / 3) * pi * pow(r, 3))


class Number(Sprite):
    def __init__(self, imagen, **kwargs):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect(**kwargs)


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

    numbers = WidgetGroup()
    for i in [i for i in range(len(radius_keys))]:
        n = Number(radius_imgs[i], x=i * 40 + 53, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i for i in range(len(mass_keys))]:
        n = Number(mass_imgs[i], right=53, centery=i * 20 + 32)
        numbers.add(n)
        yes.append(n.rect.y - 16)

    done = False
    data = {}

    lineas = WidgetGroup()
    linea_h = Linea(bg_rect, bg_rect.x, bg_rect.centery, bg_rect.w, 1, lineas)
    linea_v = Linea(bg_rect, bg_rect.centerx, bg_rect.y, 1, bg_rect.h, lineas)
    punto = Punto(bg_rect, bg_rect.centerx, bg_rect.centery, lineas)

    move_x, move_y = True, True
    while not done:
        for e in event.get([KEYDOWN, QUIT, MOUSEMOTION, KEYUP]):
            if (e.type == KEYDOWN and e.key == K_ESCAPE) or e.type == QUIT:
                quit()
                exit()

            elif e.type == MOUSEMOTION:
                x, y = e.pos

                if move_y:
                    linea_h.move_y(y)
                    punto.move_y(y)

                if move_x:
                    linea_v.move_x(x)
                    punto.move_x(x)

                if bg_rect.collidepoint(x, y):
                    mass = round(pos_to_keys(linea_h.rect.y - 26, mass_keys, yes, 'gt'), 5)
                    radius = round(pos_to_keys(linea_v.rect.x, radius_keys, exes, 'gt'), 3)
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

                elif e.key == K_LSHIFT:
                    move_x = False

                elif e.key == K_LCTRL:
                    move_y = False

            elif e.type == KEYUP:
                if e.key == K_LSHIFT:
                    move_x = True

                elif e.key == K_LCTRL:
                    move_y = True

        render_mass = fuente.render(text_mass, True, COLOR_TEXTO, COLOR_BOX)
        render_radius = fuente.render(text_radius, True, COLOR_TEXTO, COLOR_BOX)
        render_density = fuente.render(text_density, True, COLOR_TEXTO, COLOR_BOX)

        fondo.fill(COLOR_BOX)
        fondo.blit(render_mass, (3, ALTO - 20))
        fondo.blit(render_radius, (150, ALTO - 20))
        fondo.blit(render_density, (300, ALTO - 20))

        fondo.blit(bg, bg_rect)
        numbers.draw(fondo)
        lineas.update()
        lineas.draw(fondo)
        display.update()

    display.quit()
    return data

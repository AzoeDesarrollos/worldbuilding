from pygame import KEYDOWN, QUIT, K_ESCAPE, MOUSEMOTION, MOUSEBUTTONDOWN, K_SPACE, image, K_LSHIFT, K_LCTRL, KEYUP
from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, ANCHO, ALTO
from pygame import init, quit, display, font, event, Rect, Surface
from ..common import pos_to_keys, keys_to_pos,  Linea, Punto
from engine.frontend.globales import WidgetGroup
from pygame.sprite import Sprite
from sys import exit
from os.path import join
from os import getcwd
from math import pi


def density(m, r):
    return m / ((4 / 3) * pi * pow(r, 3))


radius_keys = [1 + i / 100 for i in range(-3, 11)] + [1 + i / 10 for i in range(2, 10)]
mass_keys = [i / 100 for i in range(3, 11)]
mass_keys += [i / 10 for i in range(2, 10)]
mass_keys += [i for i in range(1, 14)]

init()
fuente = font.SysFont('Verdana', 11)
fuente2 = font.SysFont('Verdana', 13)
mass_imgs = [fuente.render(str(mass_keys[i]), True, COLOR_TEXTO, COLOR_BOX) for i in range(len(mass_keys))]
radius_imgs = [fuente.render(str(radius_keys[i]), True, COLOR_TEXTO, COLOR_BOX) for i in range(len(radius_keys))]

exes, yes = [], []

ruta = join(getcwd(), 'engine', 'frontend', 'graphs', 'gasgraph', 'gasgraph.png')
img_rect = Rect(31, 16, 540, 570)
img = image.load(ruta)


class Number(Sprite):
    def __init__(self, imagen, **kwargs):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect(**kwargs)


def gasgraph_loop(limit_mass):
    done = False
    data = {}
    text_mass = 'Mass: N/A'
    text_radius = 'Radius: N/A'
    text_density = 'Density: N/A'
    invalid = True

    fondo = display.set_mode((ANCHO, ALTO))
    fondo.fill(COLOR_BOX)

    numbers = WidgetGroup()
    for i in [i for i in range(len(radius_keys[:4]))]:
        n = Number(radius_imgs[i], x=i * 28 + 30, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i + 4 for i in range(len(radius_keys[4:14]))]:
        n = Number(radius_imgs[i], x=i * 27 + 26, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i + 14 for i in range(len(radius_keys[14:]))]:
        n = Number(radius_imgs[i], x=i * 22 + 90, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i for i in range(len(mass_keys))]:
        n = Number(mass_imgs[i], right=30, centery=i * 20 + 21)
        numbers.add(n)
        yes.append(n.rect.centery)

    x = exes[radius_keys.index(1.02)]
    y = yes[mass_keys.index(2)]

    rect_super = Rect(31, y + 16, x - 3, (img_rect.h / 2) - 60)
    rect_puffy = Rect(x + 28, 16, (img_rect.w / 2) + 100, y)
    rect_giant = Rect(31, 16, x - 3, y)

    lim_y = keys_to_pos(limit_mass, mass_keys, yes, 'gt')
    lim_rect = Rect(31, lim_y, img_rect.w, img_rect.h-lim_y+img_rect.y)
    lim_img = Surface(lim_rect.size)
    lim_img.set_alpha(150)

    lineas = WidgetGroup()
    linea_h = Linea(img_rect, img_rect.x, img_rect.centery, img_rect.w, 1, lineas)
    linea_v = Linea(img_rect, img_rect.centerx, img_rect.y, 1, img_rect.h, lineas)
    punto = Punto(img_rect, img_rect.centerx, img_rect.centery, lineas)

    move_x, move_y = True, True
    while not done:
        for e in event.get([KEYDOWN, KEYUP, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION]):
            if (e.type == KEYDOWN and e.key == K_ESCAPE) or e.type == QUIT:
                quit()
                exit()

            elif e.type == MOUSEMOTION:
                px, py = e.pos

                if move_y:
                    linea_h.move_y(py)
                    punto.move_y(py)
                if move_x:
                    linea_v.move_x(px)
                    punto.move_x(px)

                dx, dy = punto.rect.center
                valid = [rect_puffy.collidepoint(dx, dy),
                         rect_giant.collidepoint(dx, dy),
                         rect_super.collidepoint(dx, dy)]
                off_limit = lim_rect.collidepoint(dx, dy)

                if img_rect.collidepoint(px, py) and any(valid) and not off_limit:
                    invalid = False
                    mass = round(pos_to_keys(linea_h.rect.y+1, mass_keys, yes, 'gt'), 5)
                    radius = round(pos_to_keys(linea_v.rect.x, radius_keys, exes, 'gt'), 3)
                    clase = ''
                    if valid[0]:
                        clase = 'Puffy Giant'
                    elif valid[1]:
                        clase = 'Gas Giant'
                    elif valid[2]:
                        clase = 'Super Jupiter'
                    data.update({'mass': mass, 'radius': radius, 'clase': clase})

                    d = round(density(mass, radius), 5)
                    text_mass = 'Mass: {}'.format(mass)
                    text_radius = 'Radius: {}'.format(radius)
                    text_density = 'Density: {}'.format(d)

                else:
                    invalid = True
                    text_mass = 'Mass: N/A'
                    text_radius = 'Radius: N/A'
                    text_density = 'Density: N/A'

            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    done = True

            elif e.type == KEYDOWN and not invalid:
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

        render_mass = fuente2.render(text_mass, True, COLOR_TEXTO, COLOR_BOX)
        render_radius = fuente2.render(text_radius, True, COLOR_TEXTO, COLOR_BOX)
        render_density = fuente.render(text_density, True, COLOR_TEXTO, COLOR_BOX)

        fondo.fill(COLOR_BOX)
        fondo.blit(render_mass, (3, ALTO - 20))
        fondo.blit(render_radius, (150, ALTO - 20))
        fondo.blit(render_density, (300, ALTO - 20))

        fondo.blit(img, img_rect)
        fondo.blit(lim_img, lim_rect)
        numbers.draw(fondo)
        lineas.update()
        lineas.draw(fondo)
        display.update()

    display.quit()
    return data

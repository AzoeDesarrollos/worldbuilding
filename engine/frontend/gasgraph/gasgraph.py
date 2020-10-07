from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, ANCHO, ALTO
from pygame import KEYDOWN, QUIT, K_ESCAPE, MOUSEMOTION, K_SPACE, image
from pygame import init, quit, display, font, event, Rect
from engine.frontend.graph.graph import pos_to_keys
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

ruta = join(getcwd(), 'engine', 'frontend', 'gasgraph', 'gasgraph.png')
img_rect = Rect(31, 16, 540, 570)
img = image.load(ruta)


def gasgraph_loop():
    done = False
    data = {}
    text_mass = 'Mass: N/A'
    text_radius = 'Radius: N/A'
    text_density = 'Density: N/A'
    invalid = True

    fondo = display.set_mode((ANCHO, ALTO))
    fondo.fill(COLOR_BOX)

    for i in [i for i in range(len(radius_keys[:4]))]:
        key_img = radius_imgs[i]
        rect = key_img.get_rect(x=i * 28 + 30, y=3)
        exes.append(rect.centerx)
        fondo.blit(key_img, rect)

    for i in [i + 4 for i in range(len(radius_keys[4:14]))]:
        key_img = radius_imgs[i]
        rect = key_img.get_rect(x=i * 27 + 26, y=3)
        exes.append(rect.centerx)
        fondo.blit(key_img, rect)

    for i in [i + 14 for i in range(len(radius_keys[14:]))]:
        key_img = radius_imgs[i]
        rect = key_img.get_rect(x=i * 22 + 90, y=3)
        exes.append(rect.centerx)
        fondo.blit(key_img, rect)

    for i in [i for i in range(len(mass_keys))]:
        key_img = mass_imgs[i]
        rect = key_img.get_rect(right=30, centery=i * 20 + 20)
        yes.append(rect.centery - 16)
        fondo.blit(key_img, rect)

    x = exes[radius_keys.index(1.02)]
    y = yes[mass_keys.index(2)]

    rect_super = Rect(0, y, x - 3, img_rect.h)
    rect_puffy = Rect(x - 3, 0, img_rect.w, y)
    rect_giant = Rect(0, 0, x - 3, y)

    while not done:
        for e in event.get([KEYDOWN, QUIT, MOUSEMOTION]):
            if (e.type == KEYDOWN and e.key == K_ESCAPE) or e.type == QUIT:
                quit()
                exit()

            elif e.type == MOUSEMOTION:
                px, py = e.pos
                dx = px - 30
                dy = py - 14

                valid = [rect_puffy.collidepoint(dx, dy),
                         rect_giant.collidepoint(dx, dy),
                         rect_super.collidepoint(dx, dy)]

                if img_rect.collidepoint(px, py) and any(valid):
                    invalid = False
                    mass = round(pos_to_keys(dy, mass_keys, yes, 'gt'), 5)
                    radius = round(pos_to_keys(px, radius_keys, exes, 'gt'), 3)
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

            elif e.type == KEYDOWN and not invalid:
                if e.key == K_SPACE:
                    done = True

        render_mass = fuente2.render(text_mass, True, COLOR_TEXTO, COLOR_BOX)
        render_radius = fuente2.render(text_radius, True, COLOR_TEXTO, COLOR_BOX)
        render_density = fuente.render(text_density, True, COLOR_TEXTO, COLOR_BOX)

        fondo.fill(COLOR_BOX, (0, ANCHO, ALTO - 20, 50))
        fondo.blit(render_mass, (3, ALTO - 20))
        fondo.blit(render_radius, (150, ALTO - 20))
        fondo.blit(render_density, (300, ALTO - 20))

        fondo.blit(img, img_rect)
        display.update()

    display.quit()
    return data

from pygame import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN, KEYUP, SRCALPHA, K_ESCAPE, K_RETURN, K_LCTRL, K_LSHIFT, QUIT
from pygame import font, Surface, Rect, image, mouse, event, Color as Clr, mask
from pygame import display as pantalla, init as py_init, quit as py_quit
from pygame.sprite import LayeredUpdates
from os import getcwd, environ
# from bisect import bisect_left,bisect_right
import sys
import json

# noinspection PyUnresolvedReferences
if __name__ == '__main__':
    # noinspection PyUnresolvedReferences
    from objects import Linea, Punto

    if len(sys.argv) > 1:
        parameters = [(float(i)) for i in sys.argv[1:]]
    else:
        parameters = []
else:
    from .objects import Linea, Punto

    parameters = []


def abrir_json(archivo, encoding='utf-8'):
    with open(archivo, encoding=encoding) as file:
        return json.load(file)


def average(a, b):
    return (a + b) / 2


py_init()
mouse.set_visible(0)
fuente1 = font.SysFont('verdana', 16)
fuente2 = font.SysFont('verdana', 14)
# noinspection PyArgumentList
negro, blanco, rojo = Clr(0, 0, 0, 255), Clr(255, 255, 255, 255), Clr(255, 0, 0, 255)

environ['SDL_VIDEO_CENTERED'] = "{!s},{!s}".format(0, 0)
witdh, height = (590, 630)
frect = Rect(0, 0, witdh, height)

r = fuente2.render
texto1 = r('- Hold Shift to lock mass or Control to lock radius -', 1, negro, blanco)
rectT1 = texto1.get_rect(centerx=frect.centerx, centery=600)
texto2 = r("Mass and Radii values are relative to Earth's", 1, negro, blanco)
rectT2 = texto2.get_rect(centerx=frect.centerx, centery=620)

mass_keys = [(i + 1) / 10 for i in range(0, 9)]
mass_keys += [float(i) for i in range(1, 10)]
mass_keys += [float(i * 10) for i in range(1, 10)]
mass_keys += [float(i * 100) for i in range(1, 10)]
mass_keys += [float(i * 1000) for i in range(1, 5)]
mass_keys.sort()

radius_keys = [0.1] + [i / 10 for i in range(2, 10, 2)] + [float(i) for i in range(1, 12)]
if __name__ == '__main__':
    ruta = getcwd() + '/data/'
else:
    ruta = getcwd() + '/engine/frontend/data/'

graph = image.load(ruta + '/graph.png')
exes = [59, 93, 114, 128, 139, 148, 156, 162, 169, 173, 209, 229, 244, 254, 263, 271, 278, 284, 288, 325, 345, 360, 370,
        380, 387, 394, 400, 405, 440, 460, 475, 485, 495, 502, 509, 515, 520, 555, 575, 589]
yes = [478, 453, 431, 412, 395, 379, 279, 221, 179, 147, 121, 99, 79, 62, 47, 1]

_lineas = abrir_json(ruta + 'lineas.json')
composiciones = abrir_json(ruta + 'compositions.json')
# noinspection PyArgumentList
mascara = mask.from_threshold(image.load(ruta + 'mask.png'), (255, 0, 255), (250, 1, 250))


def pos_to_keys(delta, keys, puntos, comparison):
    if delta in puntos:
        idx = puntos.index(delta)
        return keys[idx]
    else:
        diffs = None
        up = 0
        down = 1
        if comparison == 'gt':
            diffs = [delta > j for j in puntos]
        elif comparison == 'lt':
            diffs = [delta < j for j in puntos]

        for i, b in enumerate(diffs):
            if b:
                down = i
            else:
                up = i
                break

        d = (puntos[down] - delta) / (puntos[down] - puntos[up])
        e = keys[up] - keys[down]
        return round(e * d + keys[down], 3)


def keys_to_pos(delta, keys, puntos, comparison):
    if delta in keys:
        idx = keys.index(delta)
        return puntos[idx]
    else:

        diffs = None
        up = 0
        down = 1
        if comparison == 'gt':
            diffs = [delta > j for j in keys]
        elif comparison == 'lt':
            diffs = [delta < j for j in keys]
        for i, b in enumerate(diffs):
            if b:
                down = i
            else:
                up = i
                break
        d = (keys[down] - delta) / (keys[down] - keys[up])
        e = puntos[up] - puntos[down]

        return round(e * d + puntos[down])


def graph_loop(lim_x_a=0.0, lim_x_b=0.0, lim_y_a=0.0, lim_y_b=0.0):
    if not __name__ == '__main__':
        fondo = pantalla.set_mode((witdh, height))
        font.init()
    else:
        fondo = pantalla.get_surface()

    rect = Rect(60, 2, 529, 476)
    lineas = LayeredUpdates()

    linea_h = Linea(rect.x, rect.centery, rect.w, 1, lineas)
    linea_v = Linea(rect.centerx, rect.y, 1, rect.h, lineas)
    punto = Punto(rect.centerx, rect.centery, lineas)

    data = {'composition': ''}

    if any([lim_x_a < 0, lim_x_b < 0, lim_y_a < 0, lim_y_b < 0]):
        raise ValueError()

    lim_mass_a = int(keys_to_pos(lim_x_a, mass_keys, exes, 'lt')) if lim_x_a else 0
    lim_mass_b = int(keys_to_pos(lim_x_b, mass_keys, exes, 'gt')) if lim_x_b else 0
    lim_radius_a = int(keys_to_pos(lim_y_a, radius_keys, yes, 'lt')) if lim_y_a else 0
    lim_radius_b = int(keys_to_pos(lim_y_b, radius_keys, yes, 'gt')) if lim_y_b else 0

    move_x, move_y = True, True
    lockx, locky = False, False

    mass_value = 0
    radius_value = 0

    mouse.set_pos(rect.center)
    event.clear()

    done = False
    px, py = 0, 0
    while not done:
        for e in event.get():
            if e.type == QUIT:
                py_quit()
                if __name__ == '__main__':
                    sys.exit()
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if (not lockx) or (not locky):
                        if (not lockx) and (not move_x):
                            lockx = True

                        if (not locky) and (not move_y):
                            locky = True

                elif e.button == 3:
                    if lockx:
                        lockx = False
                        move_x = not lockx

                    elif locky:
                        locky = False
                        move_y = not locky

            elif e.type == MOUSEMOTION:
                px, py = e.pos
                if move_y:
                    linea_h.move_y(py)
                    punto.move_y(py)

                if move_x:
                    linea_v.move_x(px)
                    punto.move_x(px)

                if rect.collidepoint(px, py) and (move_x or move_y):
                    if mascara.get_at((px, py)):
                        punto.select()
                        for name in _lineas:
                            if [px, py] in _lineas[name]:
                                data['composition'] = name
                                break
                    else:
                        punto.deselect()
                        data['composition'] = ''

            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    py_quit()
                    sys.exit()

                if e.key == K_LSHIFT:
                    move_x = False

                elif e.key == K_LCTRL:
                    move_y = False

                elif e.key == K_RETURN:
                    data['mass'] = round(mass_value, 2)
                    data['radius'] = round(radius_value, 2)
                    data['gravity'] = round(mass_value / (radius_value ** 2), 2)
                    data['density'] = round(mass_value / (radius_value ** 3), 2)
                    if rect.collidepoint(px, py) and mascara.get_at((px, py)):
                        for name in _lineas:
                            if [px, py] in _lineas[name]:
                                data['composition'] = composiciones[name]
                                break
                    done = True

            elif e.type == KEYUP:
                if e.key == K_LSHIFT:
                    if not lockx:
                        move_x = True

                elif e.key == K_LCTRL:
                    if not locky:
                        move_y = True

        px, py = mouse.get_pos()
        alto, bajo = 0, 0
        if not data.get('composition', False):
            for _y in reversed(range(0, py)):
                if mascara.get_at((px, _y)):
                    alto = _y
                    break
            for _y in range(py, 476):
                if mascara.get_at((px, _y)):
                    bajo = _y
                    break

            a, b = 0, 0
            # creo que esto se puede escribir con oneliners.
            for name in _lineas:
                if [px, alto] in _lineas[name]:
                    a = name
                    break
            for name in _lineas:
                if [px, bajo] in _lineas[name]:
                    b = name
                    break
            if a and b:
                # si el cursor está entre dos lineas, se computa el promedio de los valores de composición.
                silicates = average(composiciones[a]['silicates'], composiciones[b]['silicates'])
                hydrogen = average(composiciones[a]['hydrogen'], composiciones[b]['hydrogen'])
                helium = average(composiciones[a]['helium'], composiciones[b]['helium'])
                iron = average(composiciones[a]['iron'], composiciones[b]['iron'])
                water_ice = average(composiciones[a]['water ice'], composiciones[b]['water ice'])

                # sólo mostramos los valores mayores a 0%
                compo = []
                if silicates:
                    compo.append(str(round(silicates, 2)) + '% silicates')
                if hydrogen:
                    compo.append(str(round(hydrogen, 2)) + '% hydrogen')
                if helium:
                    compo.append(str(round(helium, 2)) + '% helium')
                if iron:
                    compo.append(str(round(iron, 2)) + '% iron')
                if water_ice:
                    compo.append(str(round(water_ice, 2)) + '% water ice')
                data['composition'] = ', '.join(compo)

                if hydrogen or helium:
                    data['planet'] = 'gaseous'
                else:
                    data['planet'] = 'terrestial'

        mass_value = pos_to_keys(linea_v.rect.x, mass_keys, exes, 'gt')
        radius_value = pos_to_keys(linea_h.rect.y, radius_keys, yes, 'lt')

        if any([lim_mass_b, lim_mass_a, lim_radius_a, lim_radius_b]):
            block = Surface(rect.size, SRCALPHA)
            limit = True
            alpha = 150
            if lim_mass_a:
                block.fill([0] * 3 + [alpha], (0, rect.y - 2, lim_mass_a - rect.x, rect.h))
            if lim_mass_b:
                block.fill([0] * 3 + [alpha], (lim_mass_b - rect.x, rect.y - 2, rect.w, rect.h))
            if lim_radius_a:
                block.fill([0] * 3 + [alpha], (0, lim_radius_a, rect.w, rect.h - lim_radius_a))
            if lim_radius_b:
                block.fill([0] * 3 + [alpha], (0, rect.y - 2, rect.w, lim_radius_b))

        else:
            block = None
            limit = False

        mass_text = 'Mass:' + str(round(mass_value, 3))
        radius_text = 'Radius:' + str(round(radius_value, 3))
        gravity_text = 'Density:' + str(round(mass_value / (radius_value ** 3), 2))
        density_text = 'Gravity:' + str(round(mass_value / (radius_value ** 2), 2))
        composition_text = 'Composition:' + data['composition']

        if pantalla.get_init():
            fondo.fill(blanco)
            fondo.blit(graph, (0, 0))
            mass_color = negro
            radius_color = negro
            if limit:
                fondo.blit(block, rect)
                if lim_x_a > mass_value or (0 < lim_x_b < mass_value):
                    mass_color = rojo

                if lim_y_a > radius_value or (0 < lim_y_b < radius_value):
                    radius_color = rojo

            fondo.blit(fuente1.render(mass_text, 1, mass_color), (rect.left, rect.bottom + 43))
            fondo.blit(fuente1.render(radius_text, 1, radius_color), (rect.left, rect.bottom + 22))
            fondo.blit(fuente1.render(density_text, 1, negro), (rect.left + 120, rect.bottom + 43))
            fondo.blit(fuente1.render(gravity_text, 1, negro), (rect.left + 120, rect.bottom + 22))
            if data['composition']:
                fondo.blit(fuente1.render(composition_text, 1, negro, blanco), (rect.left, rect.bottom + 64))

            fondo.blit(texto1, rectT1)
            fondo.blit(texto2, rectT2)
            lineas.update()
            lineas.draw(fondo)
            pantalla.update()

    py_quit()
    return data


if __name__ == '__main__':
    pantalla.set_mode((witdh, height))
    info = graph_loop(*parameters)
    print(info)

from pygame import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN, KEYUP, SRCALPHA, K_ESCAPE, K_SPACE, K_LCTRL, K_LSHIFT, QUIT
from pygame import font, Surface, Rect, image, mouse, event, Color as Clr, mask
from pygame import display, init as py_init, quit as py_quit, SCALED
from ..common import Linea, Punto, pos_to_keys, keys_to_pos
from engine.backend.util import abrir_json
from pygame.sprite import LayeredUpdates
from os import environ, getcwd, path
import sys

py_init()
fuente1 = font.SysFont('verdana', 15)
fuente2 = font.SysFont('verdana', 14)
negro, blanco, rojo = Clr(0, 0, 0, 255), Clr(255, 255, 255, 255), Clr(255, 0, 0, 255)

environ['SDL_VIDEO_CENTERED'] = "{!s},{!s}".format(0, 0)
witdh, height = (590, 630)
frect = Rect(0, 0, witdh, height)

r = fuente2.render
texto1 = r('- Hold Shift to lock mass or Control to lock radius -', True, negro, blanco)
rectT1 = texto1.get_rect(centerx=frect.centerx, centery=600)
texto2 = r("Mass and Radii values are relative to Earth's", True, negro, blanco)
rectT2 = texto2.get_rect(centerx=frect.centerx, centery=620)
texto3 = r('The cursor is beyond the parameters selected for this world type.', True, negro, blanco)
rectT3 = texto3.get_rect(centerx=frect.centerx, y=530)

mass_keys = [(i + 1) / 10 for i in range(0, 9)]
mass_keys += [float(i) for i in range(1, 10)]
mass_keys += [float(i * 10) for i in range(1, 10)]
mass_keys += [float(i * 100) for i in range(1, 10)]
mass_keys += [float(i * 1000) for i in range(1, 5)]
mass_keys.sort()

radius_keys = [0.1] + [i / 10 for i in range(2, 10, 2)] + [float(i) for i in range(1, 12)]
ruta = path.join(getcwd(), 'engine', 'frontend', 'graphs', 'graph', 'data')

graph = image.load(path.join(ruta, 'graph.png'))
exes = [59, 93, 114, 128, 139, 148, 156, 162, 169, 173, 209, 229, 244, 254, 263, 271, 278, 284, 288, 325, 345, 360, 370,
        380, 387, 394, 400, 405, 440, 460, 475, 485, 495, 502, 509, 515, 520, 555, 575, 589]
yes = [478, 453, 431, 412, 395, 379, 279, 221, 179, 147, 121, 99, 79, 62, 47, 1]

_lineas = abrir_json(path.join(ruta, 'lineas.json'))
composiciones = abrir_json(path.join(ruta, 'compositions.json'))
mascara = mask.from_threshold(image.load(path.join(ruta, 'mask.png')), (255, 0, 255), (250, 1, 250))


def average(a, b):
    return (a + b) / 2


def graph_loop(mass_lower_limit=0.0, mass_upper_limit=0.0, radius_lower_limit=0.0, radius_upper_limit=0.0):
    fondo = display.set_mode((witdh, height), SCALED)
    rect = Rect(60, 2, 529, 476)
    lineas = LayeredUpdates()

    linea_h = Linea(rect, rect.x, rect.centery, rect.w, 1, lineas)
    linea_v = Linea(rect,  rect.centerx, rect.y, 1, rect.h, lineas)
    punto = Punto(rect, rect.centerx, rect.centery, lineas)

    data = {}

    if any([mass_lower_limit < 0, mass_upper_limit < 0, radius_lower_limit < 0, radius_upper_limit < 0]):
        raise ValueError()

    lim_mass_a = int(keys_to_pos(mass_lower_limit, mass_keys, exes, 'lt')) if mass_lower_limit else 0
    lim_mass_b = int(keys_to_pos(mass_upper_limit, mass_keys, exes, 'gt')) if mass_upper_limit else 0
    lim_radius_a = int(keys_to_pos(radius_lower_limit, radius_keys, yes, 'lt')) if radius_lower_limit else 0
    lim_radius_b = int(keys_to_pos(radius_upper_limit, radius_keys, yes, 'gt')) if radius_upper_limit else 0

    move_x, move_y = True, True
    lockx, locky = False, False

    mass_value = 0
    radius_value = 0

    mass_color = negro
    radius_color = negro

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

                        elif (not locky) and (not move_y):
                            locky = True

                        elif not punto.disabled:
                            data['mass'] = round(mass_value, 3)
                            data['radius'] = round(radius_value, 3)
                            data['gravity'] = round(mass_value / (radius_value ** 2), 3)
                            data['density'] = round(mass_value / (radius_value ** 3), 3)
                            if rect.collidepoint(px, py) and mascara.get_at((px, py)):
                                for name in _lineas:
                                    if [px, py] in _lineas[name]:
                                        data['composition'] = composiciones[name]
                                        break
                            done = True
                        else:
                            data = {}
                            done = True

                elif e.button == 3:
                    if lockx:
                        lockx = False
                        move_x = not lockx

                    if locky:
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

                point_x, point_y = punto.rect.center
                if rect.collidepoint(point_x, point_y) and (move_x or move_y):
                    if mascara.get_at((point_x, point_y)):
                        punto.select()
                        for name in _lineas:
                            if [point_x, point_y] in _lineas[name]:
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

                elif e.key == K_SPACE:
                    data['mass'] = round(mass_value, 3)
                    data['radius'] = round(radius_value, 3)
                    data['gravity'] = round(mass_value / (radius_value ** 2), 3)
                    data['density'] = round(mass_value / (radius_value ** 3), 3)
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

        px, py = punto.rect.center
        alto, bajo = 0, 0
        if not data.get('composition', False):
            if rect.collidepoint((px, py)):
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
                        data['clase'] = 'Gas Dwarf'
                    else:
                        data['clase'] = 'Terrestial Planet'

        mass_value = pos_to_keys(linea_v.rect.x, mass_keys, exes, 'gt')
        radius_value = pos_to_keys(linea_h.rect.y, radius_keys, yes, 'lt')

        block = Surface(rect.size, SRCALPHA)
        block_mask = mask.from_surface(block)
        if any([lim_mass_b, lim_mass_a, lim_radius_a, lim_radius_b]):
            block_rect = block.get_rect(topleft=rect.topleft)
            alpha = 150
            if lim_mass_a:
                block.fill([0] * 3 + [alpha], (0, rect.y - 2, lim_mass_a - rect.x, rect.h))
            if lim_mass_b:
                block.fill([0] * 3 + [alpha], (lim_mass_b - rect.x, rect.y - 2, rect.w, rect.h))
            if lim_radius_a:
                block.fill([0] * 3 + [alpha], (0, lim_radius_a, rect.w, rect.h - lim_radius_a))
            if lim_radius_b:
                block.fill([0] * 3 + [alpha], (0, rect.y - 2, rect.w, lim_radius_b))

            block_mask = mask.from_surface(block)
            point_x, point_y = punto.rect.center
            if block_rect.collidepoint((point_x, point_y)):
                if block_mask.get_at((point_x - rect.x, point_y - rect.y)):
                    punto.disable()
                    radius_color = rojo
                    mass_color = rojo
                else:
                    punto.enable()
                    mass_color = negro
                    radius_color = negro

        mass_text = 'Mass:' + str(round(mass_value, 3))
        radius_text = 'Radius:' + str(round(radius_value, 3))
        gravity_text = 'Density:' + str(round(mass_value / (radius_value ** 3), 3))
        density_text = 'Gravity:' + str(round(mass_value / (radius_value ** 2), 3))

        if not done:
            fondo.fill(blanco)
            fondo.blit(graph, (0, 0))
            if block_mask.count() != 0:
                fondo.blit(block, rect)

            if punto.disabled:
                fondo.blit(texto3, rectT3)
            else:
                fondo.blit(fuente1.render(mass_text, True, mass_color), (5, rect.bottom + 43))
                fondo.blit(fuente1.render(radius_text, True, radius_color), (140, rect.bottom + 43))
                fondo.blit(fuente1.render(density_text, True, negro), (130 * 2 - 5, rect.bottom + 43))
                fondo.blit(fuente1.render(gravity_text, True, negro), (140 * 3, rect.bottom + 43))
                if data.get('composition', False):
                    composition_text = 'Composition:' + data['composition']
                    fondo.blit(fuente1.render(composition_text, True, negro, blanco), (5, rect.bottom + 64))

            fondo.blit(texto1, rectT1)
            fondo.blit(texto2, rectT2)
            punto.update()
            lineas.update()
            lineas.draw(fondo)
            display.update()

    display.quit()
    return data

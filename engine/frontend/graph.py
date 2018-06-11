from pygame import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN, KEYUP, SRCALPHA, K_ESCAPE, K_RETURN, K_LCTRL, K_LSHIFT, QUIT
from pygame import font, Surface, Rect, PixelArray, image, mouse, event, draw, Color as Clr
from pygame import display as pantalla, init as py_init, quit as py_quit
from pygame.sprite import Sprite, LayeredUpdates
from os import getcwd, environ
import sys

py_init()
mouse.set_visible(0)
fuente1 = font.SysFont('verdana', 16)
fuente2 = font.SysFont('verdana', 14)
# noinspection PyArgumentList
negro, blanco, cian, rojo = Clr(0, 0, 0, 255), Clr(255, 255, 255, 255), Clr(0, 125, 255, 255), Clr(255, 0, 0, 255)

environ['SDL_VIDEO_CENTERED'] = "{!s},{!s}".format(0, 0)
witdh, height = (601, 590)
frect = Rect(0, 0, witdh, height)

r = fuente2.render
texto1 = r('- Hold Shift to lock mass or Control to lock radius -', 1, negro, blanco)
rectT1 = texto1.get_rect(centerx=frect.centerx, centery=580)
texto2 = r("Mass and Radii values are relative to Earth's", 1, negro, blanco)
rectT2 = texto2.get_rect(centerx=frect.centerx, centery=560)

mass_keys = [(i + 1) / 10 for i in range(0, 9)]
mass_keys += [float(i) for i in range(1, 10)]
mass_keys += [float(i * 10) for i in range(1, 10)]
mass_keys += [float(i * 100) for i in range(1, 10)]
mass_keys += [float(i * 1000) for i in range(1, 5)]
mass_keys.sort()

radius_keys = [0.1] + [i / 10 for i in range(2, 10, 2)] + [float(i) for i in range(1, 12)]
if __name__ == '__main__':
    ruta = getcwd() + '/frontend'
else:
    ruta = getcwd() + '/engine/frontend/'

graph = image.load(ruta + 'graph.png')
px_array = PixelArray(graph.copy())

yes = []
for i in reversed(range(0, 479)):
    color = graph.unmap_rgb(px_array[63, i])
    if color == negro:
        yes.append(i)

exes = []
for i in range(59, 590):
    color = graph.unmap_rgb(px_array[i, 475])
    if color == negro:
        exes.append(i)

graph = px_array.make_surface()
compositions = {
    (255, 100, 63, 255): '100% hydrogen',
    (255, 200, 63, 255): '75% hydrogen, 25% helium',
    (255, 54, 214, 255): '100% water ice',
    (159, 116, 0, 255): '75% water ice, 22% silicates, 3% iron core',
    (64, 128, 0, 255): '48% water ice, 48.5 silicates, 6.5% iron core',
    (64, 128, 255, 255): '25% water ice, 52.5% silicates, 22.5 iron core',
    (0, 0, 255, 255): '100% silicates',
    (0, 191, 255, 255): '32.5% silicate mantle, 67.5% iron core',
    (230, 191, 255, 255): '70% iron core, 30% silicate mantle',
    (0, 201, 0, 255): '100% iron core'
}


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


class Linea(Sprite):
    def __init__(self, x, y, w, h, grupo):
        super().__init__(grupo)
        self.image = Surface((w, h))
        self.image.fill(cian)

        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = Rect(x, y, w, h)

    def move_x(self, x):
        if 59 < x < 589:
            self.rect.centerx = x

    def move_y(self, y):
        if 2 < y < 480:
            self.rect.centery = y


class Punto(Sprite):
    def __init__(self, x, y, grupo):
        super().__init__(grupo)
        self.image_des = Surface((10, 10), SRCALPHA)
        self.image_sel = Surface((10, 10), SRCALPHA)
        draw.circle(self.image_des, cian, [5, 5], 5)

        draw.circle(self.image_sel, rojo, [5, 5], 5)

        self.image = self.image_des
        self.rect = self.image.get_rect(center=[x, y])

    def select(self):
        self.image = self.image_sel

    def deselect(self):
        self.image = self.image_des

    def move_x(self, x):
        if 59 < x < 589:
            self.rect.centerx = x

    def move_y(self, y):
        if 2 < y < 480:
            self.rect.centery = y


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

    data = {}
    lim_mass_a, lim_mass_b = 0, 0
    lim_radius_a, lim_radius_b = 0, 0

    if any([lim_x_a < 0, lim_x_b < 0, lim_y_a < 0, lim_y_b < 0]):
        raise ValueError()

    if lim_x_a:
        lim_mass_a = int(keys_to_pos(lim_x_a, mass_keys, exes, 'lt'))
    if lim_x_b:
        lim_mass_b = int(keys_to_pos(lim_x_b, mass_keys, exes, 'gt'))
    if lim_y_a:
        lim_radius_a = int(keys_to_pos(lim_y_a, radius_keys, yes, 'gt'))
    if lim_y_b:
        lim_radius_b = int(keys_to_pos(lim_y_b, radius_keys, yes, 'gt'))

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
                # sys.exit()
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

                if rect.collidepoint(px, py):
                    rgba = tuple(fondo.unmap_rgb(px_array[px, py]))
                    if rgba in compositions:
                        punto.select()
                    else:
                        punto.deselect()

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
                    if rect.collidepoint(px, py):
                        rgba = tuple(fondo.unmap_rgb(px_array[px, py]))
                        if rgba in compositions:
                            data['composition'] = compositions[rgba]
                    done = True

            elif e.type == KEYUP:
                if e.key == K_LSHIFT:
                    if not lockx:
                        move_x = True

                elif e.key == K_LCTRL:
                    if not locky:
                        move_y = True

        mass_value = pos_to_keys(linea_v.rect.x, mass_keys, exes, 'gt')
        radius_value = pos_to_keys(linea_h.rect.y, radius_keys, yes, 'lt')

        if any([lim_mass_b, lim_mass_a, lim_radius_a, lim_radius_b]):
            block = Surface(rect.size, SRCALPHA)
            limit = True

            if lim_mass_a:
                block.fill([125] * 4, (0, rect.y - 2, lim_mass_a - rect.x, rect.h))
            if lim_mass_b:
                block.fill([125] * 4, (lim_mass_b - rect.x, rect.y - 2, rect.w, rect.h))
            if lim_radius_a:
                block.fill([125] * 4, (0, lim_radius_a, rect.w, rect.h - lim_radius_a))
            if lim_radius_b:
                block.fill([125] * 4, (0, rect.y - 2, rect.w, lim_radius_b))

        else:
            block = None
            limit = False

        mass_text = 'Mass:' + str(round(mass_value, 3))
        radius_text = 'Radius:' + str(round(radius_value, 3))
        gravity_text = 'Gravity:' + str(round(mass_value / (radius_value ** 3), 2))
        density_text = 'Density:' + str(round(mass_value / (radius_value ** 2), 2))

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

            fondo.blit(texto1, rectT1)
            fondo.blit(texto2, rectT2)
            lineas.update()
            lineas.draw(fondo)
            pantalla.update()

    py_quit()
    return data


if __name__ == '__main__':
    pantalla.set_mode((witdh, height))
    info = graph_loop()
    print(info)

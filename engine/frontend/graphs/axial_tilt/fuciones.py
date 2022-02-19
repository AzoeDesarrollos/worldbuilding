from engine.frontend.globales import COLOR_SELECTED, COLOR_BOX, COLOR_AREA, render_textrect
from pygame import Rect, Surface, font, draw, MOUSEMOTION, mouse
from engine.backend.util import decimal_round
from math import cos, sin, radians, pi
from bisect import bisect_right
from .constantes import *


def set_xy(rect, angle: int):
    x = round(rect.centerx + rect.w // 2 * sin(radians(angle + 90)))
    y = round(rect.centery + rect.h // 2 * cos(radians(angle + 90)))
    return x, y


def variacion_estacional(x, axial_tilt):
    # temp_latitud = (-8 / 9) * latitud + temp_promedio + 35
    contant = 3 + (4 / 423) + (3.3 * (10 ** -8))
    constante_de_variacion_estacional = (contant * axial_tilt) / 5

    # y es la  fución de temperatura según el momento del año
    # x es el momento de año (2pi es el fin del año)
    return constante_de_variacion_estacional * cos(x)


def graph_seasonal_var(panel, tilt):
    graph_rect = Rect(20, 0, 130, 130)
    graph_surf = Surface(graph_rect.size)
    f = font.SysFont('Verdana', 14)
    f_render = f.render('Seasonal Variation', True, COLOR_SELECTED)
    f_rect = f_render.get_rect(top=graph_rect.bottom, centerx=graph_rect.centerx)

    graph_surf.fill(COLOR_BOX)
    puntos = []
    x = 0
    while x <= 4 * pi:
        x += 0.01
        y = variacion_estacional(x, tilt if tilt <= 90 else 90 - (tilt - 90))
        puntos.append([round(x, 3) * 10, round(y, 3) + graph_rect.centery])

    draw.aaline(graph_surf, gris, (0, graph_rect.centery), (graph_rect.w, graph_rect.centery))
    for x in [0, pi, 2 * pi, 3 * pi]:
        x = round(x, 3) * 10
        draw.aaline(graph_surf, gris, [x, 0], [x, graph_rect.h])

    draw.aalines(graph_surf, blanco, False, points=puntos)
    draw.rect(graph_surf, gris, graph_surf.get_rect(), 2)

    poss = [0, graph_rect.h//3, graph_rect.h]
    colors = [rojo, verde, azul]
    rect = Rect(graph_rect.right+2, 0, 6, 1)
    for y in range(graph_rect.h):
        if y in poss:
            color = colors[y]
        else:
            color = Color(color_and_cap(poss, colors, y))
            colors.insert(y, color)

        if y not in poss:
            poss.append(y)
        poss.sort()
        panel.fill(color, rect)
        rect.y = y

    panel.blit(f_render, f_rect)
    panel.blit(graph_surf, graph_rect)
    return graph_rect


def set_latitude(events, panel, x, y, latitude):
    f = font.SysFont('Verdana', 14)
    text = f.render('Set Latitude', True, COLOR_SELECTED)
    text_rect = text.get_rect(left=x, top=y + text.get_height())

    area_rect = Rect(text_rect.left, text_rect.bottom + 3, 91, 10)
    area_img = Surface(area_rect.size)
    area_img.fill(COLOR_AREA)

    number_rect = Rect(0, 0, 30, 30)
    number_rect.midleft = text_rect.right + 15, area_rect.top

    panel.blit(area_img, area_rect)
    panel.blit(text, text_rect)

    for event in events:
        if event.type == MOUSEMOTION:
            px, py = event.pos
            if area_rect.collidepoint(px, 170 + py - (y + text_rect.bottom + 3)):
                mouse.set_pos(px, area_rect.centery + 330)
                latitude = event.pos[0] - 20

    if latitude is not None:
        panel.fill(COLOR_BOX, number_rect)
        render_lat = f.render(str(latitude) + "°", True, COLOR_SELECTED)
        render_rect = render_lat.get_rect(center=number_rect.center)
        panel.blit(render_lat, render_rect)

    return latitude


def print_info(panel, planet, x, y, w):
    f = font.SysFont('Verdana', 15)
    if planet.tilt == 'Not set':
        text = f"The planet {str(planet)}'s axial tilt has not been set yet."
    else:
        text = f'The planet {str(planet)} has an axial tilt of {planet.tilt.m}°'

    render = render_textrect(text, f, w, COLOR_SELECTED, COLOR_BOX)
    render_rect = render.get_rect(center=(x, y))
    panel.blit(render, render_rect)


def color_and_cap(grupo_a, grupo_b, t):
    if t in grupo_a:
        return grupo_b[t]

    elif t < grupo_a[0]:
        # "extrapolación" lineal positiva
        despues = 1
        antes = 0
    elif t > grupo_a[-1]:
        # "extrapolación" lineal nagativa
        despues = -1
        antes = -2
    else:
        # interpolación lineal
        despues = bisect_right(grupo_a, t)
        antes = despues - 1

    x1 = grupo_a[antes]
    x2 = grupo_a[despues]

    y1 = grupo_b[antes]
    y2 = grupo_b[despues]

    diff_x = x2 - x1
    ar = (y2.r - y1.r) / diff_x
    ag = (y2.g - y1.g) / diff_x
    ab = (y2.b - y1.b) / diff_x

    br = y1.r - ar * x1
    bg = y1.g - ag * x1
    bb = y1.b - ab * x1

    x = t - x1 if t > x1 else x1 - t

    def cap(number):
        if number >= 255:
            return 255
        elif number < 0:
            v = abs(number)
            return cap(v)
        else:
            return number

    r = cap(decimal_round(ar * x + br))
    g = cap(decimal_round(ag * x + bg))
    b = cap(decimal_round(ab * x + bb))

    return r, g, b

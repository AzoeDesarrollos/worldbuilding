from engine.frontend.globales import COLOR_SELECTED, COLOR_BOX, COLOR_AREA, render_textrect
from pygame import Rect, Surface, font, draw, MOUSEMOTION, mouse
from math import cos, sin, radians, pi
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

    rect = Rect(graph_rect.right+2, 0, 6, 1)
    for y in range(0, graph_rect.h):
        r = red_gradient(y)
        b = blue_gradient(y)
        color = Color(r, 0, b)
        panel.fill(color, rect)
        rect.y = y+1

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
        text = f"The planet {str(planet)}'s axial tilt has not been set yet.\n\n"
        text += "Set the axial tilt using the Up and Down keys. Hold Ctrl to increase precision."
    else:
        text = f'The planet {str(planet)} has an axial tilt of {planet.tilt.m}°.'

    render = render_textrect(text, f, w, COLOR_SELECTED, COLOR_BOX)
    render_rect = render.get_rect(topleft=(x, y))
    panel.blit(render, render_rect)


def red_gradient(x):
    a = -1.961538462
    return round(a * x + 255)


def blue_gradient(x):
    a = 1.961538462
    return round(a * x)

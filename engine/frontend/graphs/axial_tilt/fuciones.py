from pygame import draw, Surface, SRCALPHA
from math import cos, sin, pi, radians
from .constantes import *


def axial_precession(year):
    a1 = 19.87  # minimum axial tilt value
    a2 = 20.21  # maximum axial tilt value
    m = 34000  # period of the precession

    # from: https://www.youtube.com/watch?v=a5aAIbTs_Gw
    b = (a1 + a2) / 2
    a = a2 - b
    y = a * cos((2 * pi / m) * year - pi) + b
    return y


def interpolate(x, h):
    p = [[0, h // 2], [90, h]]

    x1 = p[0][0]
    x2 = p[1][0]

    y1 = p[0][1]
    y2 = p[1][1]

    diff_x = x2 - x1
    a = (y2 - y1) / diff_x
    b = y1 - a * x1

    y = round(a * x + b)
    return y


def lines(tilt):
    frame = Surface((1200, 601), SRCALPHA)
    if tilt > 90:
        tilt -= 180
    rect = frame.get_rect()
    equator = rect.centery
    draw.line(frame, verde, [0, equator], [rect.w, equator])

    south_tropic = interpolate(tilt, rect.h)
    draw.line(frame, rojo, [0, south_tropic], [rect.w, south_tropic])

    north_tropic = rect.h - south_tropic
    draw.line(frame, rojo, [0, north_tropic], [rect.w, north_tropic])

    south_polar = interpolate(90 - tilt, rect.h)
    draw.line(frame, azul, [0, south_polar], [rect.w, south_polar])

    north_polar = rect.h - south_polar
    draw.line(frame, azul, [0, north_polar], [rect.w, north_polar])

    return frame


def set_xy(rect, angle: int):
    x = round(rect.centerx + rect.w // 2 * cos(radians(angle)))
    y = round(rect.centery + rect.w // 2 * sin(radians(angle)))
    return x, y

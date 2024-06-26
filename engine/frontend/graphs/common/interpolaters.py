from bisect import bisect_right
from engine.backend.util import interpolate
from math import pi


def find_points(x: int, group_x: list, group_y: list):
    if x < 0 or x < group_x[0]:
        despues = 1
        antes = 0
    elif x >= group_x[-1]:
        despues = -1
        antes = -2
    else:
        despues = bisect_right(group_x, x)
        antes = despues - 1

    x1 = group_x[antes]
    x2 = group_x[despues]

    y1 = group_y[antes]
    y2 = group_y[despues]

    return x1, x2, y1, y2


def find_and_interpolate(x, group_x, group_y):
    x1, x2, y1, y2 = find_points(x, group_x, group_y)
    return interpolate(x, x1, x2, y1, y2)


def find_and_interpolate_flipped(x: int, group_x: list, group_y: list):
    a = group_x.copy()
    b = group_y.copy()

    a.sort(reverse=False)
    b.sort(reverse=True)

    return find_and_interpolate(x, a, b)


def density(m, r):
    return m / ((4 / 3) * pi * pow(r, 3))

import math


def f_circumference(r):
    return 2 * math.pi * r


def f_surface_area(r):
    return 4 * math.pi * (r ** 2)


def f_volume(r):
    return (4 / 3) * math.pi * (r ** 3)


def f_density(r, m):
    return m / (4 / 3) * math.pi * (r ** 3)

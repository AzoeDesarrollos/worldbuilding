from math import cos, sin, radians


def set_xy(rect, angle: int):
    x = round(rect.centerx + rect.w // 2 * sin(radians(angle + 90)))
    y = round(rect.centery + rect.h // 2 * cos(radians(angle + 90)))
    return x, y


def variacion_estacional(x, latitud, temp_promedio, axial_tilt):
    # TPL es la temperatura del planeta por latitud
    temp_promedio_planeta = (-8 / 9) * latitud + temp_promedio + 35
    # Ve es la variación estacional
    # Op es el axial tilt
    contant = 3 + (4 / 423) + (3.3 * (10 ** -8))
    constante_de_variacion_estacional = (contant * axial_tilt) / 5

    # y es la  fución de temperatura según el momento del año
    # x es el momento de año (2pi es el fin del año)
    return constante_de_variacion_estacional * cos(x) + temp_promedio_planeta

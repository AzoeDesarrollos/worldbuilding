from pygame import image, PixelArray
from ..common import pos_to_keys
from bisect import bisect_left
from os import getcwd, path
from engine import q

ruta = path.join(getcwd(), 'engine', 'frontend', 'graphs', 'atmograph', 'atmograph04rev24.png')
graph = image.load(ruta)

pos_psi = [12, 20, 27, 36, 46, 59, 74, 93, 120, 166, 174, 181, 190, 200, 213, 228, 247, 274]
nums_psi = sorted([i for i in range(1, 11)] + [i for i in range(20, 101, 10)], reverse=True)


def interpolacion_lineal(vol):
    pos_o2 = [47, 81, 114, 147, 179, 213, 246, 279, 311, 345, 378]
    pos_o2.sort(reverse=True)
    nums_o2 = [i for i in range(0, 101, 10)]
    antes = 11 - bisect_left(nums_o2, vol)
    despues = antes + 1

    x1 = nums_o2[antes]
    x2 = nums_o2[despues]

    y1 = pos_o2[antes]
    y2 = pos_o2[despues]

    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1

    return int(a * vol + b)


def atmo(vol, rect):
    y = interpolacion_lineal(vol)
    pxarray = PixelArray(graph)
    p, d = 0, 0
    for j in range(0, rect.bottom - 80):
        # noinspection PyUnresolvedReferences
        rgba = graph.unmap_rgb(pxarray[y, j])
        if rgba == (0, 217, 184, 255):
            if p == 0:
                p = j
                d = j
            else:
                p += 1
        elif p != 0:
            break

    del pxarray
    return d, p


def convert(selected_pressure):
    return q(pos_to_keys(selected_pressure, nums_psi, pos_psi, 'gt'), 'psi')

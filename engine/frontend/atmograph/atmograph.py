from pygame import image, display, PixelArray, event, draw, Surface, SRCALPHA, key
from pygame import KEYDOWN, K_ESCAPE, K_DOWN, K_UP, K_SPACE
from engine.frontend.graph.graph import pos_to_keys
from bisect import bisect_right
from engine import q
from os import getcwd, path

ruta = path.join(getcwd(), 'engine', 'frontend', 'atmograph', 'atmograph04rev.png')
graph = image.load(ruta)


def interpolacion_lineal(vol):
    pos_o2 = [47, 81, 114, 147, 179, 213, 246, 279, 311, 345, 378]
    nums_o2 = [i for i in range(0, 101, 10)]
    despues = bisect_right(nums_o2, vol)
    antes = despues - 1

    x1 = nums_o2[antes]
    x2 = nums_o2[despues]

    y1 = pos_o2[antes]
    y2 = pos_o2[despues]

    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1

    return int(a * vol + b)


def atmo(vol, rect):
    rea = (95, 231, 210, 255)
    reb = (0, 216, 184, 255)
    y = interpolacion_lineal(vol)
    pxarray = PixelArray(graph)
    p, d = 0, 0
    for j in range(0, rect.bottom - 80):
        rgba = graph.unmap_rgb(pxarray[y, j])
        if rgba == rea or rgba == reb:
            if p == 0:
                p = j
                d = j
            else:
                p += 1
        elif p != 0:
            break

    del pxarray
    return d, p


def atmograph(vol_o2, rect):
    pos_psi = [12, 20, 27, 36, 46, 59, 74, 93, 120, 166, 174, 181, 190, 200, 213, 228, 247, 274]
    nums_psi = sorted([i for i in range(1, 11)] + [i for i in range(20, 101, 10)], reverse=True)

    key.set_repeat(60, 30)
    max_pressure, min_pressure = atmo(vol_o2, rect)  # valores máximos y minimos de presión atmosférica
    selected_pressure = (max_pressure + min_pressure) // 2  # valor de presión a nivel del mar seleccionado
    pressure_at_sea_level = 0
    canvas = Surface(graph.get_size(), SRCALPHA)
    done = False
    while not done:
        delta_y = 0
        for e in event.get(KEYDOWN):
            if e.type == KEYDOWN:
                canvas.fill((0, 0, 0, 0))
                if e.key == K_ESCAPE:
                    quit()
                    exit()
                elif e.key == K_UP:
                    if max_pressure < (selected_pressure - 1) < min_pressure:
                        delta_y = -1
                elif e.key == K_DOWN:
                    if max_pressure < (selected_pressure + 1) < min_pressure:
                        delta_y = +1
                elif e.key == K_SPACE:
                    pressure_at_sea_level = q(pos_to_keys(selected_pressure, nums_psi, pos_psi, 'gt'), 'psi')
                    done = True

        fondo = display.get_surface()
        fondo.blit(graph, rect)
        fondo.blit(canvas, rect)
        oxigen_marker = interpolacion_lineal(vol_o2)
        if delta_y:
            selected_pressure += delta_y
        draw.line(canvas, (255, 0, 0, 255), (oxigen_marker, rect.top), (oxigen_marker, rect.bottom))
        draw.line(canvas, (0, 255, 0, 255), (0, selected_pressure), (rect.right, selected_pressure))
        draw.line(canvas, (0, 0, 0, 255), (0, max_pressure), (rect.right, max_pressure))
        draw.line(canvas, (0, 0, 0, 255), (0, min_pressure), (rect.right, min_pressure))

        display.flip()

    return pressure_at_sea_level

from pygame import KEYDOWN, K_UP, K_DOWN, KMOD_CTRL, QUIT, K_ESCAPE, K_SPACE, K_RETURN, KEYUP
from pygame import draw, font, display, event, quit, init, Surface, time, Rect
from engine.frontend.globales import ANCHO, ALTO
from .fuciones import set_xy, variacion_estacional
from .constantes import *
from sys import exit
from math import pi

init()
fps = time.Clock()
display.set_caption('Worldbuilding')


def hemiphere_note(angle: int, north=True):
    real = angle
    hemisphere = ''

    if 0 < angle <= 90:
        real = angle
        if north:
            hemisphere = 'N'
        else:
            hemisphere = 'S'
    elif 90 < angle < 180:
        real = 90 + (90 - angle)
        if north:
            hemisphere = 'S'
        else:
            hemisphere = 'N'

    return real, hemisphere


def interactive_loop(tilt):
    screen = display.get_surface()
    rect = screen.get_rect(y=-160)
    frame = Surface((rect.w, rect.h - 320))
    f2 = font.SysFont('Verdana', 12)

    frame.fill(blanco)
    drawn = False
    for i in range(100, rect.w - 50, 14):  # orbital plane
        if not drawn:
            draw.line(frame, negro, [i, rect.centery], [i + 14, rect.centery], width=2)
            drawn = True
        else:
            drawn = False

    draw.circle(frame, amarillo, [100, rect.centery], 50)  # "here's a star"
    planet = draw.circle(frame, negro, [400, rect.centery], 100, width=1)  # "and a planet"

    drawn = False
    for i in range(planet.top - 50, planet.bottom + 50, 14):  # orbital plane
        if not drawn:
            draw.line(frame, negro, [planet.centerx, i], [planet.centerx, i + 14], width=1)
            drawn = True
        else:
            drawn = False

    axial_tilt = [tilt - 90, tilt + 90]
    x1, y1 = set_xy(planet.inflate(75, 75), tilt - 90)
    x2, y2 = set_xy(planet.inflate(75, 75), tilt + 90)
    draw.line(frame, negro, [x1, y1], [x2, y2], width=1)  # axial tilt line

    equator = [tilt, tilt + 180]
    x1, y1 = set_xy(planet, equator[0])
    x2, y2 = set_xy(planet, equator[1])
    draw.line(frame, 'red', [x1, y1], [x2, y2], width=1)  # equator

    north_tropic = equator.copy()
    north_tropic[0] += tilt
    north_tropic[1] = 180
    x1, y1 = set_xy(planet, north_tropic[0])
    x2, y2 = set_xy(planet, north_tropic[1])
    draw.line(frame, 'orange', [x1, y1], [x2, y2], width=1)  # tropic
    tropic_north, hemisphere = hemiphere_note(tilt)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    frame.blit(render, [x1, y1])

    south_tropic = equator.copy()
    south_tropic[0] = 0
    south_tropic[1] += tilt
    x1, y1 = set_xy(planet, south_tropic[0])
    x2, y2 = set_xy(planet, south_tropic[1])
    draw.line(frame, 'orange', [x1, y1], [x2, y2], width=1)  # tropic
    tropic_north, hemisphere = hemiphere_note(tilt, north=False)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    frame.blit(render, [x2, y2])

    north_polar_circle = equator.copy()
    north_polar_circle[0] = axial_tilt[1] - tilt
    north_polar_circle[1] = axial_tilt[1] + tilt
    x1, y1 = set_xy(planet, north_polar_circle[0])
    x2, y2 = set_xy(planet, north_polar_circle[1])
    draw.line(frame, 'cyan', [x1, y1], [x2, y2], width=1)  # polar circle
    tropic_north, hemisphere = hemiphere_note(abs(90 - tilt), north=True)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    frame.blit(render, [x1, y1])

    south_polar_circle = equator.copy()
    south_polar_circle[0] = axial_tilt[0] - tilt
    south_polar_circle[1] = axial_tilt[0] + tilt
    x1, y1 = set_xy(planet, south_polar_circle[0])
    x2, y2 = set_xy(planet, south_polar_circle[1])
    draw.line(frame, 'cyan', [x1, y1], [x2, y2], width=1)  # polar circle
    tropic_north, hemisphere = hemiphere_note(abs(90 - tilt), north=False)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    frame.blit(render, [x1, y1])

    screen.blit(frame, (0, 0))

    return tilt


def axial_loop():
    screen = display.set_mode((ANCHO, ALTO))
    panel = Surface((ANCHO, 300))
    panel_rect = panel.get_rect(y=310)

    done = False
    delta = 0
    tilt = 0
    graph_rect = Rect(0, 0, 130, 120)
    graph_surf = Surface(graph_rect.size)

    while not done:
        fps.tick(60)
        events = event.get([KEYDOWN, QUIT, KEYUP])

        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                quit()
                exit()

            elif e.type == KEYDOWN:
                if e.key == K_UP:
                    if e.mod & KMOD_CTRL:
                        delta = -0.1
                    else:
                        delta = -1
                elif e.key == K_DOWN:
                    if e.mod & KMOD_CTRL:
                        delta = +0.1
                    else:
                        delta = +1
                elif e.key == K_RETURN or e.key == K_SPACE:
                    done = True

            elif e.type == KEYUP:
                delta = 0

        if tilt + delta < 0:
            tilt = 180
        elif tilt + delta > 180:
            tilt = 0

        tilt += delta

        interactive_loop(tilt)

        graph_surf.fill(negro)
        puntos = []
        x = 0
        while x <= 4 * pi:
            x += 0.01
            y = variacion_estacional(x, 45, 15, tilt if tilt <= 90 else 90 - (tilt - 90))
            puntos.append([round(x, 3) * 10, round(y, 3)+50])

        panel.fill('green')

        draw.aalines(graph_surf, 'white', False, points=puntos)
        draw.aaline(graph_surf,'white',(0,graph_rect.centery),(graph_rect.w,graph_rect.centery))

        panel.blit(graph_surf, graph_rect)
        screen.blit(panel, panel_rect)
        display.update()
    return tilt


__all__ = [
    'axial_loop'
]

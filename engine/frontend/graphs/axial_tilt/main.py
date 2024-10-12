from pygame import KEYDOWN, K_UP, K_DOWN, QUIT, K_ESCAPE, K_SPACE, K_RETURN, KEYUP, K_LCTRL, K_RCTRL
from pygame import draw, font, display, event, quit, init, Surface, time
from .fuciones import set_xy, graph_seasonal_var, print_info
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX
from pygame import MOUSEBUTTONDOWN, MOUSEMOTION
from engine.backend import q
from .constantes import *
from sys import exit

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

    frame.fill(COLOR_BOX)

    planet = draw.circle(frame, negro, [400, rect.centery], 100, width=1)  # "and a planet"
    inflated_planet = planet.inflate(75, 75)
    margin_ext = planet.inflate(30, 30)
    draw.circle(frame, negro, [400, rect.centery], 95)
    draw.circle(frame, dark_green, [400, rect.centery], 99, width=6)

    drawn = False
    for i in range(100, rect.w - 50, 14):  # orbital plane
        if not drawn:
            draw.line(frame, gris, [i, rect.centery], [i + 14, rect.centery], width=2)
            drawn = True
        else:
            drawn = False

    drawn = False
    for i in range(planet.top - 50, planet.bottom + 50, 14):  # the line perpendicular to the orbital plane
        if not drawn:
            draw.line(frame, gris, [planet.centerx, i], [planet.centerx, i + 14], width=1)
            drawn = True
        else:
            drawn = False

    draw.circle(frame, amarillo, [100, rect.centery], 50)  # "here's a star"

    axial_tilt = [tilt - 90, tilt + 90]
    x1, y1 = set_xy(inflated_planet, tilt - 90)
    x2, y2 = set_xy(inflated_planet, tilt + 90)
    draw.line(frame, gris, [x1, y1], [x2, y2], width=3)  # axial tilt line

    equator = [tilt, tilt + 180]
    x1, y1 = set_xy(planet, equator[0])
    x2, y2 = set_xy(planet, equator[1])
    draw.line(frame, 'red', [x1, y1], [x2, y2], width=1)  # equator

    north_tropic = equator.copy()
    north_tropic[0] += tilt
    north_tropic[1] = 180
    x1, y1 = set_xy(planet, north_tropic[0])
    x2, y2 = set_xy(planet, north_tropic[1])
    x3, y3 = set_xy(margin_ext, north_tropic[0])
    draw.line(frame, 'orange', [x1, y1], [x2, y2], width=1)  # tropic
    tropic_north, hemisphere = hemiphere_note(tilt)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    render_rect = render.get_rect(center=[x3, y3])
    frame.blit(render, render_rect)

    south_tropic = equator.copy()
    south_tropic[0] = 0
    south_tropic[1] += tilt
    x1, y1 = set_xy(planet, south_tropic[0])
    x2, y2 = set_xy(planet, south_tropic[1])
    x3, y3 = set_xy(margin_ext, south_tropic[1])
    draw.line(frame, 'orange', [x1, y1], [x2, y2], width=1)  # tropic
    tropic_north, hemisphere = hemiphere_note(tilt, north=False)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    render_rect = render.get_rect(center=[x3, y3])
    frame.blit(render, render_rect)

    north_polar_circle = equator.copy()
    north_polar_circle[0] = axial_tilt[1] - tilt
    north_polar_circle[1] = axial_tilt[1] + tilt
    x1, y1 = set_xy(planet, north_polar_circle[0])
    x2, y2 = set_xy(planet, north_polar_circle[1])
    x3, y3 = set_xy(margin_ext, north_polar_circle[0])
    draw.line(frame, 'cyan', [x1, y1], [x2, y2], width=1)  # polar circle
    tropic_north, hemisphere = hemiphere_note(abs(90 - tilt), north=True)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    render_rect = render.get_rect(center=[x3, y3])
    frame.blit(render, render_rect)

    south_polar_circle = equator.copy()
    south_polar_circle[0] = axial_tilt[0] - tilt
    south_polar_circle[1] = axial_tilt[0] + tilt
    x1, y1 = set_xy(planet, south_polar_circle[0])
    x2, y2 = set_xy(planet, south_polar_circle[1])
    x3, y3 = set_xy(margin_ext, south_polar_circle[0])
    draw.line(frame, 'cyan', [x1, y1], [x2, y2], width=1)  # polar circle
    tropic_north, hemisphere = hemiphere_note(abs(90 - tilt), north=False)
    render = f2.render(str(round(tropic_north, 1)) + f"° {hemisphere}", 1, 'black')
    render_rect = render.get_rect(center=[x3, y3])
    frame.blit(render, render_rect)

    screen.blit(frame, (0, 0))

    return tilt


def axial_loop(planet):
    screen = display.set_mode((ANCHO, ALTO))
    panel = Surface((ANCHO, 300))
    panel_rect = panel.get_rect(y=330)

    done = False
    delta = 0
    tilt = 0
    mod = 1
    while not done:
        fps.tick(60)
        events = event.get([KEYDOWN, QUIT, KEYUP, MOUSEBUTTONDOWN, MOUSEMOTION])
        event.clear()

        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                quit()
                exit()
            if e.type == KEYUP:
                if e.key not in (K_LCTRL, K_RCTRL):
                    delta = 0
                else:
                    mod = 1

            if e.type == KEYDOWN:
                if e.key in (K_LCTRL, K_RCTRL):
                    mod = 10

                if e.key == K_UP:
                    delta = -1
                elif e.key == K_DOWN:
                    delta = +1
                elif e.key == K_RETURN or e.key == K_SPACE:
                    done = True

        if tilt + delta < 0:
            tilt = 180
        elif tilt + delta > 180:
            tilt = 0

        tilt += delta / mod
        screen.fill(COLOR_BOX)
        panel.fill(COLOR_BOX)
        interactive_loop(tilt)
        graph_seasonal_var(panel, tilt)
        print_info(panel, planet, round(tilt, 3), 165, 0, 410)
        screen.blit(panel, panel_rect)
        display.update()
    return q(tilt, 'degree')


__all__ = [
    'axial_loop'
]

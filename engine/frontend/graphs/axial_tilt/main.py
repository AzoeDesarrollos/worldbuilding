from pygame import KEYDOWN, K_UP, K_DOWN, QUIT, K_ESCAPE, K_SPACE, K_RETURN, KEYUP
from pygame import draw, font, display, event, quit, init, Surface, time
from engine.frontend.globales import ANCHO, ALTO
from .fuciones import set_xy
from .constantes import *
from sys import exit

init()
fps = time.Clock()
display.set_caption('Worldbuilding')


def hemiphere_note(angle: int):
    real = angle
    hemisphere = ''

    if 0 < angle <= 90:
        real = angle
        hemisphere = 'N'
    elif 90 < angle < 180:
        real = 90 + (90 - angle)
        hemisphere = 'S'
    # elif 180 <= angle < 270:
    #     real = abs(angle - 180)+90
    #     hemisphere = 'N'
    #     if real == 0:
    #         hemisphere = ''
    # elif 270 <= angle <= 360:
    #     real = 90 - abs(angle - 270)
    #     hemisphere = 'S'
    #     if real == 0:
    #         hemisphere = ''

    return real, hemisphere


def axial_loop():
    screen = display.set_mode((ANCHO, ALTO))
    frame = Surface(screen.get_size())
    frame.fill(blanco)

    rect = screen.get_rect()

    screen.fill(blanco)
    f = font.SysFont('Verdana', 16)
    f2 = font.SysFont('Verdana', 12)

    tilt = 0
    done = False
    delta = 0

    while not done:
        fps.tick(60)
        events = event.get([KEYDOWN, QUIT, KEYUP])

        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                quit()
                exit()

            elif e.type == KEYDOWN:
                if e.key == K_UP:
                    delta = -1
                elif e.key == K_DOWN:
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
        x3, y3 = set_xy(planet.inflate(10, 10), equator[0])
        x4, y4 = set_xy(planet.inflate(10, 10), equator[1])
        draw.line(frame, 'red', [x1, y1], [x2, y2], width=1)  # equator
        render = f2.render(" " + str(0) + "°", 1, 'red')
        render_rect = render.get_rect(center=[x3, y3])
        frame.blit(render, render_rect)
        render_rect = render.get_rect(center=[x4, y4])
        frame.blit(render, render_rect)

        north_tropic = equator.copy()
        north_tropic[0] += tilt
        north_tropic[1] = 180
        x1, y1 = set_xy(planet, north_tropic[0])
        x2, y2 = set_xy(planet, north_tropic[1])
        draw.line(frame, 'orange', [x1, y1], [x2, y2], width=1)  # tropic
        # tropic_north, hemisphere = hemiphere_note(tilt)
        # render = f2.render(str(tropic_north) + f"° {hemisphere}", 1, 'black')
        # frame.blit(render, [x1, y1])

        south_tropic = equator.copy()
        south_tropic[0] = 0
        south_tropic[1] += tilt
        x1, y1 = set_xy(planet, south_tropic[0])
        x2, y2 = set_xy(planet, south_tropic[1])
        draw.line(frame, 'orange', [x1, y1], [x2, y2], width=1)  # tropic
        # tropic_north, hemisphere = hemiphere_note(north_tropic[0])
        # render = f2.render(str(tropic_north) + f"° {hemisphere}", 1, 'black')
        # frame.blit(render, [x1, y1])

        north_polar_circle = equator.copy()
        north_polar_circle[0] = axial_tilt[0] - tilt
        north_polar_circle[1] = axial_tilt[0] + (
                axial_tilt[0] - north_polar_circle[0]) + 360  # don't know if this is right.
        x1, y1 = set_xy(planet, north_polar_circle[0])
        x2, y2 = set_xy(planet, north_polar_circle[1])
        draw.line(frame, 'cyan', [x1, y1], [x2, y2], width=1)  # polar circle
        # render = f2.render(str(north_polar_circle[0]) + f"° {hemisphere}", 1, 'black')
        # frame.blit(render, [x2, y2])

        south_polar_circle = equator.copy()
        south_polar_circle[0] = north_polar_circle[1] + 180
        south_polar_circle[1] = north_polar_circle[0] + 180
        x1, y1 = set_xy(planet, south_polar_circle[0])
        x2, y2 = set_xy(planet, south_polar_circle[1])
        draw.line(frame, 'cyan', [x1, y1], [x2, y2], width=1)  # polar circle
        # render = f2.render(str(north_polar_circle[0]) + f"° {hemisphere}", 1, 'black')
        # frame.blit(render, [x2, y2])

        render_tilt = f.render('tilt: ' + str(round(tilt, 2)), True, negro)
        tilt_rect = render_tilt.get_rect(right=rect.w)
        frame.blit(render_tilt, tilt_rect)

        screen.fill(blanco)
        screen.blit(frame, (0, 0))
        display.update()

    return tilt


__all__ = [
    'axial_loop'
]

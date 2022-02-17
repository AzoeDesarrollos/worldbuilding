from pygame import KEYDOWN, K_UP, K_DOWN, QUIT, K_ESCAPE, K_SPACE, K_RETURN, KEYUP
from pygame import draw, font, display, event, quit, init, Surface, time
from engine.frontend.globales import ANCHO, ALTO
from .fuciones import set_xy, interpolate
from .constantes import *
from sys import exit

init()
fps = time.Clock()
display.set_caption('Worldbuilding')


def axial_loop():
    screen = display.set_mode((ANCHO, ALTO))
    frame = Surface(screen.get_size())
    frame.fill(blanco)

    rect = screen.get_rect()

    screen.fill(blanco)
    f = font.SysFont('Verdana', 16)

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
                    delta = +1
                elif e.key == K_DOWN:
                    delta = -1
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

        x1, y1 = set_xy(planet.inflate(75, 75), tilt - 90)
        x2, y2 = set_xy(planet.inflate(75, 75), tilt + 90)
        draw.line(frame, negro, [x1, y1], [x2, y2], width=1)  # axial tilt line

        x1, y1 = set_xy(planet, tilt - 180)
        x2, y2 = set_xy(planet, tilt)
        draw.line(frame, 'red', [x1, y1], [x2, y2], width=1)  # equator

        north_tropic = interpolate(tilt, planet.h)
        x1, y1 = set_xy(planet, tilt)
        x2, y2 = set_xy(planet, north_tropic+tilt)
        draw.line(frame, 'black', [x1, y1], [x2, y2], width=1)  # equator

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

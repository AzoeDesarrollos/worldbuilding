from pygame import display, event, init, quit, Surface, draw, font, time, Color
from pygame import QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_UP, K_DOWN, K_SPACE
from math import sin, cos, sqrt, radians, pow
from engine import q
from sys import exit

init()

fuente1 = font.SysFont('Verdana', 16)
fuente2 = font.SysFont('Verdana', 14)
fuente3 = font.SysFont('Verdana', 12)

render_x = fuente1.render('x', 1, Color('black'))
render_y = fuente1.render('y', 1, Color('black'))
render_z = fuente1.render('z', 1, Color('black'))

rect_x = render_x.get_rect(x=390, y=200)
rect_top = render_y.get_rect(x=202, y=0)
rect_mid = render_z.get_rect(x=190, y=rect_x.y)

text_a = 'Adjusting the Argument of periapsis'.center(45, ' ')
text_b = 'Adjusting the Longitude of the ascending node'
text_c = 'Press [Space] to set the value and move on to the next.'
text_d = 'Press [Space] to set the value and close.'

render_text_a = fuente2.render(text_a, 1, Color('black'))
render_text_b = fuente2.render(text_b, 1, Color('black'))
instruction1 = fuente3.render(text_c, 1, Color('black'))
instruction2 = fuente3.render(text_d, 1, Color('black'))

rect_text = render_text_b.get_rect(centerx=200, bottom=440)
rect_instruction = instruction1.get_rect(bottom=rect_text.top - 2)

render_rotation = fuente2.render('Rotation: ', 1, Color('black'))
rect_rotation = render_rotation.get_rect()

# mock orbit since these parameters are independent.
a = 1
e = 0.7
b = (sqrt(1 - pow(e, 2)))
c = sqrt(pow(a, 2) - pow(b, 2))

# some adjustments for positioning
delta = 100
a *= delta
b *= delta
c *= delta

c1, c2 = 200, 200
offset_x = c1
offset_y = c2


def draw_ellipse(rot_angle):
    img = Surface((400, 400))
    img.fill(Color('white'))
    rect = img.get_rect()

    draw.line(img, Color('grey'), rect.midleft, rect.midright, 1)
    draw.line(img, Color('grey'), rect.midtop, rect.midbottom, 1)

    r = radians(rot_angle)
    cos_r, sin_r = cos(r), sin(r)
    cx = c * cos_r
    cy = c * sin_r
    for angle in range(0, 361):
        ang = radians(angle)
        cos_a, sin_a = cos(ang), sin(ang)

        #   offsets, foci,  ellipse,  rotation...
        x = offset_x + cx + a * cos_a * cos_r - b * sin_a * sin_r
        y = offset_y + cy + b * sin_a * cos_r + a * cos_a * sin_r
        img.set_at((int(x), int(y)), Color('black'))

    draw.circle(img, Color('yellow'), (c1, c2), 7)

    return img


def rotation_loop():
    display.quit()
    fps = time.Clock()
    rect_a = rect_top
    rect_b = rect_mid
    screen = display.set_mode((400, 440))
    rotation_delta = 0
    text = render_text_b
    actual_rotation = 0
    instruction = instruction1
    running = True
    rot = []
    rotation = 270
    while running:
        fps.tick(60)
        events = event.get([QUIT, KEYDOWN, KEYUP])
        event.clear()
        for ev in events:
            if (ev.type == QUIT) or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                quit()
                exit()
            elif ev.type == KEYDOWN:
                if ev.key == K_UP:
                    rotation_delta = -1

                elif ev.key == K_DOWN:
                    rotation_delta = +1

                elif ev.key == K_SPACE:
                    if rect_a == rect_top:
                        rect_a = rect_mid
                        rect_b = rect_top
                        text = render_text_a
                        instruction = instruction2
                    else:
                        running = False
                    rot.append(q(actual_rotation, 'degree'))
                    rotation = 270

            elif ev.type == KEYUP:
                rotation_delta = 0

        if -90 <= rotation + rotation_delta <= 270:
            rotation += rotation_delta
            actual_rotation = round(abs(rotation - 270), 3)

        canvas = draw_ellipse(rotation)
        screen.fill(Color('grey'))
        screen.blit(canvas, (0, 0))
        screen.blit(render_x, rect_x)
        screen.blit(render_y, rect_a)
        screen.blit(render_z, rect_b)

        screen.blit(text, rect_text)
        screen.blit(instruction, rect_instruction)

        screen.blit(render_rotation, rect_rotation)
        screen.blit(fuente2.render(str(actual_rotation) + '°', 1, Color('black')), rect_rotation.topright)
        display.update()

    return rot


__all__ = [
    'rotation_loop'
]

if __name__ == '__main__':
    data = rotation_loop()

from pygame import Surface, image, draw, Rect
from decimal import Decimal, getcontext
from random import randint

getcontext().prec = 2
size = 2052
surf = Surface((size, size / 6))
surf_rect = surf.get_rect()
centery = surf_rect.centery
w, h = surf_rect.size
for i in range(1000):
    x = randint(0, w)
    y = randint(0, h)
    surf.set_at((x, y), (255, 255, 255))

radiuses = [0.34, 0.53, 0.72, 0.99, 1.05, 1.42, 2.06, 3.09, 4.02, 5.02, 6.02, 9.03, 16.25, 21.91, 32.87, 39.44]
draw.circle(surf, (255, 255, 0), surf_rect.midleft, 11)  # star
for i, r in enumerate(radiuses):
    radio = Decimal(r) * Decimal(100.0)
    rect = Rect(0, 0, radio, radio)
    rect.center = surf_rect.midleft
    if r == 5.02:  # frost line
        color = 0, 0, 255
    elif r in (0.99, 1.42):  # habitable zone
        color = 0, 255, 0
    else:
        color = 255, 255, 255
    draw.ellipse(surf, color, rect, 1)

    pos = (rect.right - 1, centery)
    if r in (0.34, 0.53, 0.72):  # terrestial planets
        draw.circle(surf, (255, 0, 0), pos, 3)
    elif r == 1.05:  # main planet
        draw.circle(surf, (255, 0, 255), pos, 3)
    elif r in (2.06, 3.09, 4.02):  # terrestial planet
        draw.circle(surf, (255, 0, 0), pos, 3)
    elif r in (6.02, 9.03, 16.25, 21.91, 32.87, 39.44):  # gas giants
        draw.circle(surf, (0, 0, 255), pos, 6)

image.save(surf, 'D:/Python/wb/data/orbita.png')

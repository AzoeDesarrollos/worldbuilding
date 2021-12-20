from pygame import draw, Surface, SRCALPHA
from math import sin, cos, radians, ceil
from .basewidget import BaseWidget


class StarSprite(BaseWidget):
    centerx = 0
    centery = 0
    ticks = 0
    has_mouseover = False
    clicked = False

    def __init__(self, parent, star, x, y):
        super().__init__(parent)
        self.radius = round(star.radius.m * 10)

        if self.radius % 2 == 0:
            self.radius += 1
        self.color = star.color
        self.image = self.create()
        self.rect = self.image.get_rect(center=(x, y))
        self.centerx, self.centery = [self.radius - 1] * 2
        self.draw_rays()

    def create(self):
        image = Surface((2 * self.radius, 2 * self.radius), SRCALPHA)
        rect = image.get_rect()
        draw.circle(image, self.color, rect.center, self.radius // 4 * 3)
        return image

    def draw_rays(self, start=0):
        for angulo in range(start, 181, 10):
            contra = (angulo - 180) + 360
            x1, y1 = self.set_xy(angulo)
            x2, y2 = self.set_xy(contra)
            draw.aaline(self.image, self.color, (x1, y1), (x2, y2))

    def set_xy(self, angle: int):
        x = round(self.centerx + self.radius * cos(radians(angle)))
        y = round(self.centery + self.radius * sin(radians(angle)))
        return x, y

    def animate(self):
        self.ticks += 1
        self.image.fill((0, 0, 0, 255))
        self.image = self.create()
        if self.ticks <= 30:
            self.draw_rays(start=0)
        elif self.ticks <= 60:
            self.draw_rays(start=15)
        else:
            self.ticks = 0

    def on_mouseover(self):
        self.animate()

    def is_distict(self, other):
        # similar to __eq__(), but doesn't induce a conflict with hash().
        if other is not None:
            return self.color != other.color and self.radius != other.radius
        return True


class PlanetSprite(BaseWidget):
    centerx = 0
    centery = 0
    ticks = 0
    has_mouseover = False
    clicked = False

    def __init__(self, parent, planet, x, y):
        super().__init__(parent)
        self.radius = round((planet.radius.m * 10) + 2)
        self.composition = planet.composition
        if self.radius % 2 == 0:
            self.radius += 1

        self.image = self.create()
        self.rect = self.image.get_rect(center=(x, y))
        self.centerx, self.centery = [self.radius - 1] * 2

    def create(self):
        image = Surface((2 * self.radius, 2 * self.radius), SRCALPHA)
        rect = image.get_rect()
        blobs = {}
        components = {
            'iron': [200, 200, 200],
            'silicates': [159, 129, 112],
            'water ice': [0, 150, 150],
            'hydrogen': [0, 225, 225],
            'helium': [255, 255, 255]
        }

        last_radius = 0
        for element, color in components.items():
            if element in self.composition and self.composition[element] > 0:
                last_radius += ceil(self.radius * (self.composition[element] / 100))
                blob = Surface((last_radius * 2, last_radius * 2), SRCALPHA)
                blobrect = blob.get_rect()
                draw.circle(blob, color, blobrect.center, last_radius)
                blobrect.center = rect.center
                blobs[element] = [blob, blobrect]

        for element in reversed(sorted(blobs, key=lambda e: blobs[e][1].width)):
            image.blit(*blobs[element])

        return image

    def on_mousebuttondown(self, event):
        comp = self.composition
        if event.button == 1:
            text = 'Compostition:\n\n'
            text += '\n'.join([e.capitalize()+': {:n}%'.format(round(comp[e], 2)) for e in comp if comp[e] > 0])
            raise AssertionError(text)

from pygame import draw, Surface, SRCALPHA
from .basewidget import BaseWidget
from math import ceil


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
        if event.origin == self:
            comp = self.composition
            if event.data['button'] == 1:
                text = 'Compostition:\n\n'
                text += '\n'.join([e.capitalize()+': {:n}%'.format(round(comp[e], 2)) for e in comp if comp[e] > 0])
                raise AssertionError(text)

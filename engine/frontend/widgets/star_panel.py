from .sprite_star import StarSprite
from .object_type import ObjectType
from .base_panel import BasePanel


class StarPanel(BasePanel):
    def __init__(self):
        super().__init__('Star')
        self.current = StarType(self)


class StarType(ObjectType):
    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Luminosity', 'Radius', 'Lifetime', 'Temperature'],
                         ['Volume', 'Density', 'Circumference', 'Surface', 'Classification'])

    def set_star(self, star):
        self.current = star
        self.has_values = True
        self.fill()

    def fill(self, tos=None):
        tos = {
            'Mass': 'kg',
            'Radius': 'km',
            'Luminosity': 'W',
            'Lifetime': 'year',
            'Temperature': 'kelvin'
        }
        super().fill(tos)

        sprite = StarSprite(self.current, 460, 100)
        self.parent.image.blit(sprite.image, sprite.rect)

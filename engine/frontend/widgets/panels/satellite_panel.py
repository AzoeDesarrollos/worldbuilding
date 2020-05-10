from engine.frontend.globales import COLOR_TEXTO, COLOR_AREA
from engine.frontend.widgets.values import ValueText
# from engine.equations.satellite import create_moon
from engine import material_densities
from ..object_type import ObjectType
from .base_panel import BasePanel
from pygame import font


class SatellitePanel(BasePanel):
    unit = None

    def __init__(self, parent):
        super().__init__('Satellite', parent)
        self.current = SatelliteType(self)
        self.image.fill(COLOR_AREA, [0, 420, self.rect.w // 2, 200])
        f = font.SysFont('Verdana', 16)
        f.set_underline(True)
        render = f.render('Composition', 1, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(topleft=(0, 420))
        self.image.blit(render, render_rect)


class SatelliteType(ObjectType):
    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Clase'])
        for i, name in enumerate(sorted(material_densities)):
            a = ValueText(self, name.capitalize(), 3, 420 + 21 + i * 21, bg=COLOR_AREA)
            self.properties.add(a, layer=7)

    def calculate(self):
        star = self.parent.parent.system.star
        planet = self.parent.parent.system.current
        print(star, planet)
        # total = 0
        # for material in self.properties.get_sprites_from_layer(7):
        #     if material.text_area.value:  # not empty
        #         print(material.text, material.text_area.value)
        #         total += float(material.text_area.value)
        # print(total)

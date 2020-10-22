from engine.frontend.globales import COLOR_TEXTO, COLOR_AREA, ANCHO
from engine.frontend.widgets.values import ValueText
from engine.equations.planetary_system import system
from engine.equations.satellite import create_moon
from engine.frontend.globales import WidgetGroup
from engine import material_densities
from ..object_type import ObjectType
from .base_panel import BasePanel
from .common import ListedArea, PlanetButton
from pygame import font


class SatellitePanel(BasePanel):
    unit = None

    def __init__(self, parent):
        super().__init__('Satellite', parent)
        self.current = SatelliteType(self)
        self.image.fill(COLOR_AREA, [0, 420, self.rect.w // 2, 200])
        f = font.SysFont('Verdana', 16)
        f.set_underline(True)
        render = f.render('Composition', True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(topleft=(0, 420))
        self.image.blit(render, render_rect)
        self.properties = WidgetGroup()
        self.area_planets = AvailablePlanets(self, ANCHO - 200, 32, 200, 350)
        self.properties.add(self.area_planets)

    def show(self):
        super().show()
        self.is_visible = True
        for pr in self.properties.widgets():
            pr.show()

    def hide(self):
        super().hide()
        for pr in self.properties.widgets():
            pr.hide()


class SatelliteType(ObjectType):
    planet = None

    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Clase'])
        for i, name in enumerate(sorted(material_densities)):
            a = ValueText(self, name.capitalize(), 3, 420 + 21 + i * 21, bg=COLOR_AREA)
            self.properties.add(a, layer=7)

    def calculate(self):
        star = system.star
        data = {'composition': {}}
        for material in self.properties.get_sprites_from_layer(7):
            if material.text_area.value:  # not empty
                data['composition'][material.text.lower()] = float(material.text_area.value)
        for item in self.properties.get_widgets_from_layer(1):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        self.current = create_moon(self.planet, star, data)
        self.has_values = True
        self.fill()

    def set_planet(self, planet):
        self.planet = planet

    def fill(self, tos=None):
        tos = {
            'Mass': 'kg',
            'Radius': 'km',
            'Gravity': 'm/s**2',
            'Escape_velocity': 'km/s'
        }
        super().fill(tos)


class AvailablePlanets(ListedArea):
    def populate(self, planets):
        for i, planet in enumerate(planets):
            listed = ListedPlanet(self, planet, self.rect.x + 3, i * 16 + self.rect.y + 21)
            self.listed_objects.add(listed)

    def show(self):
        super().show()
        self.populate(system.planets)
        for listed in self.listed_objects.widgets():
            listed.show()


class ListedPlanet(PlanetButton):
    def on_mousebuttondown(self, event):
        pass

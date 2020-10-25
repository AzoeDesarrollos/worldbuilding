from .common import ListedArea, PlanetButton, TextButton, Meta
from engine.frontend.widgets.basewidget import BaseWidget
from engine.frontend.globales import COLOR_AREA, ANCHO
from engine.equations.planetary_system import Systems
from engine.frontend.widgets.values import ValueText
from engine.equations.satellite import create_moon
from engine.frontend.globales import WidgetGroup
from engine import material_densities
from ..object_type import ObjectType
from .base_panel import BasePanel


class SatellitePanel(BasePanel):
    curr_x = 0
    curr_y = 0

    def __init__(self, parent):
        super().__init__('Satellite', parent)
        self.current = SatelliteType(self)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 32, 200])
        self.area_satellites = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 400, 200))
        self.curr_x = self.area_satellites.x + 3
        self.curr_y = self.area_satellites.y + 21
        f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(13, underline=True)
        self.write('Composition', f1, COLOR_AREA, topleft=(0, 420))
        self.write('Satellites', f2, COLOR_AREA, x=self.area_satellites.x + 3, y=self.area_satellites.y)
        self.properties = WidgetGroup()
        self.area_planets = AvailablePlanets(self, ANCHO - 200, 32, 200, 350)
        self.button = AddMoonButton(self, 476, 416)
        self.properties.add(self.area_planets, self.button)
        self.satellites = WidgetGroup()

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.satellites.get_widgets_from_layer(Systems.get_current_idx()):
            bt.move(x, y)
            if not self.area_satellites.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def set_planet(self, planet):
        self.current.set_planet(planet)

    def set_planet_satellite(self):
        planet = self.current.planet
        planet.satellites.append(self.current)
        self.add_button()
        self.current.erase()

    def add_button(self):
        button = SatelliteButton(self.current, self.current.current, self.curr_x, self.curr_y)
        self.satellites.add(button, layer=Systems.get_current_idx())
        self.sort_buttons()

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
        star = Systems.get_current().star_system
        data = {'composition': {}}
        for material in self.properties.get_sprites_from_layer(7):
            if material.text_area.value:  # not empty
                data['composition'][material.text.lower()] = float(material.text_area.value)
        for item in self.properties.get_widgets_from_layer(1):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        assert self.planet, 'Must select a planet'
        self.has_values = True

        if self.current is None:
            self.current = create_moon(self.planet, star, data)
            self.parent.button.enable()
        else:
            for item in self.properties.get_widgets_from_layer(7):
                if item.text.lower() in self.current.composition:
                    item.value = str(self.current.composition[item.text.lower()])
                else:
                    item.value = '0'

        self.fill()

    def show_current(self, satellite):
        self.erase()
        self.current = satellite
        self.calculate()

    def erase(self):
        super().erase()
        for vt in self.properties:
            vt.value = ''

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
        system = Systems.get_current()
        self.populate([p for p in system.planets if not len(p.satellites)])
        for listed in self.listed_objects.widgets():
            listed.show()


class ListedPlanet(PlanetButton):
    def on_mousebuttondown(self, event):
        self.select()
        self.parent.parent.set_planet(self.object_data)


class AddMoonButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Satellite', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.set_planet_satellite()


class SatelliteButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, satellite, x, y):
        super().__init__(parent)
        self.object_data = satellite
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.img_uns = self.f1.render(satellite.cls, True, satellite.color, COLOR_AREA)
        self.img_sel = self.f2.render(satellite.cls, True, satellite.color, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.show_current(self.object_data)

    def move(self, x, y):
        self.rect.topleft = x, y

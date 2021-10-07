from engine.equations.tides import major_tides, minor_tides, is_tidally_locked
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup
from .common import AvailableObjects, AvailablePlanet
from engine.equations.planetary_system import Systems
from ..basewidget import BaseWidget
from pygame import Surface
from engine import q


class TidesPanel(BaseWidget):
    skippable = False

    current = None

    def __init__(self, parent):
        self.name = 'Tides'
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        self.f2 = self.crear_fuente(14)
        self.f3 = self.crear_fuente(16)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.properties.add(self.planet_area, layer=2)

    def show_name(self, astrobody):
        self.image.fill(COLOR_BOX, (0, 21, self.rect.w, 16))
        self.image.fill(COLOR_BOX, (3, 50, self.rect.w, 200))
        text = 'Tides on ' + astrobody.clase
        idx = Systems.get_current().astro_group(astrobody).index(astrobody)
        text += ' #' + str(idx)

        self.write(text, self.f2, centerx=(ANCHO // 4) * 1.5, y=21)

        self.current = astrobody
        self.show_selected()

    def clear(self):
        self.image.fill(COLOR_BOX, (0, 21, self.rect.w, 32))
        self.image.fill(COLOR_BOX, (3, 40, self.rect.w, 200))

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()

    def hide(self):
        self.clear()
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def show_selected(self):
        system = Systems.get_current()
        astrobody = self.current
        diameter = astrobody.radius.to('earth_radius').m * 2

        if system.star_system.letter == 'S':
            star = system.star_system.primary
            stellar_tides = minor_tides(diameter, star.mass.m, astrobody.orbit.a.m)
        else:
            combined_mass = sum([star.mass.m for star in system.star_system])
            stellar_tides = minor_tides(diameter, combined_mass, astrobody.orbit.a.m)

        if astrobody.celestial_type == 'planet':
            lunar_tides = 0
            primary = 'star'
            for satellite in astrobody.satellites:
                if satellite.celestial_type == 'satellite':
                    lunar_tides += major_tides(diameter, satellite.mass.m, satellite.orbit.a.to('earth_diameter').m)
        else:
            primary = 'planet'
            lunar_tides = major_tides(diameter, astrobody.orbit.star.mass.m, astrobody.orbit.a.to('earth_diameter').m)

        std_high = q(lunar_tides * 0.54, 'm')
        std_low = -std_high

        spring_high = q((lunar_tides + stellar_tides) * 0.54, 'm')  # meters
        spring_low = -spring_high

        neap_high = q((lunar_tides - stellar_tides) * 0.54, 'm')  # meters
        neap_low = -neap_high

        resolution = 4

        rect = self.write('Standard high: {}'.format(round(std_high, resolution)), self.f2, x=3, y=50)
        rect = self.write('Standard low: {}'.format(round(std_low, resolution)), self.f2, x=3, y=rect.bottom + 2)
        rect = self.write('Spring high: {}'.format(round(spring_high, resolution)), self.f2, x=3, y=rect.bottom + 12)
        rect = self.write('Spring low: {}'.format(round(spring_low, resolution)), self.f2, x=3, y=rect.bottom + 2)
        rect = self.write('Neap high: {}'.format(round(neap_high, resolution)), self.f2, x=3, y=rect.bottom + 12)
        rect = self.write('Neap low: {}'.format(round(neap_low, resolution)), self.f2, x=3, y=rect.bottom + 2)

        if is_tidally_locked(lunar_tides, system.age.m, self.current.orbit.star.mass.m):
            text = '{} is tidally locked to its {}'.format(str(self.current), primary)
        elif is_tidally_locked(stellar_tides, system.age.m, self.current.orbit.star.mass.m):
            text = '{} is tidally locked to its {}'.format(str(self.current), primary)
        else:
            text = '{} is not tidally locked'.format(str(self.current))

        self.write(text, self.f3, x=3, y=rect.bottom + 12)


class Astrobody(AvailablePlanet):

    def on_mousebuttondown(self, event):
        self.parent.select_one(self)
        self.parent.parent.show_name(self.object_data)


class AvailablePlanets(AvailableObjects):
    listed_type = Astrobody

    def show(self):
        system = Systems.get_current()
        self.deselect_all()
        if system is not None:
            bodies = [body for body in system.astro_bodies if body.orbit is not None]
            self.populate(bodies)
        super().show()

    def on_mousebuttondown(self, event):
        super().on_mousebuttondown(event)
        self.parent.clear()

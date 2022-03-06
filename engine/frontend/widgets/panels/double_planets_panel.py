from engine.frontend.widgets.panels.common import ListedBody, ListedArea, ColoredBody, TextButton
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, Group
from engine.frontend.widgets.basewidget import BaseWidget
from engine.backend import Systems, q
from engine.equations.binary import PlanetaryPTypeSystem
from .star_system_panel import SystemType
from pygame import Surface
from random import choice


class DoublePlanetsPanel(BaseWidget):
    skippable = True
    skip = False

    last_idx = None

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Double Planets'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', self.f1, centerx=(ANCHO // 4) * 1.5, y=0)
        self.current = DoublesType(self)
        self.planets_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.systems_area = self.image.fill(COLOR_AREA, [0, 280, 380, 130])
        self.planet_buttons = Group()
        self.properties = Group()
        self.primary_planets = {}
        self.setup_button = SetupButton(self, 484, 416)
        self.undo_button = UndoButton(self, self.setup_button.rect.left-50, 416)
        self.f2 = self.crear_fuente(14, underline=True)
        self.write('Potential Planets', self.f2, COLOR_AREA, x=self.area_buttons.x+3, y=self.area_buttons.y+2)
        self.write('Double Planets', self.f2, COLOR_AREA, x=self.systems_area.x + 3, y=self.systems_area.y + 2)

        self.properties.add(self.planets_area, self.undo_button, self.setup_button, layer=1)

    def populate(self, *planets, layer: str):
        if layer not in self.primary_planets:
            self.primary_planets[layer] = []

        for planet in planets:
            if planet not in self.primary_planets[layer]:
                self.primary_planets[layer].append(planet)

    def show(self):
        super().show()
        self.current.show()
        for widget in self.properties.get_widgets_from_layers(1, 3):
            widget.show()

    def hide(self):
        super().hide()
        self.current.hide()
        for widget in self.properties.get_widgets_from_layers(1, 3):
            widget.hide()

    def create_buttons(self, planet):
        pm = planet.mass.to('earth_mass').m
        layer = self.last_idx
        widgets = self.primary_planets[layer]
        by_mass = sorted(widgets, key=lambda b: abs(pm / b.mass.to('earth_mass').m))
        by_mass.pop(by_mass.index(planet))
        selected = []
        for i, p in enumerate(by_mass):
            mass_of_p = p.mass.to('earth_mass').m
            ratio = min([pm, mass_of_p]) / max([pm, mass_of_p])
            if 0.8 <= ratio <= 1.1:
                if planet.id not in self.planet_buttons.layers:
                    self.add_button(p, planet.id)
                    selected.append(p)

        for button in self.planet_buttons.get_widgets_from_layers(planet.id):
            button.hide()
        self.sort_buttons(self.planet_buttons.get_widgets_from_layer(planet.id))
        return selected

    def add_button(self, planet, layer):
        button = CreatedPlanet(self, planet, str(planet), self.curr_x, self.curr_y)
        self.planet_buttons.add(button, layer=layer)
        self.properties.add(button, layer=3)
        self.image.fill(COLOR_AREA, self.area_buttons)
        return button

    def hide_buttons(self):
        for button in self.planet_buttons.widgets():
            button.hide()

    def suggest(self):
        primary = self.current.primary.value
        secondary = self.current.secondary.value

        primary_r = primary.radius.to('earth_radius').m
        secondary_r = secondary.radius.to('earth_radius').m

        primary_m = primary.mass.to('earth_mass').m
        secondary_m = secondary.mass.to('earth_mass').m
        choices = []
        for avg_sep in (primary_r * 3, secondary_r * 3):
            barycenter = avg_sep * (secondary_m / (primary_m + secondary_m))
            primary_distance = round(barycenter, 2)
            secondary_distance = round(avg_sep - primary_distance, 2)
            if primary_r < primary_distance and secondary_r < secondary_distance:
                choices.append(avg_sep)

        chosen = q(choice(choices), 'earth_radius')
        vt = self.current.properties.get_widget(2)
        vt.text_area.set_value(chosen)

    def update(self):
        idx = Systems.get_current_id(self)
        if idx != self.last_idx:
            self.last_idx = idx
            if self.last_idx not in self.primary_planets:
                self.primary_planets[self.last_idx] = []


class DoublesType(SystemType):

    def __init__(self, parent):
        props = [
            'Primary Planet', 'Secondary Planet', 'Average Separation',
            'Eccentriciy (primary)', 'Eccentricty (secondary)', 'Barycenter',
            'Maximun Separation', 'Minimun Separation']
        super().__init__(parent, props)

    def unset_planets(self):
        self.parent.planets_area.show()
        self.erase()
        self.parent.hide_buttons()

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                self.current = PlanetaryPTypeSystem(*self.get_determinants(), unit='earth_radius')
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep', 'min_sep']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            self.parent.setup_button.enable()


class PotentialPlanet(ListedBody):
    # Because it has the "potential" to form a double planet system.
    enabled = True

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.parent.current.set_bodies(self.object_data)
            created = self.parent.parent.create_buttons(self.object_data)
            self.parent.remove_listed(self)
            for pln in created:
                self.parent.delete_objects(pln)
            self.kill()
            self.parent.sort()


class AvailablePlanets(ListedArea):
    name = 'Planets'
    listed_type = PotentialPlanet

    def show(self):
        for system in Systems.get_systems():
            idx = system.id
            self.populate(system.planets, layer=idx)
            self.parent.populate(*system.planets, layer=idx)
        # else:
        #     hide the panel
        super().show()


class CreatedPlanet(ColoredBody):
    enabled = True

    def disable(self):
        self.enabled = False

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.set_bodies(self.object_data)
            self.parent.suggest()
        return self

    def update(self):
        super().update()
        if self.object_data.flagged:
            self.kill()


class UndoButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Undo'
        super().__init__(parent, name, 0, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        self.parent.current.unset_planets()
        self.disable()


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            pass
            # sistema = self.parent.current.current
            # self.parent.create_button(sistema)
            # self.parent.current.erase()
            # self.disable()

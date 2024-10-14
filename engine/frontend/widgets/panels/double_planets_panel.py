from engine.frontend.widgets.panels.common import ListedBody, ListedArea, ColoredBody, TextButton
from .star_system_panel import SystemType, SystemButton, DissolveButton, AutoButton
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, Group
from engine.equations.system_binary import PlanetaryPTypeSystem
from engine.frontend.widgets.basewidget import BaseWidget
from engine.backend import q, EventHandler
from engine.equations import Universe
from pygame import Surface


class DoublePlanetsPanel(BaseWidget):
    skippable = True
    _skip = False

    last_id = None

    curr_s_x = None
    curr_s_y = None

    show_swap_system_button = True

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Double Planets'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.current = DoublesType(self)
        self.planets_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.auto_button = AutoButton(self, ANCHO - 260, 133)

        self.system_buttons = Group()
        self.systems = []
        self.planet_buttons = Group()
        self.properties = Group()
        self.primary_planets = {}
        self.setup_button = SetupButton(self, 484, 416)
        self.undo_button = UndoButton(self, self.setup_button.rect.left - 50, 416)
        self.dissolve_button = DissolveSystemsButton(self, self.undo_button.rect.x, self.planets_area.rect.bottom + 21)
        f = self.crear_fuente(14, underline=True)
        self.write('Double Planets', f, COLOR_AREA, x=self.area_buttons.x + 3, y=self.area_buttons.y)

        self.properties.add(self.planets_area, self.undo_button, self.auto_button,
                            self.setup_button, self.dissolve_button, layer=1)

        EventHandler.register(self.save_systems, 'Save')
        EventHandler.register(self.load_systems, 'LoadBinary')
        EventHandler.register(self.export_data, 'ExportData')

    @property
    def skip(self):
        return self._skip

    @skip.setter
    def skip(self, value):
        self._skip = value

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
        layer = self.last_id
        widgets = self.primary_planets[layer]
        by_mass = sorted(widgets, key=lambda b: abs(pm / b.mass.to('earth_mass').m))
        by_mass.pop(by_mass.index(planet))
        for i, p in enumerate(by_mass):
            mass_of_p = p.mass.to('earth_mass').m
            ratio = min([pm, mass_of_p]) / max([pm, mass_of_p])
            if not (0.8 <= ratio <= 1.1):
                self.planets_area.disable_object(p)

        self.sort_buttons(self.planet_buttons.get_widgets_from_layer(planet.id))

    def add_button(self, planet, layer):
        button = CreatedPlanet(self, planet, str(planet), self.curr_x, self.curr_y)
        self.planet_buttons.add(button, layer=layer)
        self.properties.add(button, layer=3)
        self.image.fill(COLOR_AREA, [0, 441, self.rect.w, 189])
        return button

    def del_button(self, system):
        button = [i for i in self.system_buttons.widgets() if i.object_data == system][0]
        self.systems.remove(system)
        self.system_buttons.remove(button)
        button.kill()
        self.sort_buttons(self.system_buttons.widgets())
        self.properties.remove(button)
        self.dissolve_button.disable()

    def hide_buttons(self):
        for button in self.planet_buttons.widgets():
            button.hide()

    def create_system_button(self, system_data):
        if system_data not in self.systems:
            Universe.current_planetary().add_astro_obj(system_data)
            idx = len([s for s in self.systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, 0, 0)
            self.systems.append(system_data)
            self.system_buttons.add(button)
            self.properties.add(button)
            if self.is_visible:
                self.sort_buttons(self.system_buttons.widgets())
            self.current.enable()

    def show_current(self, system):
        self.current.erase()
        self.current.current = system
        self.current.reset(system)

    def save_systems(self, event):
        macro_data = {}
        for system in self.systems:
            data = {
                'primary': system.primary.id,
                'secondary': system.secondary.id,
                'avg_s': system.average_separation.m,
                'ecc_p': system.ecc_p.m,
                "ecc_s": system.ecc_s.m,
                "name": system.name,
                "neighbourhood_id": Universe.nei().id,
                "flagged": system.flagged
            }
            if system.cartesian is not None:
                data.update({"position": dict(zip(['x', 'y', 'z'], system.cartesian))})
            macro_data[system.id] = data

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Binary Systems': macro_data})

    def load_systems(self, event):
        for id in event.data['Binary Systems']:
            system_data = event.data['Binary Systems'][id]
            prim = Universe.get_astrobody_by(system_data['primary'], 'id', silenty=True)
            scnd = Universe.get_astrobody_by(system_data['secondary'], 'id', silenty=True)
            if 'system_id' in system_data:
                systems = Universe.nei().true_systems
                sstm = [s for s in systems if s.id == system_data['system_id']]
                if len(sstm):
                    sstm = sstm[0]
            else:
                continue
            if prim.celestial_type == 'planet' and scnd.celestial_type == 'planet':
                avg_s = system_data['avg_s']
                ecc_p = system_data['ecc_p']
                ecc_s = system_data['ecc_s']

                system = PlanetaryPTypeSystem(sstm, prim, scnd, avg_s, ecc_p, ecc_s, idx=id)

                self.systems.append(system)

                Universe.add_astro_obj(system)

                self.create_system_button(system)

        if len(self.systems):
            for id in event.data['Stellar Orbits']:
                orbit_data = event.data['Stellar Orbits'][id]
                a = orbit_data['a']
                e = orbit_data['e']
                i = orbit_data['i']
                system = [s for s in self.systems if s.id == orbit_data['astrobody']][0]
                systems = Universe.nei().true_systems
                sstm = [s for s in systems if s.id == orbit_data['star_id']]
                if len(sstm):
                    sstm = sstm[0]
                system.set_orbit(sstm, (a, e, i))

    def select_one(self, btn):
        for button in self.system_buttons.widgets():
            button.deselect()
        btn.select()

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

        chosen = q(max(choices), 'earth_radius')
        vt = self.current.properties.get_widget(2)
        vt.text_area.set_value(chosen)
        vt.set_min_and_max(min_v=chosen.m)

    def update(self):
        neighbourhood = Universe.nei()
        idx = neighbourhood.current_planetary.id if neighbourhood is not None else self.last_id
        if idx != self.last_id:
            self.last_id = idx
            if self.last_id not in self.primary_planets:
                self.primary_planets[self.last_id] = []

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


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

    def destroy(self):
        self.parent.del_button(self.current)
        self.erase()

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                star = Universe.nei().current_planetary.parent.star
                self.current = PlanetaryPTypeSystem(star, *self.get_determinants())
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep', 'min_sep']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            self.parent.setup_button.enable()


class PotentialPlanet(ListedBody):
    # Because it has the "potential" to form a double planet system.

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.parent.current.set_bodies(self.object_data)
            self.parent.parent.create_buttons(self.object_data)
            self.parent.remove_listed(self)
            self.kill()
            self.parent.sort()


class AvailablePlanets(ListedArea):
    name = 'Planets'
    listed_type = PotentialPlanet
    excluded = None

    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self.excluded = []
        EventHandler.register(self.exclude, 'ExcludePlanet')

    def exclude(self, event):
        """Excludes planets that already have satellites to form double-planet systems"""
        for planet_id in event.data['planets']:
            if planet_id not in self.excluded:
                self.excluded.append(planet_id)

    def show(self):
        neighbourhood = Universe.nei()
        if neighbourhood is not None:
            for system in neighbourhood.get_p_systems():
                idx = system.id
                planets = [p for p in system.planets if p.id not in self.excluded]
                self.populate(planets, layer=idx)
                self.parent.populate(*system.planets, layer=idx)
        super().show()


class CreatedPlanet(ColoredBody):
    enabled = True

    def disable(self):
        self.enabled = False

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
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
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.current.unset_planets()
            self.disable()


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.planets_area.unlock()
            sistema = self.parent.current.current
            self.parent.create_system_button(sistema)
            self.parent.current.erase()
            self.disable()


class DissolveSystemsButton(DissolveButton):

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            system = self.parent.current.current
            Universe.current_planetary().remove_astro_obj(system)
            self.parent.planets_area.show()
            self.parent.current.destroy()

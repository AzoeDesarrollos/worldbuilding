from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_SELECTED, COLOR_TEXTO
from .common import AvailableObjects, AvailablePlanet, ModifyArea, TextButton, ToggleableButton
from engine.equations.orbit import PseudoOrbit, RawOrbit, from_planetary_resonance
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.globales import WidgetHandler, WidgetGroup
from engine.frontend.widgets.basewidget import BaseWidget
from .stellar_orbit_panel import OrbitType, RatioDigit
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets.meta import Meta
from pygame import Surface, Rect
from itertools import cycle
from engine import q, roll


class PlanetaryOrbitPanel(BaseWidget):
    skippable = True
    skip = False
    current = None
    markers = None

    curr_digit = 0
    selected_marker = None

    curr_x = 0
    curr_y = 0

    added = None
    visible_markers = True

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Planetary Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.buttons = WidgetGroup()
        self.orbit_descriptions = WidgetGroup()
        self._markers = {}
        self.markers = []
        self.added = []
        self.objects = []
        self._loaded_orbits = []
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 58, 380, 20 * 16)
        self.curr_x = self.area_buttons.x + 3
        self.curr_y = self.area_buttons.y + 21
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.add_orbits_button = SetOrbitButton(self, ANCHO - 94, 394)
        self.area_modify = ModifyArea(self, ANCHO - 201, 374)
        self.show_markers_button = ToggleableButton(self, 'Satellites', self.toggle_stellar_orbits, 3, 421)
        self.show_markers_button.disable()
        self.resonances_button = AddResonanceButton(self, ANCHO - 140, 416)
        self.order_f = self.crear_fuente(14)
        self.write(self.name + ' Panel', self.crear_fuente(16, underline=True), centerx=(ANCHO // 4) * 1.5, y=0)
        self.digit_x = RatioDigit(self, 'x', self.resonances_button.rect.left - 60, self.resonances_button.rect.y)
        self.write(':', self.crear_fuente(16), topleft=[self.digit_x.rect.right + 1, self.resonances_button.rect.y - 1])
        self.digit_y = RatioDigit(self, 'y', self.digit_x.rect.right + 9, self.resonances_button.rect.y)
        self.ratios = [self.digit_x, self.digit_y]
        self.cycler = cycle(self.ratios)
        next(self.cycler)

        self.properties.add(self.area_modify, self.show_markers_button, self.digit_x, self.digit_y,
                            self.planet_area, self.add_orbits_button, self.resonances_button,
                            layer=2)

        EventHandler.register(self.save_orbits, 'Save')
        EventHandler.register(self.load_orbits, 'LoadData')

    def load_orbits(self, event):
        for position in event.data.get('Planetary Orbits', []):
            if position not in self._loaded_orbits:
                self._loaded_orbits.append(position)

    def set_loaded_orbits(self):
        for orbit_data in self._loaded_orbits:
            a = q(orbit_data['a'], 'earth_radius')
            e = q(orbit_data['e'])
            i = q(orbit_data['i'], 'degree')
            system = Systems.get_system_by_id(orbit_data['star_id'])
            planet = system.get_astrobody_by(orbit_data['planet_id'], tag_type='id')
            satellite = system.get_astrobody_by(orbit_data['astrobody'], tag_type='id')
            orbit = satellite.set_orbit(planet, [a, e, i])
            # self.add_orbit_marker(planet.orbit)
            # self.planet_area.delete_objects(planet)

        # borrar las órbitas cargadas para evitar que se dupliquen.
        self._loaded_orbits.clear()

    def save_orbits(self, event):
        orbits = self._loaded_orbits
        for planet_obj in self.planet_area.listed_objects.widgets():
            planet = planet_obj.object_data
            for marker in self._markers.get(planet.id, []):
                if marker.orbit is not None:
                    d = self.create_save_data(marker.orbit)
                    orbits.append(d)

        EventHandler.trigger(event.tipo + 'Data', 'Orbit', {'Planetary Orbits': orbits})

    @staticmethod
    def create_save_data(orb):
        d = {}
        if hasattr(orb, 'semi_major_axis'):
            d['a'] = round(orb.semi_major_axis.m, 2)
        if hasattr(orb, 'inclination'):
            d['i'] = orb.inclination.m
        if hasattr(orb, 'eccentricity'):
            d['e'] = orb.eccentricity.m
        if hasattr(orb, 'astrobody'):
            d['astrobody'] = orb.astrobody.id
            d['planet_id'] = orb.astrobody.parent.id
            d['star_id'] = orb.astrobody.parent.parent.id
            d['name'] = orb.astrobody.name
        return d

    def toggle_stellar_orbits(self):
        if self.visible_markers:
            self.area_modify.color_alert()
            self.add_orbits_button.disable()
            for marker in self.markers:
                marker.hide()
        else:
            self.hide_orbit_types()
            for marker in self.markers:
                marker.show()
            self.show_markers_button.disable()
            self.add_orbits_button.enable()
            self.area_modify.color_standby()
        self.visible_markers = not self.visible_markers
        self.area_modify.visible_markers = self.visible_markers

    def hide_orbit_types(self):
        for orbit_type in self.orbit_descriptions.widgets():
            orbit_type.hide()
        for orbit_button in self.buttons.widgets():
            orbit_button.enable()

    def populate(self):
        planet = self.current
        if planet.id not in self._markers:
            self._markers[planet.id] = []
        self.markers = self._markers[planet.id]
        for marker in self.markers:
            marker.show()

        if not len(self.markers):
            x = Marker(self, 'Hill Sphere', planet.hill_sphere)
            x.locked = True
            self.markers.append(x)
            self.properties.add(x, layer=2)
        self.sort_markers()

    def add_objects(self):
        system = Systems.get_current()
        if system is not None:
            for obj in system.satellites + system.asteroids:
                if obj not in self.objects:
                    self.objects.append(obj)
                    btn = ObjectButton(self, obj, self.curr_x, self.curr_y)
                    self.buttons.add(btn, layer=Systems.get_current_idx())
                    self.properties.add(btn)
            self.sort_buttons()

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()
        self.add_objects()
        self.set_loaded_orbits()

    def hide(self):
        super().hide()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.hide()

    def select_planet(self, planet):
        if planet is not self.current:
            self.hide_everything()
            self.current = planet
            self.populate()
        for button in self.buttons.widgets():
            button.enable()

    def anchor_maker(self, marker):
        self.area_modify.link(marker)
        self.area_modify.visible_markers = True
        self.add_orbits_button.link(marker)
        self.add_orbits_button.enable()
        self.selected_marker = marker

    def deselect_markers(self, m):
        for marker in self.markers:
            marker.deselect()
            marker.enable()
        m.select()

    def sort_markers(self):
        self.markers.sort(key=lambda m: m.value.m)
        for i, marker in enumerate(self.markers, start=1):
            marker.rect.y = i * 2 * 10 + 38
            if not self.area_markers.contains(marker.rect):
                marker.hide()
            else:
                marker.show()

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.buttons.get_widgets_from_layer(Systems.get_current_idx()):
            bt.move(x, y)
            if not self.area_buttons.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def create_roches_marker(self, obj):
        obj_density = obj.density.to('earth_density').m
        roches = self.current.set_roche(obj_density)
        roches_marker = Marker(self, "Roche's Limit", roches, lock=True)
        first = self.markers[0]
        if first.name == "Roche's Limit":
            self.properties.remove(first)
            self.markers[0] = roches_marker
        else:
            self.markers.append(roches_marker)
        self.properties.add(roches_marker, layer=2)
        return roches

    def add_new(self, obj):
        if obj not in self.added:
            self.added.append(obj)
        obj_name = obj.cls
        pln_habitable = Systems.get_current().is_habitable(self.current)
        pln_hill = self.current.hill_sphere.m
        obj_type = obj.celestial_type
        roches = self.create_roches_marker(obj)

        text = "A satellite's mass must be less than or equal to the\nmass of the planet."
        text += '\n\nConsider using a less massive satellite for this planet.'
        assert self.current.mass.to('earth_mass').m >= obj.mass.to('earth_mass').m, text

        pos = q(round(roll(self.current.roches_limit.m, self.current.hill_sphere.m / 2), 3), 'earth_radius')
        orbit = RawOrbit(Systems.get_current_star(), pos)
        obj_marker = Marker(self, obj_name, pos, color=COLOR_SELECTED, lock=False)

        max_value = pln_hill
        if pln_habitable and obj_type != 'asteroid':
            max_value /= 2
        obj_marker.set_max_value(max_value)
        obj_marker.set_min_value(roches.m)
        obj_marker.links(orbit, obj)

        self.markers.append(obj_marker)
        self.properties.add(obj_marker, layer=2)
        self.sort_markers()

        return orbit, obj_marker

    def hide_everything(self):
        for marker in self.markers:
            if marker.linked_button is not None:
                marker.linked_button.hide_info()
            marker.hide()
        self.visible_markers = False
        self.show_markers_button.disable()
        for button in self.buttons.widgets():
            if button.completed:
                button.disable()

    def is_added(self, obj):
        return obj in self.added

    def create_complete_button(self, obj):
        pass

    def link_satellite_to_planet(self, marker):
        marker._orbit = PseudoOrbit(marker.orbit)
        button = marker.linked_button
        self.hide_everything()
        button.update_text(marker.orbit.a)
        button.info.link_marker(marker)
        button.info.locked = False
        button.info.show()

    def notify(self):
        self.planet_area.listed_objects.empty()
        if not self.visible_markers:
            self.show_markers_button.enable()
            for button in self.buttons.widgets():
                button.disable()

    def get_sorted_satellites(self):
        self.sort_markers()
        markers = [marker.obj for marker in self.markers if marker.obj is not None]
        return markers

    def set_current_digit(self, idx):
        self.curr_digit = self.ratios.index(idx)

    def cycle(self):
        has_values = False
        for ratio in self.ratios:
            ratio.deselect()
            has_values = ratio.value != ''

        valid = has_values and self.selected_marker is not None

        if valid:
            self.resonances_button.enable()
        else:
            ratio = next(self.cycler)
            ratio.select()
            WidgetHandler.set_origin(ratio)

    def ratios_to_string(self):
        x = int(self.digit_x.value)
        y = int(self.digit_y.value)
        diff = y - x if y > x else x - y
        self.write('{}° Order'.format(diff), self.order_f, right=self.digit_x.rect.left - 2, y=self.digit_x.rect.y)
        return '{}:{}'.format(x, y)

    def clear_ratios(self):
        self.digit_x.clear()
        self.digit_y.clear()


class OrbitableObject(AvailablePlanet):
    def on_mousebuttondown(self, event):
        self.parent.parent.select_planet(self.object_data)


class AvailablePlanets(AvailableObjects):
    listed_type = OrbitableObject

    def show(self):
        system = Systems.get_current()
        if system is not None:
            bodies = [body for body in system.astro_bodies if body.hill_sphere != 0]
            if not len(self.listed_objects.get_widgets_from_layer(Systems.get_current_idx())):
                self.populate(bodies)
        super().show()


class ObjectButton(Meta):
    enabled = False
    info = None
    linked_marker = None
    completed = False

    def __init__(self, parent, obj, x, y):
        super().__init__(parent)
        self.object_data = obj
        self.orbit_data = None
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.color = obj.color
        self.img_uns = self.f1.render(obj.cls, True, self.color, COLOR_AREA)
        self.img_sel = self.f2.render(obj.cls, True, self.color, COLOR_AREA)
        self.img_dis = self.img_uns
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_text(self, orbit):
        self.completed = True
        obj: str = self.object_data.title + ' @{:~}'.format(orbit)
        self.img_uns = self.f1.render(obj, True, self.color, COLOR_AREA)
        self.img_sel = self.f2.render(obj, True, self.color, COLOR_AREA)
        self.img_dis = self.img_uns
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect.size = self.image.get_size()
        self.info = OrbitType(self.parent)
        self.info.link_astrobody(self.object_data)
        self.parent.orbit_descriptions.add(self.info)
        self.parent.sort_buttons()

    def on_mousebuttondown(self, event):
        if self.enabled:
            if not self.parent.is_added(self.object_data) and self.parent.current is not None:
                orbit, marker = self.parent.add_new(self.object_data)
                self.create_type(orbit)
                self.link_marker(marker)
            else:
                self.parent.toggle_stellar_orbits()
                self.parent.show_markers_button.enable()
                self.info.link_marker(self.linked_marker)
                self.info.show()
                self.disable()

    def move(self, x, y):
        self.rect.topleft = x, y

    def create_type(self, info):
        self.orbit_data = PseudoOrbit(info)

    def link_marker(self, marker):
        self.linked_marker = marker
        marker.linked_button = self

    def hide_info(self):
        if self.info is not None:
            self.info.hide()


class Marker(Meta, IncrementalValue):
    locked = True
    enabled = True
    text = ''
    color = COLOR_TEXTO
    max_value = None
    min_value = None

    _orbit = None
    obj = None

    linked_button = None

    def __init__(self, parent, name, value, color=None, lock=True):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.name = name
        self._value = value
        self.unit = value.u

        if not lock:
            self.locked = False
            self.color = color
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)
        self.show()

    def set_max_value(self, value):
        self.max_value = value

    def set_min_value(self, value):
        self.min_value = value

    @property
    def orbit(self):
        return self._orbit

    @orbit.setter
    def orbit(self, orbit):
        self._orbit = orbit
        self.parent.notify()

    @property
    def value(self):
        if self.orbit is not None:
            return round(self._orbit.semi_major_axis, 3)
        else:
            return self._value

    @value.setter
    def value(self, new_value):
        if self._orbit is not None:
            self._orbit.semi_major_axis = new_value

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if not self.locked:
                self.parent.deselect_markers(self)
                self.parent.anchor_maker(self)

        return self

    def tune_value(self, delta):
        if not self.locked:
            self.increment = self.update_increment()
            self.increment *= delta
            ta = 'Regular satellites must orbit close to their planet, that is within half of the maximun value.'
            ta += '\n\nTry moving the satellite to a lower orbit.'

            tb = "A satellite cannot orbit beyond it's main body's Hill Sphere."
            tc = "A satellite cannot orbit below it's main body's Roche's limit."
            test_a = self.value.m + self.increment > self.min_value
            test_b = self.value.m + self.increment < self.max_value
            if self.obj.celestial_type == 'satellite':
                assert test_b, ta
            assert test_a, tc
            assert test_b, tb

            self.value += q(self.increment, self.value.u)
            self.increment = 0
            self.parent.sort_markers()

    def set_value(self, new_value):
        self.value = q(new_value.m, self.value.u)
        self.parent.sort_markers()

    def update(self):
        self.reset_power()
        self.text = '{:~}'.format(round(self.value, 3))
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        super().update()
        if self.selected:
            self.image = self.img_sel

    def links(self, orbit, obj):
        self.orbit = orbit
        self.obj = obj


class SetOrbitButton(TextButton):
    linked_marker = None

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set Orbit', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.link_satellite_to_planet(self.linked_marker)

    def link(self, marker):
        self.linked_marker = marker


class AddResonanceButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Resonance', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            assert self.parent.selected_marker.obj is not None, "The orbit is empty."
            satellite = self.parent.selected_marker.obj
            planet = self.parent.current
            position = from_planetary_resonance(planet, satellite, self.parent.ratios_to_string())
            print(position)
            self.disable()
            self.parent.clear_ratios()

    def enable(self):
        super().enable()
        self.parent.image.fill(COLOR_BOX, [325, 396, 63, 18])

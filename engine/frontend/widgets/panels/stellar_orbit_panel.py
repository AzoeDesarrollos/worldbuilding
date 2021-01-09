from .common import TextButton, Meta, AvailableObjects, ToggleableButton, AvailablePlanet
from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, COLOR_AREA, COLOR_DISABLED
from engine.frontend.globales import Renderer, WidgetHandler, ANCHO, ALTO
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.globales import COLOR_SELECTED, COLOR_STARORBIT
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.orbit import RawOrbit, PseudoOrbit
from engine.frontend.globales.group import WidgetGroup
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from pygame import Surface, Rect
from engine.backend import roll
from ..values import ValueText
from engine import q


class OrbitPanel(BaseWidget):
    current = None  # ahora será la estrella o sistema seleccionado.
    curr_idx = None  # ahora será el layer de self.Buttons.

    last_idx = 0
    _loaded_orbits = None

    offset = 0
    curr_x, curr_y = 3, 442

    visible_markers = True
    orbits = None
    markers = None
    buttons = None

    skippable = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 58, 380, 20 * 16)
        self.area_scroll = Rect(3, 32, 387, 388)
        self.area_modify = ModifyArea(self, ANCHO - 200, 399)
        self.properties.add(self.area_modify, layer=2)

        self.f = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', self.f, centerx=(ANCHO // 4) * 1.5, y=0)

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 350)
        self.properties.add(self.planet_area, layer=2)

        self._orbits = {}
        self._loaded_orbits = []
        self._buttons = WidgetGroup()
        self.indexes = []
        self._markers = {}
        self.orbit_descriptions = WidgetGroup()
        self.show_markers_button = ToggleableButton(self, 'Stellar Orbits', self.toggle_stellar_orbits, 3, 421)
        self.properties.add(self.show_markers_button, layer=2)
        self.show_markers_button.disable()

        self.add_orbits_button = AddOrbitButton(self, ANCHO - 100, 416)
        self.properties.add(self.add_orbits_button, layer=2)
        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.save_orbits, 'Save')
        EventHandler.register(self.load_orbits, 'LoadData')

    def set_current(self):
        self.toggle_current_markers_and_buttons(False)
        star = Systems.get_current_star()
        if star not in self._markers:
            self._markers[star] = []
            self._orbits[star] = []
            self.indexes.append(star)

        self.current = star
        self.curr_idx = self.indexes.index(star)
        self.orbits = self._orbits[star]
        self.markers = self._markers[star]
        self.buttons = self._buttons.get_widgets_from_layer(self.curr_idx)
        if not len(self.markers):
            self.populate()
        else:
            self.toggle_current_markers_and_buttons(True)
        self.add_orbits_button.enable()
        self.visible_markers = False
        self.toggle_stellar_orbits()

    def populate(self):
        star = self.current
        markers = {'Inner Boundary': star.inner_boundry,
                   'Habitable Inner': star.habitable_inner,
                   'Habitable Outer': star.habitable_outer,
                   'Frost Line': star.frost_line,
                   'Outer Boundary': star.outer_boundry}

        for i, marker in enumerate(markers, start=1):
            x = OrbitMarker(self, marker, star, markers[marker])
            x.locked = True
            self.markers.append(x)
            self.properties.add(x, layer=2)
        self.sort_markers()

    def toggle_current_markers_and_buttons(self, toggle: bool):
        if self.markers is not None:
            for marker in self.markers:
                marker.toggle(toggle)
        if self.buttons is not None:
            for button in self.buttons:
                button.toggle(toggle)

    def add_orbit_marker(self, position):
        star = self.current
        inner = star.inner_boundry
        outer = star.outer_boundry
        if type(position) is q:
            bool_a = True
            bool_b = False
            test = inner < position < outer
            color = COLOR_TEXTO
        else:  # type(position) is PlanetOrbit
            bool_a = False
            bool_b = True
            test = inner < position.semi_major_axis < outer
            color = COLOR_STARORBIT

        if test is True:
            new = OrbitMarker(self, 'Orbit', star, position, is_orbit=bool_a, is_complete_orbit=bool_b)
            self.markers.append(new)
            self.orbits.append(new)
            self.sort_markers()
            self.add_button_and_type(new, color)
            self.properties.add(new, layer=2)
            return True
        return False

    def add_button_and_type(self, marker, color):
        orbit_type = OrbitType(self)
        button = OrbitButton(self, color)
        self._buttons.add(button, layer=self.curr_idx)
        self.buttons = self._buttons.get_widgets_from_layer(self.curr_idx)

        # Buttons, OrbitTypes and Markers are all Intertwined.
        orbit_type.intertwine(m=marker, b=button)
        button.intertwine(m=marker, o=orbit_type)
        marker.intertwine(o=orbit_type, b=button)

        self.orbit_descriptions.add(orbit_type)
        self.sort_buttons()
        self.properties.add(button, layer=2)
        self.properties.add(orbit_type, layer=3)
        button.enable()
        button.show()

    def sort_markers(self):
        self.markers.sort(key=lambda m: m.value)
        for i, marker in enumerate(self.markers, start=1):
            marker.rect.y = i * 2 * 10 + 38 + self.offset
            if not self.area_markers.contains(marker.rect):
                marker.hide()
            else:
                marker.show()

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in sorted(self.buttons, key=lambda b: b.get_value().m):
            bt.move(x, y)
            if not self.area_buttons.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 15 < self.rect.w - bt.rect.w + 15:
                x += bt.rect.w + 15
            else:
                x = 3
                y += 32

    def delete_marker(self, marker):
        """
        :type marker: OrbitMarker
        """
        if not marker.locked:
            marker.kill()
            marker.linked_type.kill()
            marker.linked_button.kill()
            if marker is self.area_modify.marker:
                self.area_modify.unlink()
            idx = self.markers.index(marker)
            del self.markers[idx]
            self.buttons.remove(marker.linked_button)
            self.sort_markers()
            self.sort_buttons()

    def on_mousebuttondown(self, event):

        if self.area_scroll.collidepoint(event.pos):
            last_is_hidden = not self.markers[-1].is_visible
            if len(self.markers) > 16 and event.button in (4, 5):
                if event.button == 4 and self.offset < 0:
                    self.offset += 20
                elif event.button == 5 and last_is_hidden:
                    self.offset -= 20

                self.sort_markers()

        elif self.area_buttons.collidepoint(event.pos) and self.buttons is not None and len(self.buttons):
            self.buttons.sort(key=lambda b: b.get_value().m)
            last_is_hidden = not self.buttons[-1].is_visible
            first_is_hidden = not self.buttons[0].is_visible
            if event.button == 4 and first_is_hidden:
                self.curr_y += 32
            elif event.button == 5 and last_is_hidden:
                self.curr_y -= 32
            self.sort_buttons()

        elif event.button == 1 and self.markers is not None:
            for marker in self.markers:
                marker.deselect()
                marker.enable()

    def check_orbits(self):
        self.orbits.sort(key=lambda o: o.value.m)
        for x, p in enumerate(self.orbits[1:], start=1):
            a = self.orbits[x - 1].value.m if x > 0 and len(self.orbits) else self.orbits[0].value.m  # el anterior
            assert a + 0.15 < p.value.m, 'Orbit @' + str(p.value.m) + ' is too close to Orbit @' + str(a)

            if x + 1 < len(self.orbits):
                b = self.orbits[x + 1].value.m  # el posterior
                assert p.value.m < b - 0.15, 'Orbit @' + str(p.value.m) + ' is too close to Orbit @' + str(b)

    def anchor_maker(self, marker):
        self.area_modify.link(marker)

    def clear(self, event):
        if event.data['panel'] is self:
            for marker in self.markers:
                marker.kill()
            for orbit in self.buttons:
                orbit.kill()
            self.markers.clear()

    def save_orbits(self, event):
        orbits = []
        for system in Systems.get_systems():
            for star in system:
                for marker in self._orbits[star]:
                    orb = marker.orbit
                    d = {}
                    if hasattr(orb, 'semi_major_axis'):
                        d['a'] = round(orb.semi_major_axis.m, 2)
                    if hasattr(orb, 'inclination'):
                        d['i'] = orb.inclination.m
                    if hasattr(orb, 'eccentricity'):
                        d['e'] = orb.eccentricity.m
                    if hasattr(orb, 'planet'):
                        d['planet'] = orb.planet.name
                        d['star_id'] = orb.planet.orbit.star.id
                    orbits.append(d)

        EventHandler.trigger(event.tipo + 'Data', 'Orbit', {'Orbits': orbits})

    def load_orbits(self, event):
        for position in event.data.get('Orbits', []):
            self._loaded_orbits.append(position)

    def set_loaded_orbits(self):
        for orbit_data in self._loaded_orbits:
            a = q(orbit_data['a'], 'au')
            if 'e' not in orbit_data:
                self.add_orbit_marker(a)
            else:
                e = q(orbit_data['e'])
                i = q(orbit_data['i'], 'degree')
                system = Systems.get_system_by_id(orbit_data['star_id'])
                planet = system.get_planet_by_name(orbit_data['planet'])
                star = system.star_system
                planet.set_orbit(star, [a, e, i])
                self.add_orbit_marker(planet.orbit)
                self.planet_area.delete_objects(planet)

        # borrar las órbitas cargadas para evitar que se dupliquen.
        self._loaded_orbits.clear()

    def show(self):
        self.set_current()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()
        self.visible_markers = True
        if len(self._loaded_orbits):
            self.set_loaded_orbits()
        self.show_markers_button.show()

        super().show()

    def hide(self):
        super().hide()
        for item in self.properties.widgets():
            item.hide()

    def toggle_stellar_orbits(self):
        if self.visible_markers:
            self.area_modify.color_alert()
            self.add_orbits_button.disable()
            for marker in self.markers:
                marker.hide()
        else:
            for marker in self.markers:
                marker.show()
            self.hide_orbit_types()
            self.show_markers_button.disable()
            self.add_orbits_button.enable()
            self.area_modify.color_standby()
        self.visible_markers = not self.visible_markers

    def hide_orbit_types(self):
        for orbit_type in self.orbit_descriptions.widgets():
            orbit_type.hide()
        for orbit_button in self.buttons:
            orbit_button.unlock()

    def deselect_markers(self, m):
        for marker in self.markers:
            marker.deselect()
            marker.enable()
        m.select()

    def link_planet_to_orbit(self, planet):
        locked = [i for i in self.buttons if i.locked]
        if len(locked):
            orbit = PseudoOrbit(locked[0].linked_marker.orbit)
            locked[0].linked_marker.orbit = orbit
            locked[0].linked_type.show()
            locked[0].linked_type.link_planet(planet)
            self.add_orbits_button.disable()

    def update(self):
        super().update()
        idx = Systems.get_current_idx()
        if idx != self.last_idx:
            self.set_current()
            self.last_idx = idx

        self.image.fill(COLOR_BOX, self.area_markers)

    def __repr__(self):
        return 'Orbit Panel'


class Intertwined:
    linked_type = None
    linked_button = None
    linked_marker = None

    def link_type(self, orbit_type):
        """
        @type orbit_type: OrbitType
        """
        self.linked_type = orbit_type

    def link_button(self, button):
        """
        @type button: OrbitButton
        """
        self.linked_button = button

    def link_marker(self, marker):
        """
        @type marker: OrbitMarker
        """
        self.linked_marker = marker

    def intertwine(self, m=None, o=None, b=None):
        if isinstance(self, OrbitMarker):
            self.link_button(b)
            self.link_type(o)

        elif isinstance(self, OrbitType):
            self.link_button(b)
            self.link_marker(m)

        elif isinstance(self, OrbitButton):
            self.link_marker(m)
            self.link_type(o)

    def show(self):
        return NotImplemented

    def hide(self):
        return NotImplemented

    def toggle(self, value: bool):
        if value is True:
            self.show()
        else:
            self.hide()


class OrbitType(BaseWidget, Intertwined):
    linked_planet = None
    locked = True

    modifiable = False
    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()

    def link_planet(self, planet):
        self.linked_planet = planet
        self.locked = False

    def create(self):
        orbit = self.linked_marker.orbit
        self.clear()
        props = ['Semi-major Axis', 'Semi-minor Axis', 'Eccentricity', 'Inclination',
                 'Periapsis', 'Apoapsis', 'Orbital motion', 'Temperature', 'Orbital velocity', 'Orbital period',
                 'Argument of periapsis', 'Longuitude of the ascending node', 'Planet']
        attr = ['semi_major_axis', 'semi_minor_axis', 'eccentricity', 'inclination',
                'periapsis', 'apoapsis', 'motion', 'temperature', 'velocity', 'period',
                'argument_of_periapsis', 'longuitude_of_the_ascending_node', 'planet']
        for i, prop in enumerate([j for j in attr if hasattr(orbit, j)]):
            value = getattr(orbit, prop)
            vt = ValueText(self, props[attr.index(prop)], 3, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            vt.value = value
            self.properties.add(vt)

    def fill(self):
        parametros = []
        for elemento in self.properties.widgets():
            if elemento.text == 'Inclination':
                value = q(0 if elemento.text_area.value == '' else elemento.text_area.value, 'degree')
            elif elemento.text not in ['Orbital motion', 'Temperature']:
                value = q(elemento.text_area.value)
            else:
                value = 'au'
            parametros.append(value)
        star = self.parent.current
        orbit = self.linked_planet.set_orbit(star, parametros)
        self.linked_marker.orbit = orbit
        self.show()
        self.parent.planet_area.delete_objects(self.linked_planet)
        # self.locked = True
        self.has_values = True

    def clear(self):
        for prop in self.properties.widgets():
            prop.kill()
            prop.text_area.kill()

    def show(self):
        self.create()

        for p in self.properties.widgets():
            p.show()

    def hide(self):
        self.clear()

    def elevate_changes(self, key, new_value):
        # a hook to prevent errors
        pass


class OrbitMarker(Meta, BaseWidget, IncrementalValue, Intertwined):
    enabled = True
    name = ''
    color = None

    locked = False
    orbit = None

    def __init__(self, parent, name, star, value, is_orbit=False, is_complete_orbit=False):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.star = star
        self.name = name
        self._value = value
        if is_orbit:
            self.orbit = RawOrbit(self.parent.current, round(value, 3))
            self.text = '{:~}'.format(value)
            self.color = COLOR_SELECTED
        elif is_complete_orbit:
            self.orbit = value
            self.text = '{:~}'.format(value.a)
            self.color = COLOR_SELECTED
        else:
            self.color = COLOR_TEXTO
            self.text = '{:~}'.format(value)
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)
        EventHandler.register(self.key_to_mouse, 'Arrow')
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    @property
    def value(self):
        if self.orbit is not None:
            return round(self.orbit.semi_major_axis, 3)
        else:
            return self._value

    @value.setter
    def value(self, new_value):
        if self.orbit is not None:
            self.orbit.semi_major_axis = new_value

    def disable(self):
        self.enabled = False

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if not self.locked:
                self.parent.deselect_markers(self)
                self.parent.anchor_maker(self)

        elif event.button == 3:
            self.parent.delete_marker(self)

        return self

    def tune_value(self, delta):
        if not self.locked:
            self.increment = self.update_increment()
            self.increment *= delta

            if self.value.m + self.increment >= 0:
                self.value += q(self.increment, self.value.u)
                self.increment = 0
                self.parent.sort_markers()

    def key_to_mouse(self, event):
        if event.origin == self:
            self.tune_value(event.data['delta'])

    def update(self):
        self.reset_power()
        self.text = '{:~}'.format(self.value)
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        super().update()
        if self.selected:
            self.image = self.img_sel

    def __repr__(self):
        return self.name + ' @' + self.text


class OrbitButton(Meta, BaseWidget, Intertwined):
    locked = False

    def __init__(self, parent, color):
        super().__init__(parent)
        self.f1 = self.crear_fuente(14)
        self.f2 = self.crear_fuente(14, bold=True)
        self._rect = Rect(3, 442, 0, 21)
        self.color = color

    def link_marker(self, marker):
        super().link_marker(marker)
        self.create()

    def get_value(self):
        return self.linked_marker.orbit.semi_major_axis

    def create(self):
        t = 'Orbit @{:~}'.format(round(self.get_value(), 3))
        self.img_uns = self.f1.render(t, True, self.color, COLOR_AREA)
        self.img_sel = self.f2.render(t, True, self.color, COLOR_AREA)
        self.img_dis = self.f1.render(t, True, COLOR_DISABLED, COLOR_AREA)
        self.image = self.img_uns
        self.rect = self.img_uns.get_rect(topleft=self._rect.topleft)

    def move(self, x, y):
        self._rect.topleft = x, y
        self.create()

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.parent.visible_markers:
                self.parent.toggle_stellar_orbits()
            self.parent.hide_orbit_types()
            self.parent.show_markers_button.enable()
            self.linked_type.show()
            self.lock()

    def update(self):
        if not self.locked:
            super().update()
            self.create()
            self.selected = False

    def __repr__(self):
        return 'B.Orbit @' + str(self.get_value())


class RoguePlanet(AvailablePlanet):
    # "rogue" because it doens't have an orbit yet
    def on_mousebuttondown(self, event):
        if not self.parent.parent.visible_markers:
            self.enabled = False
            self.parent.parent.link_planet_to_orbit(self.object_data)


class AvailablePlanets(AvailableObjects):
    listed_type = RoguePlanet
    name = 'Planets'


class AddOrbitButton(TextButton):
    value = 'Inward'
    anchor = None
    locked = False

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Orbit', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled and not self.locked:
            star = self.parent.current
            inner = star.inner_boundry
            outer = star.outer_boundry
            position = roll(inner, outer)
            self.parent.add_orbit_marker(position)
            self.parent.check_orbits()

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def unlink(self):
        self.lock()
        self.disable()


class ModifyArea(BaseWidget):
    marker = None

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((32, 20))
        self.unlink()
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        delta = 0
        if event.button == 4:
            delta = -1
        elif event.button == 5:
            delta = +1

        if self.marker is not None and self.parent.visible_markers:
            self.marker.tune_value(delta)

    def link(self, marker):
        self.marker = marker
        self.color_ready()

    def unlink(self):
        self.marker = None
        self.color_standby()

    def color_ready(self):
        self.image.fill((0, 255, 0), (1, 1, 30, 18))

    def color_standby(self):
        if self.marker is None:
            self.image.fill((255, 255, 0), (1, 1, 30, 18))
        else:
            self.color_ready()

    def color_alert(self):
        self.image.fill((255, 0, 0), (1, 1, 30, 18))

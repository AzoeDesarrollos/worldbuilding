from .common import TextButton, ListedArea, ToggleableButton, ColoredBody, ModifyArea
from engine.equations.orbit import RawOrbit, PseudoOrbit, from_stellar_resonance
from engine.frontend.globales import WidgetGroup, render_textrect, WidgetHandler
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.globales.constantes import *
from engine.frontend.widgets.meta import Meta
from engine import q, recomendation
from pygame import Surface, Rect
from engine.backend import roll
from ..values import ValueText
from itertools import cycle
from math import sqrt, pow
from bisect import bisect_left


class OrbitPanel(BaseWidget):
    current = None  # ahora será la estrella o sistema seleccionado.
    selected_marker = None

    last_idx = 0
    _loaded_orbits = None

    offset = 0
    curr_x, curr_y = 3, 442
    curr_digit = 0

    visible_markers = True
    orbits = None
    markers = None
    buttons = None

    skippable = False

    no_star_error = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 58, 380, 20 * 15)
        self.area_scroll = Rect(3, 32, 387, 388)
        self.area_modify = ModifyArea(self, ANCHO - 201, 374)

        self.f = self.crear_fuente(16, underline=True)
        self.f2 = self.crear_fuente(12)
        self.order_f = self.crear_fuente(14)
        self.write(self.name + ' Panel', self.f, centerx=(ANCHO // 4) * 1.5, y=0)
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.recomendation = Recomendation(self, 3, ALTO // 2 - 165)

        self._loaded_orbits = {}
        self.indexes = []

        self._orbits = {}
        self._buttons = {}
        self._markers = {}

        self.orbit_descriptions = WidgetGroup()
        self.show_markers_button = ToggleableButton(self, 'Stellar Orbits', self.toggle_stellar_orbits, 3, 421)
        self.show_markers_button.disable()
        self.add_orbits_button = AddOrbitButton(self, ANCHO - 94, 394)
        self.resonances_button = AddResonanceButton(self, ANCHO - 140, 416)

        self.digit_x = RatioDigit(self, 'x', self.resonances_button.rect.left - 60, self.resonances_button.rect.y)
        self.write(':', self.crear_fuente(16), topleft=[self.digit_x.rect.right + 1, self.resonances_button.rect.y - 1])
        self.digit_y = RatioDigit(self, 'y', self.digit_x.rect.right + 9, self.resonances_button.rect.y)
        self.ratios = [self.digit_x, self.digit_y]
        self.cycler = cycle(self.ratios)
        next(self.cycler)

        self.properties.add([self.area_modify, self.planet_area, self.show_markers_button,
                             self.add_orbits_button, self.resonances_button, self.digit_x,
                             self.digit_y], layer=2)
        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.save_orbits, 'Save')
        EventHandler.register(self.load_orbits, 'LoadData')

    def set_current(self):
        self.toggle_current_markers_and_buttons(False)
        star = Systems.get_current_star()
        self.current = star
        self.orbits: list = self._orbits[star.id]
        self.markers = self._markers[star.id]
        self.buttons = self._buttons[star.id]
        if self.is_visible:
            if star.evolution_id != star.id:
                self.depopulate()
            if not len(self.markers) or not self.markers[0].locked:
                self.populate()
            self.toggle_current_markers_and_buttons(True)
            self.sort_buttons()
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

        for marker in markers:
            x = OrbitMarker(self, marker, star, markers[marker])
            x.locked = True
            self._markers[star.id].append(x)
            self.properties.add(x, layer=4)

        if star.inner_forbbiden_zone is not None:
            markers = {
                'Inner Forbbiden Zone': star.inner_forbbiden_zone,
                'Outer Forbbiden Zone': star.outer_forbbiden_zone
            }
            for marker in markers:
                x = OrbitMarker(self, marker, star, markers[marker])
                x.locked = True
                self._markers[star.id].append(x)
                self.properties.add(x, layer=4)

        self.sort_markers()

    def depopulate(self):
        flagged = []
        star = self.current
        for marker in self._markers[star.id]:
            if marker.locked:
                flagged.append(marker)

        for each in flagged:
            self._markers[star.id].remove(each)
            self.properties.remove(each)
            each.kill()

    def toggle_current_markers_and_buttons(self, toggle: bool):
        if self.markers is not None:
            for marker in self.markers:
                marker.toggle(toggle)
        if self.buttons is not None:
            for button in self.buttons:
                button.toggle(toggle)

    def add_orbit_marker(self, position, resonance=False, res_parent=None, res_order=None):
        star = self.current if not hasattr(position, 'star') else position.star
        inner = star.inner_boundry
        outer = star.outer_boundry
        bc = False if resonance is False else True
        bd = None if resonance is False else []
        if type(position) is q:
            bb = False
        elif type(position) not in (RawOrbit, PseudoOrbit):
            bb = True
        else:
            bb = None

        test = False
        color = None
        if type(position) not in (q, RawOrbit, PseudoOrbit):
            test = True  # saved orbits are valid by definition
            color = COLOR_STARORBIT
        elif resonance is False:
            test = inner < position < outer
            color = COLOR_TEXTO
        elif resonance is True:
            bd = [res_parent, res_order]
            test = inner < position  # TNOs orbit well outside of 40AUs.
            color = (255, 0, 0)  # color provisorio

        if test is True:
            new = OrbitMarker(self, 'Orbit', star, position, is_complete_orbit=bb, is_resonance=bc, res=bd)
            self._markers[star.id].append(new)
            self._orbits[star.id].append(new)
            if self.is_visible:
                self.sort_markers()
            self.anchor_maker(new)
            self.add_button_and_type(star, new, color)
            self.properties.add(new, layer=4)
            return new

    def add_button_and_type(self, star, marker, color):
        orbit_type = OrbitType(self)
        button = OrbitButton(self, color)
        self._buttons[star.id].append(button)

        # Buttons, OrbitTypes and Markers are all Intertwined.
        orbit_type.intertwine(m=marker, b=button)
        button.intertwine(m=marker, o=orbit_type)
        marker.intertwine(o=orbit_type, b=button)

        self.orbit_descriptions.add(orbit_type)
        if len(self.buttons) and self.is_visible:
            self.sort_buttons()
        self.properties.add(button, layer=4)
        self.properties.add(orbit_type, layer=4)
        button.enable()

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
            self._orbits[marker.orbit.star.id].remove(marker)
            self.buttons.remove(marker.linked_button)
            marker.orbit.astrobody.unset_orbit()
            self.planet_area.show()
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

    def check_artifexian(self, orbit):
        self.orbits.sort(key=lambda o: o.value.m)
        idx = bisect_left(self.orbits, orbit)
        left, right = None, None
        text1, text2 = '', ''
        frost_line = None
        if 0 < idx < len(self.orbits) - 1:
            left = self.orbits[idx - 1].value.m
            right = self.orbits[idx + 1].value.m
        elif len(self.orbits) == 1:
            frost_line = self.current.frost_line.m
            left = frost_line if orbit.value.m < frost_line else None
            right = frost_line if orbit.value.m > frost_line else None
        elif idx == 0:
            right = self.orbits[idx + 1].value.m
        else:
            left = self.orbits[idx - 1].value.m

        self.image.fill(COLOR_BOX, [0, 420 - 30, self.rect.w, 30])
        if left is not None:
            if frost_line is None:
                value = orbit.value.m / left
                text1 = str(round(value, 3)) + " !" if not 1.4 <= value <= 2 else str(round(value, 3))
            else:
                value = abs(left - orbit.value.m)
                text1 = str(round(value, 3)) + " !" if not 1 <= value <= 1.2 else str(round(value, 3))

        if right is not None:
            if frost_line is None:
                value = right / orbit.value.m
                text2 = str(round(value, 3)) + " !" if not 1.4 <= value <= 2 else str(round(value, 3))
            else:
                value = abs(orbit.value.m - right)
                text2 = str(round(value, 3)) + " !" if not 1 <= value <= 1.2 else str(round(value, 3))

        if left and not right:
            self.write('top ' + text1, self.f2, top=420 - 15)
        elif left and right:
            self.write('top ' + text1, self.f2, bottom=420 - 15)
            self.write('bottom ' + text2, self.f2, top=420 - 15)
        else:  # just right
            self.write('bottom ' + text2, self.f2, top=420 - 15)

    def anchor_maker(self, marker):
        self.deselect_markers(marker)
        self.area_modify.link(marker)
        self.selected_marker = marker

    def clear(self, event):
        if event.data['panel'] is self:
            for marker in self.markers:
                marker.kill()
            for orbit in self.buttons:
                orbit.kill()
            self.markers.clear()
            self.clear_ratios()

    def save_orbits(self, event):
        for system in Systems.get_systems():
            if system.star_system.letter == 'S':
                for star in system:
                    for marker in self._orbits.get(star.id, []):
                        astrobody_id = marker.orbit.astrobody.id
                        d = self.create_save_data(marker.orbit)
                        self._loaded_orbits[astrobody_id] = d
            else:
                star = system.star_system
                for marker in self._orbits.get(star.id, []):
                    d = self.create_save_data(marker.orbit)
                    if not isinstance(marker.orbit, (RawOrbit, PseudoOrbit)):
                        astrobody_id = marker.orbit.astrobody.id
                        if astrobody_id not in self._loaded_orbits:
                            self._loaded_orbits[astrobody_id] = d

        EventHandler.trigger(event.tipo + 'Data', 'Orbit', {'Stellar Orbits': self._loaded_orbits})
        # self._loaded_orbits.clear()

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
            d['star_id'] = orb.astrobody.orbit.star.id
        if hasattr(orb, 'longitude_of_the_ascending_node'):
            d['LoAN'] = orb.longitude_of_the_ascending_node.m
        if hasattr(orb, 'argument_of_periapsis'):
            aop = orb.argument_of_periapsis
            d['AoP'] = aop.m if type(aop) is not str else aop
        return d

    def load_orbits(self, event):
        self.fill_indexes()
        self.set_current()
        existing_ids = [marker.orbit.id for marker in self.orbits]
        for id in event.data.get('Stellar Orbits', []):
            if id not in existing_ids:
                orbit_data = event.data['Stellar Orbits'][id]
                a = q(orbit_data['a'], 'au')
                if 'e' not in orbit_data:
                    self.add_orbit_marker(a)
                else:
                    e = q(orbit_data['e'])
                    i = q(orbit_data['i'], 'degree')
                    aop = q(orbit_data['AoP'], 'degree') if orbit_data['AoP'] != 'undefined' else 'undefined'
                    loan = q(orbit_data['LoAN'], 'degree')
                    system = Systems.get_system_by_id(orbit_data['star_id'])
                    if system is not None:
                        planet = system.get_astrobody_by(id, tag_type='id')
                        star = system.star_system
                        planet.set_orbit(star, [a, e, i, loan, aop])
                        planet.orbit.id = id
                        self.add_orbit_marker(planet.orbit)
                        self.planet_area.delete_objects(planet)

        # borrar las órbitas cargadas para evitar que se dupliquen.
        if self.is_visible:
            self.sort_markers()

    def fill_indexes(self):
        assert len(Systems.get_systems()), "There is no data to load"
        for system in Systems.get_systems():
            star = system.star_system
            if star.id not in self._markers:
                self._markers[star.id] = []
                self._orbits[star.id] = []
                self._buttons[star.id] = []
                self.indexes.append(star)

    def show(self):
        super().show()
        try:
            self.fill_indexes()
            self.set_current()
            self.no_star_error = False

        except AssertionError:
            self.no_star_error = True

        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()
        self.visible_markers = True
        self.show_markers_button.show()

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
        self.area_modify.visible_markers = self.visible_markers

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

    def link_astrobody_to_stellar_orbit(self, astrobody):
        locked = [i for i in self.buttons if i.locked]
        if len(locked):
            orbit = PseudoOrbit(locked[0].linked_marker.orbit)
            locked[0].linked_marker.orbit = orbit
            locked[0].linked_type.show()
            locked[0].linked_type.link_astrobody(astrobody)
            self.add_orbits_button.disable()
            self.recomendation.suggest(astrobody, orbit, Systems.get_current_star())
            self.recomendation.show_suggestion(astrobody, orbit.temperature)

    def update(self):
        system = Systems.get_current()
        if system is not None:
            idx = system.id
        else:
            idx = self.last_idx

        if idx != self.last_idx:
            self.set_current()
            self.last_idx = idx

        if not self.no_star_error:
            self.image.fill(COLOR_BOX, self.area_markers)
        else:
            self.show_no_system_error()

    def __repr__(self):
        return 'Orbit Panel'

    def set_current_digit(self, idx):
        self.curr_digit = self.ratios.index(idx)

    def cycle(self):
        has_values = False
        for ratio in self.ratios:
            ratio.deselect()
            has_values = ratio.value != ''

        valid = has_values and not self.no_star_error
        valid = valid and self.selected_marker is not None

        if valid:
            self.resonances_button.enable()
        else:
            ratio = next(self.cycler)
            ratio.select()
            WidgetHandler.set_origin(ratio)

    def ratios_to_string(self):
        x = int(self.digit_x.value)
        y = int(self.digit_y.value)
        assert x >= y, 'invalid ratio'
        self.write('{}° Order'.format(x - y), self.order_f, right=self.digit_x.rect.left - 2, y=self.digit_x.rect.y)
        return '{}:{}'.format(x, y)

    def clear_ratios(self):
        self.digit_x.clear()
        self.digit_y.clear()


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
    linked_astrobody = None
    locked = True

    modifiable = True
    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.f = self.crear_fuente(16, underline=True)

    def link_astrobody(self, astro):
        self.linked_astrobody = astro
        self.locked = False

    def get_orbit(self):
        orbit = self.linked_marker.orbit
        orbit = orbit if not hasattr(orbit, 'astrobody') else orbit.astrobody.orbit
        return orbit

    def create(self):
        orbit = self.get_orbit()
        self.clear()
        if hasattr(orbit, 'astrobody'):
            astrobody = orbit.astrobody
            self.parent.write(str(astrobody) + ': Orbital Characteristics', self.f, x=3, y=21 * 2 - 1)
        props = ['Semi-major axis', 'Semi-minor axis', 'Eccentricity', 'Inclination',
                 'Periapsis', 'Apoapsis', 'Orbital motion', 'Temperature', 'Orbital velocity', 'Orbital period',
                 'Argument of periapsis', 'Longitude of the ascending node']
        attr = ['semi_major_axis', 'semi_minor_axis', 'eccentricity', 'inclination',
                'periapsis', 'apoapsis', 'motion', 'temperature', 'velocity', 'period',
                'argument_of_periapsis', 'longitude_of_the_ascending_node']
        modifiables = ['Semi-major axis', 'Eccentricity', 'Inclination',
                       'Argument of periapsis', 'Longitude of the ascending node']
        if orbit.resonant:
            props.append('In a {resonant_order} resonance with {resonance}'.format(orbit))
        for i, prop in enumerate([j for j in attr if hasattr(orbit, j)]):
            value = getattr(orbit, prop)
            vt = ValueText(self, props[attr.index(prop)], 3, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            vt.value = value
            vt.modifiable = props[attr.index(prop)] in modifiables
            self.properties.add(vt)

    def fill(self):
        parametros = []
        for elemento in self.properties.widgets():
            value = None
            if elemento.text == 'Inclination':
                value = q(0 if elemento.text_area.value == '' else elemento.text_area.value, 'degree')
            elif elemento.text not in ['Orbital motion', 'Temperature']:
                value = q(elemento.text_area.value, elemento.text_area.unit)

            if value is not None:
                parametros.append(value)

        main = self.parent.current
        if self.linked_astrobody.orbit is None:
            orbit = self.linked_astrobody.set_orbit(main, parametros)
            self.linked_marker.orbit = orbit
        self.show()
        self.parent.planet_area.delete_objects(self.linked_astrobody)
        if hasattr(self.parent, 'recomendation'):
            self.parent.recomendation.hide()
        self.locked = True
        self.has_values = True

    def clear(self):
        self.parent.image.fill(COLOR_BOX, [0, 21 * 2 - 1, self.parent.rect.w, 21])
        for prop in self.properties.widgets():
            prop.kill()
            prop.text_area.kill()

    def show(self):
        self.create()

        for p in self.properties.widgets():
            p.show()

    def hide(self):
        self.clear()

    @staticmethod
    def elevate_changes(key, new_value):
        if key == 'Eccentricity':
            if new_value.m < 0.001:
                return q(0.001)
            elif new_value.m > 0.9999:
                return q(0.999)

        elif key == 'Inclination':
            if new_value.m < 0:
                return q(0, new_value.u)
            elif new_value.m > 180:
                return q(180, new_value.u)


class OrbitMarker(Meta, IncrementalValue, Intertwined):
    enabled = True
    name = ''
    color = None

    locked = False
    orbit = None

    def __init__(self, parent, name, star, value, is_complete_orbit=None, is_resonance=False, res=None):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.star = star
        self.name = name
        self._value = value
        if is_complete_orbit is False:
            self.orbit = RawOrbit(self.parent.current, round(value, 3))
            self.text = '{:~}'.format(value)
            self.color = COLOR_SELECTED
        elif is_complete_orbit is True:
            self.orbit = value
            self.text = '{:~}'.format(value.a)
            self.color = COLOR_SELECTED
        elif is_complete_orbit is None:
            self.color = COLOR_TEXTO
            self.text = '{:~}'.format(value)
        if is_resonance:
            self.orbit.resonant = True
            self.orbit.resonance = res[0]
            self.orbit.resonant_order = res[1]
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)
        EventHandler.register(self.key_to_mouse, 'Arrow')

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
                self.parent.anchor_maker(self)

        elif event.button == 3:
            self.parent.delete_marker(self)

        return self

    def tune_value(self, delta):
        if not self.locked:
            self.increment = self.update_increment()
            self.increment *= delta

            if Systems.get_current_star().validate_orbit(self.value.m + self.increment):
                self.value += q(self.increment, self.value.u)
                self.increment = 0
                self.parent.sort_markers()
                self.parent.check_artifexian(self)

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

    def __lt__(self, other):
        return self.value < other.value


class OrbitButton(Meta, Intertwined):
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
            # self.parent.view_button.disable()
            self.linked_type.show()
            self.lock()
            self.parent.check_orbits()

    def update(self):
        if not self.locked:
            super().update()
            self.create()
            self.selected = False

    def __repr__(self):
        return 'B.Orbit @' + str(self.get_value())


class RoguePlanet(ColoredBody):
    # "rogue" because it doesn't have an orbit yet
    def on_mousebuttondown(self, event):
        if not self.parent.parent.visible_markers:
            self.enabled = False
            self.parent.parent.link_astrobody_to_stellar_orbit(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = RoguePlanet
    name = 'Planets'

    def show(self):
        system = Systems.get_current()
        if system is not None:
            population = [i for i in system.planets + system.asteroids if i.orbit is None]
            self.populate(population)
        super().show()


class AddOrbitButton(TextButton):
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


class AddResonanceButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Resonance', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            assert hasattr(self.parent.selected_marker.orbit, 'astrobody'), "The orbit is empty."
            planet = self.parent.selected_marker.orbit.astrobody

            star = self.parent.current
            order = self.parent.ratios_to_string()
            position = from_stellar_resonance(star, planet, order)
            marker = self.parent.add_orbit_marker(position, resonance=True, res_parent=planet, res_order=order)
            self.parent.check_orbits()
            self.parent.check_artifexian(marker)
            self.disable()
            self.parent.clear_ratios()

    def enable(self):
        super().enable()
        self.parent.image.fill(COLOR_BOX, [325, 396, 63, 18])


class RatioDigit(BaseWidget):
    enabled = True
    value = ''
    name = ''

    def __init__(self, parent, digit, x, y):
        super().__init__(parent)
        self.f = self.crear_fuente(14)
        self.image = Surface((20, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        r = self.rect.inflate(-1, -1)
        self.image.fill(COLOR_BOX, (1, 1, r.w - 1, r.h - 1))
        self.name = 'Ratio Digit {}'.format(digit.capitalize())

    def on_keydown(self, tecla):
        if self.enabled and self.selected and tecla.origin.name == self.name:
            if tecla.tipo == 'Key' and len(self.value) < 2:
                self.value += tecla.data['value']

            elif tecla.tipo == 'Fin' and tecla.origin.name == self.name:
                self.parent.cycle()

            elif tecla.tipo == 'BackSpace':
                self.value = self.value[0:-1]

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.select()
            self.parent.set_current_digit(self)
            return self

    def deselect(self):
        self.selected = False
        self.image.fill((0, 0, 0))
        w, h = self.rect.size
        self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
        EventHandler.deregister(self.on_keydown)

    def select(self):
        self.selected = True
        self.image.fill((255, 255, 255))
        w, h = self.rect.size
        self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
        EventHandler.register(self.on_keydown, 'Key', 'BackSpace', 'Fin')

    def clear(self):
        self.value = ''

    def update(self):
        w, h = self.rect.size
        self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
        render = self.f.render(self.value, True, COLOR_TEXTO, COLOR_BOX)
        rect = render.get_rect(centerx=self.rect.centerx - self.rect.x, y=1)
        self.image.blit(render, rect)

    def __repr__(self):
        return self.name


class Recomendation(BaseWidget):
    text = ''
    format = None
    text_size = 14
    just = 1

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((350, 230))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))

    def suggest(self, planet, orbit, star):
        data = None
        planets_in_system = len(Systems.get_current().planets)
        e = round(0.584 * pow(planets_in_system, -1.2), 3) if planets_in_system > 1 else None
        if planet.habitable and orbit.temperature == 'habitable':
            data = recomendation['habitable']
            if hasattr(star, 'habitable_orbit'):
                # though this may never come into play.
                if orbit.a.m <= star.habitable_orbit:
                    data = recomendation['inner']
            if e is not None and e <= 0.2:
                data.update({'e': e})

        elif planet.clase == 'Terrestial Planet':
            data = recomendation['inner']
            if e is not None and e <= 0.2:
                data.update({'e': e})

        elif planet.clase in ('Gas Giant', 'Super Jupiter', 'Puffy Giant', 'Gas Dwarf'):
            data = recomendation['giant']
            data.update(self.analyze_giants(planet, orbit, star))
            if data.get('eccentric', False):
                pass
            elif e is not None and 0.001 <= e <= 0.09:
                data.update({'e': e})

        elif planet.clase == 'Dwarf Planet' or planet.celestial_type == 'asteroid':
            gas_giants = [pln for pln in Systems.get_current().astro_bodies if
                          pln.clase in ('Gas Giant', 'Super Jupiter', 'Puffy Giant')]
            gas_giants.sort(key=lambda g: g.orbit.a.m, reverse=True)
            if len(gas_giants):
                last_gas_giant = gas_giants[0]
                lim_min = last_gas_giant.orbit.a.m
            else:
                lim_min = 0

            if lim_min < orbit.a.m < star.outer_boundry.m:
                data = recomendation['texts']['tno']
                if not orbit.resonant:
                    data = data.format(' ')
                    for key in ('classical', 'sednoid'):
                        t = recomendation[key]
                        data += '\n\nFor a {} object:\n'.format(t['n'])
                        data += 'Eccentricity should be {}\n'.format(t['e'])
                        data += 'Inclination should be {}.'.format(t['i'])
                else:
                    data = data.format(" resonant ")
                    for key in ('sdo', 'detached', "resonant"):
                        t = recomendation[key]
                        data += '\n\nFor a {} object:\n'.format(t['n'])
                        data += 'Eccentricity should be {}\n'.format(t['e'])
                        data += 'Inclination should be {}.'.format(t['i'])

        self.format = data

    @staticmethod
    def analyze_giants(planet, orbit, star):
        planets_in_system = len(Systems.get_current().planets)

        # average eccentricity

        clase = planet.clase in ('Puffy Giant', 'Gas Giant')
        orbita = 0.04 <= orbit.a.m <= 0.5
        period = q(sqrt(pow(orbit.a.m, 3) / star.mass.m), 'year').to('day').m >= 3
        if all([clase, orbita, period]) is True:
            return recomendation['hot']

        clase = planet.clase == 'Super Jupiter'
        orbita = 0.04 <= orbit.a.m <= 1.2 + star.frost_line.m
        if all([clase, orbita]) is True:
            # this is more of a warning than a suggestion, since a super jupiter
            # can't be placed too far away from the star, and there is no special
            # consideration about it's eccentricity or inclination.
            return recomendation['giant']
        elif clase:  # Is the planet still a Super Jupiter?
            raise AssertionError("A super jupiter can't orbit so far away from it's star.")
            # needs an "undo" after this.

        clase = planet.clase in ('Gas Dwarf', 'Gas Giant')
        orbita = star.frost_line.m + 1 <= orbit.a.m <= star.frost_line.m + 1.2
        if all([clase, orbita]) is True:
            return recomendation['giant']

        e = round(0.584 * pow(planets_in_system, -1.2), 3) if planets_in_system > 1 else 0
        clase = planet.clase == 'Gas Giant'
        habitable = any([i.habitable for i in Systems.get_current().planets])
        data = recomendation['giant']
        data.update({'eccentric': True})
        error = f'An eccentric Jupiter must have an orbital eccentricity of 0.1 or greater, up to 0.2 if there is a '
        error += f'habitable world in the system. However, there are {planets_in_system} planets in this system, so '
        error += f'the eccentricity should be {e} which falls ouside of those parameters.'
        assert all([habitable, planets_in_system not in (3, 4), e > 0.1]), error
        if all([clase, habitable]) is True:
            data.update(recomendation['eccentric_2'])
        elif not habitable:
            data.update(recomendation['eccentric_1'])
        return data

    def create_suggestion(self, planet, temperature):
        if not type(self.format) is str:
            base_text = recomendation['texts']['text']
            if planet.habitable is True and temperature == 'habitable':
                p = 'Habitable Planet'
            else:
                p = planet.clase
            self.format.update({'planet_type': p})
            return base_text.format(**self.format)
        else:
            self.text_size = 11
            self.just = 0
            return self.format

    def show_suggestion(self, planet, temp):
        text = self.create_suggestion(planet, temp)
        f = self.crear_fuente(self.text_size)
        f2 = self.crear_fuente(12, bold=True)
        title = f2.render('Suggestion', 1, COLOR_TEXTO, COLOR_AREA)
        render = render_textrect(text, f, self.rect.w, COLOR_TEXTO, COLOR_AREA, justification=self.just)
        render_rect = render.get_rect(topleft=[3, 16])
        self.image.fill(COLOR_AREA)
        self.image.blit(render, render_rect)
        self.image.blit(title, (0, 0))
        self.show()

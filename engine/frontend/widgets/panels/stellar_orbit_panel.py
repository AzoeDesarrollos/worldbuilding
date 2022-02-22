from engine.equations.orbit import RawOrbit, PseudoOrbit, from_stellar_resonance, in_resonance
from .common import TextButton, ListedArea, ToggleableButton, ColoredBody, ModifyArea
from engine.frontend.globales import WidgetGroup, render_textrect, WidgetHandler
from engine.frontend.widgets.incremental_value import IncrementalValue
from pygame import Surface, Rect, K_LCTRL, K_RCTRL, key as pyg_key
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.globales.constantes import *
from engine.frontend.widgets.meta import Meta
from engine import q, recomendation
from engine.backend import roll
from ..values import ValueText
from itertools import cycle
from math import sqrt, pow
from bisect import bisect_left


class OrbitPanel(BaseWidget):
    current = None  # ahora será la estrella o sistema seleccionado.

    last_idx = 0
    _loaded_orbits = None

    offset = 0
    curr_x, curr_y = 3, 442

    visible_markers = True
    orbits = None
    markers = None
    buttons = None

    skippable = False

    no_star_error = False

    resonance_mode = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 32, 380, 20 * 10)
        self.area_modify = ModifyArea(self, ANCHO - 201, 374)

        self.f = self.crear_fuente(16, underline=True)
        self.f2 = self.crear_fuente(12)
        self.order_f = self.crear_fuente(14)
        self.write(self.name + ' Panel', self.f, centerx=(ANCHO // 4) * 1.5, y=0)
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)

        self.area_recomendation = Rect(3, 0, 380, 185)
        self.area_recomendation.top = self.area_markers.bottom
        self.recomendation = Recomendation(self)

        self._loaded_orbits = {}
        self.indexes = []

        self._orbits = {}
        self._buttons = {}
        self._markers = {}

        self.orbit_descriptions = WidgetGroup()
        self.show_markers_button = ToggleableButton(self, 'Stellar Orbits', self.toggle_stellar_orbits, 3, 421)
        self.show_markers_button.disable()
        self.add_orbits_button = SetOrbitButton(self, ANCHO - 94, 394)
        self.resonances_button = AddResonanceButton(self, ANCHO - 140, 416)

        self.digit_x = RatioDigit(self, 'x', self.resonances_button.rect.left - 60, self.resonances_button.rect.y)
        self.write(':', self.crear_fuente(16), topleft=[self.digit_x.rect.right + 1, self.resonances_button.rect.y - 1])
        self.digit_y = RatioDigit(self, 'y', self.digit_x.rect.right + 9, self.resonances_button.rect.y)
        self.ratios = [self.digit_x, self.digit_y]
        self.cycler = cycle(self.ratios)
        next(self.cycler)

        self.properties.add([self.area_modify, self.planet_area, self.show_markers_button,
                             self.add_orbits_button, self.resonances_button, self.digit_x,
                             self.digit_y, self.recomendation], layer=2)
        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.save_orbits, 'Save')
        EventHandler.register(self.load_orbits, 'LoadData')

    def set_current(self):
        star = Systems.get_current_star()
        self.current = star
        self.last_idx = self.current.id
        self.orbits: list = self._orbits[star.id]
        self.markers = self._markers[star.id]
        self.buttons = self._buttons[star.id]
        if self.is_visible:
            if star.evolution_id != star.id:
                self.depopulate()
            if not len(self.markers) or not self.markers[0].locked:
                self.populate()
            self.sort_buttons()

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

    def add_orbit_marker(self, position, resonance=False, res_parent=None, res_order=None, obj=None):
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
        if hasattr(position, 'e'):
            test = True  # saved orbits are valid by definition
            color = COLOR_STARORBIT
        elif resonance is False:
            test = inner < position < outer
            color = COLOR_TEXTO
        elif resonance is True:
            bd = [res_parent, res_order]
            test = inner < position  # TNOs orbit well outside of 40AUs.
            color = COLOR_RESONANT

        if test is True:
            new = OrbitMarker(self, obj, star, position, is_complete_orbit=bb, is_resonance=bc, res=bd)
            self._markers[star.id].append(new)
            self._orbits[star.id].append(new)
            if self.is_visible:
                self.sort_markers()
            if bb is False:
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
        if self.markers is not None:
            self.markers.sort(key=lambda m: m.value)
            for i, marker in enumerate(self.markers, start=1):
                marker.rect.y = i * 2 * 10 + 16 + self.offset
                if self.visible_markers:
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
            if hasattr(marker.orbit, 'astrobody'):
                marker.orbit.astrobody.unset_orbit()
            self.planet_area.show()
            self.sort_markers()
            self.sort_buttons()

    def on_mousebuttondown(self, event):

        if self.area_markers.collidepoint(event.pos) and self.markers is not None:
            last_is_hidden = not self.markers[-1].is_visible
            if len(self.markers) >= 8 and event.button in (4, 5):
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

        elif self.area_recomendation.collidepoint(event.pos):
            if event.button == 4:
                pass
            elif event.button == 5:
                pass

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

    def check_orbits2(self, marker):
        self.orbits.sort(key=lambda o: o.value.m)
        x = self.orbits.index(marker)
        a: OrbitMarker = self.orbits[x - 1] if x - 1 > 0 and len(self.orbits) else self.orbits[0]  # el anterior
        b: OrbitMarker = self.orbits[x + 1] if x + 1 <= len(self.orbits) - 1 else self.orbits[-1]  # el posterior

        valid_a = a.orbit.a.m + 0.15 < marker.orbit.a.m if a != marker else None
        valid_b = marker.orbit.a.m < b.orbit.a.m - 0.15 if b != marker else None

        # Dwarf Planets, like Pluto, can orbit in crowded orbits. Same with the asteroids in the Asteroid Belt.
        main_body = marker.linked_astrobody
        body_a = a.linked_astrobody
        body_b = b.linked_astrobody

        if main_body.clase == 'Dwarf Planet' or main_body.celestial_type == 'asteroid':
            if body_a.clase == 'Dwarf Planet' or body_a.celestial_type == 'asteroid':
                valid_a = True
            if body_b.clase == 'Dwarf Planet' or body_b.celestial_type == 'asteroid':
                valid_b = True

        return valid_a, valid_b

    def check_artifexian(self, marker):
        self.orbits.sort(key=lambda o: o.value.m)
        idx = bisect_left(self.orbits, marker)
        left: OrbitMarker = None
        right: OrbitMarker = None
        frost_line = False
        if 0 < idx < len(self.orbits) - 1:
            left = self.orbits[idx - 1]
            right = self.orbits[idx + 1]
        elif marker.linked_astrobody.relative_size == 'Giant' and len(self.orbits) == 1:
            frost_line = self.current.frost_line.m
            left = frost_line if marker.value.m < frost_line else None
            right = frost_line if marker.value.m > frost_line else None
        elif idx == 0 and len(self.orbits) > 1:
            right = self.orbits[idx + 1]
        elif len(self.orbits) > 1:
            left = self.orbits[idx - 1]

        if left is not None:
            self.check_resonances(marker, left)
        if right is not None:
            self.check_resonances(marker, right)

        if len(self.orbits) == 1 and marker.linked_astrobody.relative_size != 'Giant':
            left_value = 1.5
            right_value = 1.5
        elif not frost_line:
            left_value = round(marker.value.m / left.value.m, 3) if left is not None else False
            right_value = round(right.value.m / marker.value.m, 3) if right is not None else False
        else:
            right_value = abs(marker.value.m - right) if right is not None else False
            left_value = abs(marker.value.m - left) if left is not None else False

        return left_value, right_value

    @staticmethod
    def check_resonances(marker, other):
        resonant_result = in_resonance(marker, other)
        if resonant_result is not False:
            marker.orbit.resonant = True
            marker.orbit.resonance = other.linked_astrobody
            marker.orbit.resonant_order = resonant_result

            other.orbit.resonant = True
            other.orbit.resonance = marker.linked_astrobody
            other.orbit.resonant_order = resonant_result

    def anchor_maker(self, marker):
        self.deselect_markers(marker)
        self.area_modify.link(marker)

    def clear(self, event):
        if event.data['panel'] is self:
            for marker in self.markers:
                if not marker.locked:
                    self.delete_marker(marker)
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
        if len(event.data.get('Stellar Orbits', [])):
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
                            self.add_orbit_marker(planet.orbit, obj=planet)
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
            self.resonance_mode = False
            for marker in self.markers:
                marker.hide()
        else:
            for marker in self.markers:
                marker.show()
            self.hide_orbit_types()
            self.show_markers_button.disable()
            self.area_modify.color_standby()
        self.visible_markers = not self.visible_markers

    def on_orbit_button_press(self):
        self.recomendation.hide()
        self.hide_orbit_types()
        self.show_markers_button.enable()
        self.check_orbits()

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

    def link_astrobody_to_stellar_orbit(self, astrobody, **kwargs):
        system = Systems.get_current()
        star = system.star_system
        if self.resonance_mode is False:
            pos = q(roll(star.inner_boundry.m, star.outer_boundry.m), 'au')
            marker = self.add_orbit_marker(pos, obj=astrobody)
            self.add_orbits_button.link(marker)
        else:
            pos = kwargs.pop('pos')
            marker = self.add_orbit_marker(pos, obj=astrobody, **kwargs)
            self.recomendation.set_resonance_text(step=3, obj=astrobody,
                                                  anchor=kwargs['res_parent'],
                                                  ratio=kwargs['res_order'])
            self.resonances_button.link(marker)
        self.sort_markers()
        self.recomendation.update_suggestion(marker, astrobody, marker.orbit)

    def develop_orbit(self, marker):
        self.toggle_stellar_orbits()
        marker.orbit = PseudoOrbit(marker.orbit)
        marker.linked_type.link_astrobody(marker.linked_astrobody)
        self.add_orbits_button.unlink()

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
            # self.image.fill(COLOR_BOX, self.area_markers)
            self.image.fill(COLOR_AREA, self.area_buttons)
        else:
            self.show_no_system_error()

    def __repr__(self):
        return 'Orbit Panel'

    def cycle(self):
        has_values = False
        for ratio in self.ratios:
            ratio.deselect()
            has_values = ratio.value != ''

        if has_values and not self.no_star_error:
            self.resonances_button.enable()
        else:
            ratio = next(self.cycler)
            ratio.select()
            WidgetHandler.set_origin(ratio)

    def set_resonance_mode(self, anchor):
        """Sets the resonance mode using the selected planet as anchor."""
        self.resonance_mode = True
        self.resonances_button.set_anchor(anchor)
        self.recomendation.set_resonance_text(step=1)
        self.recomendation.update()

    def unset_resonance_mode(self):
        """Unsets the resonance mode. New positions will be random."""
        self.resonance_mode = False
        self.recomendation.set_resonance_text(step=0)

    def ratios_to_string(self):
        x = int(self.digit_x.value)
        y = int(self.digit_y.value)
        assert x >= y, 'invalid ratio'
        return '{}:{}'.format(x, y)

    def clear_ratios(self):
        self.digit_x.clear()
        self.digit_y.clear()

    def reset_offset(self):
        self.offset = 0
        # self.sort_markers()


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
        self.show()

    def get_orbit(self):
        if self.linked_marker is not None:
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
        i = 0
        for i, prop in enumerate([j for j in attr if hasattr(orbit, j)]):
            value = getattr(orbit, prop)
            vt = ValueText(self, props[attr.index(prop)], 3, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            vt.value = value
            vt.modifiable = props[attr.index(prop)] in modifiables
            self.properties.add(vt)

        if hasattr(orbit, 'resonant_order') and orbit.resonant:
            i += 1
            f1 = self.crear_fuente(16)
            order = orbit.resonant_order
            resonance = orbit.resonance
            extra = f'In a {order} resonance with {resonance}'
            sprite = BaseWidget(self.parent)
            sprite.image = self.parent.write3(extra, f1, self.parent.rect.w)
            sprite.rect = sprite.image.get_rect(x=3, y=64 + i * 21)
            self.properties.add(sprite)

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
        if hasattr(self.linked_astrobody.orbit, 'longitude_of_the_ascending_node'):
            parametros.append(self.linked_astrobody.orbit.longitude_of_the_ascending_node.m)
            aop = self.linked_astrobody.orbit.argument_of_periapsis
            parametros.append(aop.m if type(aop) is q else aop)

        orbit = self.linked_astrobody.set_orbit(main, parametros)
        self.linked_marker.orbit = orbit
        self.show()
        self.parent.planet_area.delete_objects(self.linked_astrobody)
        self.linked_button.select()
        self.parent.show_markers_button.enable()
        if hasattr(self.parent, 'recomendation'):
            self.parent.recomendation.hide()
        self.locked = True
        self.has_values = True
        self.linked_marker.completed = True

    def clear(self):
        self.parent.image.fill(COLOR_BOX, [0, 21 * 2 - 1, self.parent.rect.w, 21])
        for prop in self.properties.widgets():
            prop.kill()

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

    completed = False

    def __init__(self, parent, astro, star, value, is_complete_orbit=None, is_resonance=False, res=None):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.star = star
        self.name = str(astro)
        self.linked_astrobody = astro
        self._value = value
        if is_complete_orbit is False:
            self.orbit = RawOrbit(star, round(value, 3))
            self.text = '{:~}'.format(value)
            self.color = COLOR_SELECTED
        elif is_complete_orbit is True:
            self.orbit = value
            self.text = '{:~}'.format(value.a)
            self.color = COLOR_SELECTED
            self.completed = True
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
        pressed = pyg_key.get_pressed()
        ctrl_pressed = pressed[K_RCTRL] or pressed[K_LCTRL]
        if event.button == 1:
            self.parent.sort_markers()
            if ctrl_pressed:
                self.parent.set_resonance_mode(self.linked_astrobody)
            else:
                self.parent.unset_resonance_mode()

            if not self.locked and not self.completed:
                self.parent.anchor_maker(self)
                self.parent.recomendation.update_suggestion(self, self.linked_astrobody, self.orbit)
            else:
                self.parent.recomendation.hide()

        elif event.button == 3:
            self.parent.delete_marker(self)

        elif event.button in (4, 5):
            self.parent.on_mousebuttondown(event)

        return self

    def tune_value(self, delta):
        if not self.locked:
            self.increment = self.update_increment()
            self.increment *= delta

            if Systems.get_current_star().validate_orbit(self.value.m + self.increment):
                self.value += q(self.increment, self.value.u)
                self.increment = 0
                self.parent.sort_markers()
                self.parent.recomendation.update_suggestion(self, self.linked_astrobody, self.orbit)
                self.parent.add_orbits_button.link(self)
                self.parent.sort_buttons()

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
        self.rect = self.img_sel.get_rect(topleft=self._rect.topleft)

    def move(self, x, y):
        self._rect.topleft = x, y
        self.create()

    def lock(self):
        self.selected = True
        self.locked = True

    def unlock(self):
        self.selected = False
        self.locked = False

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.parent.visible_markers:
                self.parent.toggle_stellar_orbits()
            self.parent.on_orbit_button_press()
            self.linked_type.show()
            self.lock()

    def update(self):
        super().update()
        if not self.locked:
            self.create()

    def __repr__(self):
        return 'B.Orbit @' + str(self.get_value())


class RoguePlanet(ColoredBody):
    # "rogue" because it doesn't have an orbit yet
    def on_mousebuttondown(self, event):
        if event.button == 1 and self.parent.parent.visible_markers and self.enabled:
            self.enabled = False
            if self.parent.parent.resonance_mode is False:
                self.parent.parent.link_astrobody_to_stellar_orbit(self.object_data)
            else:
                self.parent.parent.resonances_button.set_resonant(self.object_data)
                self.parent.parent.recomendation.set_resonance_text(step=2)


class AvailablePlanets(ListedArea):
    listed_type = RoguePlanet
    name = 'Planets'

    def show(self):
        system = Systems.get_current()
        if system is not None:
            population = [i for i in system.planets + system.asteroids if i.orbit is None]
            self.populate(population)
        super().show()


class SetOrbitButton(TextButton):
    anchor = None
    locked = False
    linked_marker = None
    enabled = False

    overwritten = False

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set Orbit', x, y)
        self.disable()

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            if self.linked_marker.orbit.stable:
                self.parent.recomendation.notify()
                self.parent.develop_orbit(self.linked_marker)

    def lock(self):
        self.locked = True
        self.overwritten = True

    def unlock(self):
        self.locked = False
        self.overwritten = True

    def link(self, marker):
        self.linked_marker = marker
        self.enable()

    def unlink(self):
        self.lock()
        self.disable()

    def update(self):
        if self.linked_marker is not None and not self.overwritten:
            if self.linked_marker.orbit.stable:
                self.enable()
            else:
                self.disable()

        super().update()


class AddResonanceButton(TextButton):
    anchor = None
    resonant = None
    linked_marker = None

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Resonance', x, y)

    def set_anchor(self, planet):
        self.anchor = planet

    def set_resonant(self, planet):
        self.resonant = planet

    def clear(self):
        self.anchor = None
        self.resonant = None
        self.parent.unset_resonance_mode()

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            assert self.resonant is not None, "Select a rogue planet to be resonant first."
            star = self.parent.current
            order = self.parent.ratios_to_string()
            position = from_stellar_resonance(star, self.anchor, order)
            kwargs = {'pos': position, 'resonance': True, 'res_parent': self.anchor, 'res_order': order}
            self.parent.link_astrobody_to_stellar_orbit(self.resonant, **kwargs)

            self.parent.recomendation.notify()
            self.parent.develop_orbit(self.linked_marker)
            self.parent.check_orbits()
            self.clear()
            self.disable()
            self.parent.clear_ratios()

    def link(self, marker):
        self.linked_marker = marker

    def unlink(self):
        self.linked_marker = None

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

    rendered_text = None
    rendered_rect = None

    recomendation = None

    tense = 'seem to be building'

    _marker = None
    _astro = None
    _orbit = None

    notified = False

    resonance_text = ''

    def __init__(self, parent):
        super().__init__(parent)
        self.image = Surface(self.parent.area_recomendation.size)
        self.rect = self.parent.area_recomendation

        f1 = self.crear_fuente(13, bold=True)
        self.f2 = self.crear_fuente(12)
        self.title = f1.render('Suggestion', 1, COLOR_TEXTO)
        self.title_rect = self.title.get_rect()
        self.rendered_rect = Rect(3, 0, 0, 0)
        self.rendered_rect.top = self.title_rect.bottom

    def analyze_orbits(self, marker):
        left_factor, right_factor = self.parent.check_artifexian(marker)
        astro = marker.linked_astrobody
        valid_in, valid_out = self.parent.check_orbits2(marker)
        v_in = True if valid_in is None else valid_in
        v_out = True if valid_out is None else valid_out

        v_left_in = 1.4 <= left_factor if astro.relative_size != 'Giant' else 1 <= left_factor
        v_left_out = left_factor <= 2 if astro.relative_size != 'Giant' else left_factor <= 1.2

        v_right_in = 1.4 <= right_factor if astro.relative_size != 'Giant' else 1 <= right_factor
        v_right_out = right_factor <= 2 if astro.relative_size != 'Giant' else right_factor <= 1.2

        if not left_factor:
            txt = ' ' if (v_right_in and v_in) and ((v_right_out and v_out) or not left_factor) else 'n un'
        elif not right_factor:
            txt = ' ' if (v_left_in and v_in) and ((v_left_out and v_out) or not right_factor) else 'n un'
        else:
            txt = ' ' if all([v_left_in, v_left_out, v_right_in, v_right_out, v_in, v_out]) else 'n un'

        if len(txt) > 1:
            adverb = ' However, t'
            if type(self.format) is dict:
                if not self.format.get('eccentric', False):
                    # Eccentric Jupiters can orbit anywhere in the system, so their orbits are valid by definition.
                    marker.orbit.stable = False
        elif not marker.orbit.stability_overriten:
            marker.orbit.stable = True
            adverb = ' T'
        else:
            adverb = ' However, t'
            txt = 'n un'

        message = f'{adverb}his is a{txt}stable orbit.'
        if type(self.format) is str:
            self.format = self.format.format(verb=self.tense, orbit=message, extra='{extra}')
        elif type(self.format) is dict:
            self.format['verb'] = self.tense
            if 'orbit' not in self.format:
                self.format['orbit'] = message

    def suggest(self, planet, orbit, star):
        self.recomendation = recomendation.copy()
        if type(self.format) is dict:
            self.format.clear()
        else:
            self.format = None

        data = {'extra': ''}
        planets_in_system = len(Systems.get_current().planets)
        e = round(0.584 * pow(planets_in_system, -1.2), 3) if planets_in_system > 1 else None
        if planet.habitable and orbit.temperature == 'habitable':
            data.update(self.recomendation['habitable'].copy())
            if hasattr(star, 'habitable_orbit'):
                # though this may never come into play.
                if orbit.a.m <= star.habitable_orbit:
                    data = self.recomendation['inner'].copy()
            if e is not None and e <= 0.2:
                data.update({'e': e})

        elif planet.clase == 'Terrestial Planet':
            data.update(self.recomendation['inner'].copy())
            if e is not None and e <= 0.2:
                data.update({'e': e})

        elif planet.clase == 'Dwarf Planet' or planet.celestial_type == 'asteroid':
            gas_giants = [pln for pln in Systems.get_current().astro_bodies if
                          pln.clase in ('Gas Giant', 'Super Jupiter', 'Puffy Giant')]
            terrestial_planets = [pln for pln in Systems.get_current().astro_bodies if pln.clase == 'Terrestial']
            gas_giants.sort(key=lambda g: g.orbit.a.m, reverse=True)
            terrestial_planets.sort(key=lambda g: g.orbit.a.m, reverse=True)
            lim_min, lim_max = 0, orbit.a.m + 10
            lim_terra = 0
            if len(gas_giants):
                last_gas_giant = gas_giants[0]
                first_gas_giant = gas_giants[-1]
                lim_min = last_gas_giant.orbit.a.m
                lim_max = first_gas_giant.orbit.a.m
            if len(terrestial_planets):
                last_terrestial = terrestial_planets[0]
                lim_terra = last_terrestial.orbit.a.m

            if lim_min <= orbit.a.m < star.outer_boundry.m:
                data = self.recomendation['texts']['tno']
            elif lim_terra <= orbit.a.m < lim_max:
                data = self.recomendation['texts']['belt']

        elif planet.clase in ('Gas Giant', 'Super Jupiter', 'Puffy Giant', 'Gas Dwarf'):
            data = self.recomendation['giant'].copy()
            data.update(**self.analyze_giants(planet, orbit, star, e))
            if data.get('eccentric', False):
                data['orbit'] = ' Eccentric Jupiters can orbit anywhere in the system.'
            elif e is not None and 0.001 <= e <= 0.09:
                data.update({'e': e})

        self.format = data

    def append_subclases(self, orbit, star):
        gas_giants = [pln for pln in Systems.get_current().astro_bodies if
                      pln.clase in ('Gas Giant', 'Super Jupiter', 'Puffy Giant')]
        gas_giants.sort(key=lambda g: g.orbit.a.m, reverse=True)
        lim_min = 0
        if len(gas_giants):
            last_gas_giant = gas_giants[0]
            lim_min = last_gas_giant.orbit.a.m
        txt = ''
        if lim_min <= orbit.a.m < star.outer_boundry.m:
            if orbit.stable:
                txt = ' It may fit into one of the following categories, '
                txt += 'provided it has the appropiate values for ecentricity and inclination.'
                if not orbit.resonant:
                    for key in ('classical', 'sednoid'):
                        t = self.recomendation[key].copy()
                        txt += f'\n\nFor a {t["n"]} object:\n'
                        txt += f'Eccentricity should be {t["e"]}\n'
                        txt += f'Inclination should be {t["i"]}.'
                else:
                    self.format.format(extra=" resonant ")
                    for key in ('sdo', 'detached', "resonant"):
                        t = self.recomendation[key].copy()
                        txt += f'\n\nFor a {t["n"]} object:\n'
                        txt += f'Eccentricity should be {t["e"]}\n'
                        txt += f'Inclination should be {t["i"]}.'

        if '{extra}' in self.format:
            self.format = self.format.format(extra=' ')

        self.format += txt

    def analyze_giants(self, planet, orbit, star, eccentricity=None):
        data = {'extra': ''}
        frost_line = star.frost_line.m

        clase = planet.clase in ('Puffy Giant', 'Gas Giant')
        orbita = 0.04 <= orbit.a.m <= 0.5
        period = q(sqrt(pow(orbit.a.m, 3) / star.mass.m), 'year').to('day').m >= 3
        if all([clase, orbita, period]) is True:
            data.update(self.recomendation['hot'].copy())
            data.update({'planet_type': 'Puffy Giant'})
            return data

        orbita = 0.04 < orbit.a.m <= 1.2 + frost_line
        if planet.clase == 'Super Jupiter':
            data = self.recomendation['giant'].copy()
            data.update({'extra': ''})
            if not orbita:
                txt = "\n\nSuper Jupiters must orbit between 0.04 AU and 1.2 AU away from the frost line."
                txt += " Please put your planet in that zone."
                data.update({'extra': txt})
                data.update({'planet_type': planet.clase})
                orbit.stable = False
                orbit.stability_overriten = True
            else:
                orbit.stability_overriten = False
                if orbit.a.m < frost_line:
                    orbit.migrated = True
            return data

        if planet.clase == 'Gas Dwarf':
            orbita = 1.2 + frost_line <= orbit.a.m <= star.outer_boundry.m
            data = self.recomendation['giant'].copy()
            data['extra'] = ''
            if not orbita:
                txt = "\n\n"
                txt += "Gas Dwarves must orbit between 1.2 AU from the frost line and the outer boundary of the system."
                txt += " Please put your planet in that zone. For extra added realism stick to a very distant orbit."
                data.update({'extra': txt})
                data.update({'planet_type': planet.clase})
                orbit.stable = False
                orbit.stability_overriten = True
            else:
                orbit.stability_overriten = False
            return data

        if planet.clase == 'Gas Giant':
            orbita = frost_line + 1 <= orbit.a.m <= frost_line + 1.2 or orbit.a.m >= frost_line + 1.2
            gas_giants = [pln for pln in Systems.get_current().astro_bodies if
                          pln.clase in ('Gas Giant', 'Super Jupiter', 'Puffy Giant')]
            gas_giants.sort(key=lambda g: g.mass, reverse=True)
            data = self.recomendation['giant'].copy()
            data['extra'] = ''
            if eccentricity is not None:
                data['e'] = eccentricity
            is_largest_gas_giant = gas_giants[0] == planet
            if is_largest_gas_giant:
                distance = abs(round(orbit.a.m - star.frost_line.m, 3))
                txt = "\n\n"
                txt += "As this is your largest gas giant, it should orbit 1 to 1.2 AU away from its star's frost line."
                txt += f" Currently, its orbit is {distance} AU away from the frost line."
                data.update({'extra': txt})
                data.update({'planet_type': planet.clase})
                if not frost_line + 1 <= orbit.a.m <= frost_line + 1.2:
                    orbit.stable = False
                    orbit.stability_overriten = True
                else:
                    orbit.stability_overriten = False

            elif not orbita:
                data.update({'extra': ''})
                clase = planet.clase == 'Gas Giant'
                habitable = any([i.habitable for i in Systems.get_current().planets])
                data.update({'eccentric': True, 'planet_type': 'Eccentric Jupiter', 'orbit': ''})
                if all([clase, habitable]) is True and eccentricity is None:
                    data.update(**self.recomendation['eccentric_2'].copy())
                elif not habitable:
                    data.update(**self.recomendation['eccentric_1'].copy())
                else:
                    data.update({'e': eccentricity})
            return data

    def create_suggestion(self, planet, temperature):
        if not type(self.format) is str:
            base_text = self.recomendation['texts']['text']
            if planet.habitable is True and temperature == 'habitable':
                p = 'Habitable Planet'
            else:
                p = planet.clase
            if 'planet_type' not in self.format:
                self.format.update({'planet_type': p})

            vocals = 'AEIOU'
            if self.format['planet_type'][0] in vocals:
                self.format['n'] = 'n'
            else:
                self.format['n'] = ''

            return base_text.format(**self.format) + self.resonance_text
        else:
            return self.format

    def adjust_size(self):
        if self.rendered_rect.size != self.rendered_text.get_rect().size:
            self.rendered_rect.size = self.rendered_text.get_rect().size
            self.rendered_rect.y = 17

    def show_suggestion(self, planet, temp):
        text = self.create_suggestion(planet, temp)
        self.rendered_text = render_textrect(text, self.f2, self.rect.w, COLOR_TEXTO, COLOR_DARK_AREA)
        self.adjust_size()
        self.show()

    def show_resonance_text(self):
        text = self.resonance_text
        self.rendered_text = render_textrect(text, self.f2, self.rect.w, COLOR_TEXTO, COLOR_DARK_AREA)
        self.adjust_size()
        self.show()

    def on_mousebuttondown(self, event):
        if event.button == 4:
            if self.rendered_rect.top + 12 <= 17:
                self.rendered_rect.move_ip(0, +12)
        elif event.button == 5:
            if self.rendered_rect.bottom - 6 >= self.rect.h - 3:
                self.rendered_rect.move_ip(0, -12)

    def update_suggestion(self, marker, astro_body, astro_orbit):
        if not self.notified:
            self.tense = 'seem to be building'
        self._marker = marker
        self._astro = astro_body
        self._orbit = astro_orbit
        self.suggest(astro_body, astro_orbit, Systems.get_current_star())
        self.analyze_orbits(marker)
        if astro_body.clase == 'Dwarf Planet' or astro_body.celestial_type == 'asteroid':
            self.append_subclases(astro_orbit, Systems.get_current_star())
        self.show_suggestion(astro_body, astro_orbit.temperature)

    def notify(self):
        self.notified = True
        self.tense = 'decided to build'
        self.update_suggestion(self._marker, self._astro, self._orbit)
        self.notified = False

    def update(self):
        if self.rendered_text is not None:
            self.image.fill(COLOR_DARK_AREA)
            self.image.blit(self.rendered_text, (0, self.rendered_rect.y))
            self.image.fill(COLOR_DARK_AREA, [0, 0, self.rect.w, 21])
            self.image.blit(self.title, self.title_rect)
        else:
            self.image.fill(COLOR_BOX)

    def set_resonance_text(self, anchor=None, ratio=None, obj=None, step=0):
        if step == 0:
            self.resonance_text = ''
        elif step == 1:
            self.resonance_text = 'Resonance mode is enabled. Select a Rogue planet to establish the resonance.'
            self.show_resonance_text()
        elif step == 2:
            self.resonance_text = "Resonance mode is enabled. Set the resonance's ratio and press the button."
            self.show_resonance_text()
            self.parent.digit_x.select()
            WidgetHandler.set_origin(self.parent.digit_x)
        elif step == 3:
            self.resonance_text = f'\n\n{obj} is in a {ratio} Mean Motion Resonance with {anchor}.'

    def unset_resonance_text(self):
        self.resonance_text = ''

    def hide(self):
        super().hide()
        self.parent.area_markers.h += self.rect.h
        self.parent.reset_offset()

    def show(self):
        super().show()
        if self.parent.area_markers.colliderect(self.rect):
            self.parent.area_markers.h -= self.rect.h
            self.parent.sort_markers()

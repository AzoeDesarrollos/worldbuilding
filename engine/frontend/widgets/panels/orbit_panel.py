from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, COLOR_AREA, COLOR_DISABLED
from engine.frontend.globales import Renderer, WidgetHandler, ANCHO, ALTO
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.orbit import RawOrbit, PseudoOrbit
from engine.frontend.globales.group import WidgetGroup
from engine.backend.eventhandler import EventHandler
from engine.equations.planetary_system import system
from .planet_panel import PlanetButton, TextButton
from pygame import Surface, font, Rect
from engine.backend import roll
from ..values import ValueText
from .planet_panel import Meta
from engine import q


class OrbitPanel(BaseWidget):
    current = None
    curr_idx = 0
    _loaded_orbits = None

    offset = 0

    visible_markers = True
    current_orbit = None

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.properties = WidgetGroup()
        self.marker_area = Rect(3, 58, 380, 20 * 16)
        self.modify_area = ModifyArea(self, ANCHO - 200, 399)
        self.properties.add(self.modify_area, layer=2)

        self.f = font.SysFont('Verdana', 16)
        self.f.set_underline(True)
        self.write(self.name + ' Panel', self.f, centerx=self.rect.centerx, y=0)

        self.planet_area = PlanetArea(self, ANCHO - 200, 32)
        self.properties.add(self.planet_area, layer=2)

        self.orbits = []
        self._loaded_orbits = []
        self.buttons = WidgetGroup()
        self.markers = []
        self.orbit_descriptions = WidgetGroup()
        self.markers_button = ShowMarkersButton(self, 3, 421)
        self.properties.add(self.markers_button, layer=2)
        self.markers_button.disable()

        self.add_orbits_button = AddOrbitButton(self, ANCHO - 100, 416)
        self.properties.add(self.add_orbits_button, layer=2)
        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.save_orbits, 'Save')
        EventHandler.register(self.load_orbits, 'LoadData')

    def write(self, text, fuente, **kwargs):
        render = fuente.render(text, True, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(**kwargs)
        self.image.blit(render, render_rect)

    def populate(self):
        markers = {'Inner Boundary': system.star.inner_boundry,
                   'Habitable Inner': system.star.habitable_inner,
                   'Habitable Outer': system.star.habitable_outer,
                   'Frost Line': system.star.frost_line,
                   'Outer Boundary': system.star.outer_boundry}

        for i, marker in enumerate(markers, start=1):
            x = OrbitMarker(self, marker, markers[marker])
            x.locked = True
            self.markers.append(x)
            self.properties.add(x, layer=2)
        self.sort_markers()

    def add_orbit_marker(self, position):
        inner = system.star.inner_boundry
        outer = system.star.outer_boundry
        if type(position) is q:
            is_orbit = True
            is_complete_orbit = False
            test = inner < position < outer
        else:  # type(position) is PlanetOrbit
            is_orbit = False
            is_complete_orbit = True
            test = inner < position.semi_major_axis < outer

        if test is True:
            new = OrbitMarker(self, 'Orbit', position, is_orbit=is_orbit, is_complete_orbit=is_complete_orbit)
            self.markers.append(new)
            self.orbits.append(new)
            self.sort_markers()
            self.add_button_and_type(new)
            self.properties.add(new, layer=2)
            return True
        return False

    def add_button_and_type(self, marker):
        orbit_type = OrbitType(self)
        button = OrbitButton(self)
        self.buttons.add(button)

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
            if not self.marker_area.contains(marker.rect):
                marker.hide()
            else:
                marker.show()

    def sort_buttons(self):
        x, y = 3, 442
        for bt in sorted(self.buttons.widgets(), key=lambda b: b.get_value()):
            bt.move(x, y)
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
            idx = self.markers.index(marker)
            del self.markers[idx]
            self.sort_markers()
            self.sort_buttons()

    def on_mousebuttondown(self, event):
        last_is_hidden = not self.markers[-1].is_visible
        if len(self.markers) > 16 and event.button in (4, 5):
            if event.button == 4 and self.offset < 0:
                self.offset += 20
            elif event.button == 5 and last_is_hidden:
                self.offset -= 20

            self.sort_markers()

        elif event.button == 1:
            for marker in self.markers:
                marker.deselect()
                marker.enable()
            self.add_orbits_button.unlink()

    def check_orbits(self):
        self.orbits.sort(key=lambda o: o.value.m)
        for x, p in enumerate(self.orbits[1:], start=1):
            a = self.orbits[x - 1].value.m if x > 0 and len(self.orbits) else self.orbits[0].value.m  # el anterior
            assert a + 0.15 < p.value.m, 'Orbit @' + str(p.value.m) + ' is too close to Orbit @' + str(a)

            if x + 1 < len(self.orbits):
                b = self.orbits[x + 1].value.m  # el posterior
                assert p.value.m < b - 0.15, 'Orbit @' + str(p.value.m) + ' is too close to Orbit @' + str(b)

    def cycle(self, delta):
        if 0 <= self.curr_idx + delta < len(self.markers):
            self.curr_idx += delta
            self.current = self.markers[self.curr_idx]
            return self.current.value

    def get_idx(self, marker):
        """
        :type marker: OrbitMarker
        """
        self.curr_idx = self.markers.index(marker)

    def get_disabled(self):
        markers = self.markers.copy()
        markers.sort(key=lambda m: m.enabled)
        self.get_idx(markers[0])

    def anchor_maker(self, marker):
        self.get_idx(marker)

        self.add_orbits_button.link(marker.value)
        self.modify_area.link(marker)

        self.add_orbits_button.enable()
        self.add_orbits_button.unlock()

    def clear(self, event):
        if event.data['panel'] is self:
            for marker in self.markers:
                marker.kill()
            for orbit in self.buttons:
                orbit.kill()
            self.markers.clear()
            self.populate()

    def save_orbits(self, event):
        orbits = []
        for marker in self.orbits:
            orb = marker.orbit
            d = {}
            if hasattr(orb, 'semi_major_axis'):
                d['a'] = orb.semi_major_axis.m
            if hasattr(orb, 'inclination'):
                d['i'] = orb.inclination.m
            if hasattr(orb, 'eccentricity'):
                d['e'] = orb.eccentricity.m
            if hasattr(orb, 'planet'):
                d['planet'] = orb.planet.name
            orbits.append(d)

        EventHandler.trigger(event.tipo + 'Data', 'Orbit', {'Star': {'Orbits': orbits}})

    def load_orbits(self, event):
        for position in event.data['Star']['Orbits']:
            self._loaded_orbits.append(position)

    def set_loaded_orbits(self):
        for orbit_data in self._loaded_orbits:
            a = q(orbit_data['a'], 'au')
            if 'e' not in orbit_data:
                self.add_orbit_marker(a)
            else:
                e = q(orbit_data['e'])
                i = q(orbit_data['i'], 'degree')
                planet = system.get_planet_by_name(orbit_data['planet'])
                planet.set_orbit(system.star, [a, e, i])
                self.add_orbit_marker(planet.orbit)
                self.planet_area.delete_planet(planet)

        # borrar las órbitas cargadas para evitar que se dupliquen.
        self._loaded_orbits.clear()

    def show(self):
        if system is not None and not self.markers:
            self.populate()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()
        self.visible_markers = True
        if len(self._loaded_orbits):
            self.set_loaded_orbits()
        self.markers_button.show()

        super().show()

    def hide(self):
        super().hide()
        for item in self.properties.widgets():
            item.hide()

    def toggle_markers(self):
        if self.visible_markers:
            for marker in self.markers:
                marker.hide()
        else:
            for orbit_type in self.orbit_descriptions.widgets():
                orbit_type.hide()
            for marker in self.markers:
                marker.show()
            self.unlock_every_button()
            self.markers_button.disable()
        self.visible_markers = not self.visible_markers

    def hide_orbit_types(self):
        for orbit_type in self.orbit_descriptions.widgets():
            orbit_type.hide()
        for orbit_button in self.buttons.widgets():
            orbit_button.unlock()

    def unlock_every_button(self):
        for orbit_button in self.buttons.widgets():
            orbit_button.unlock()

    def link_planet_to_orbit(self, planet):
        locked = [i for i in self.buttons.widgets() if i.locked]
        if len(locked):
            locked[0].linked_marker.orbit = PseudoOrbit(locked[0].linked_marker.orbit)
            locked[0].linked_type.show()
            locked[0].linked_type.link_planet(planet)

    def update(self):
        self.image.fill(COLOR_BOX, self.marker_area)

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


class OrbitType(BaseWidget, Intertwined):
    linked_planet = None
    locked = True

    modifiable = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()

    def link_planet(self, planet):
        self.linked_planet = planet
        self.locked = False

    def create(self):
        orbit = self.linked_marker.orbit
        self.clear()
        props = ['semi_major_axis', 'semi_minor_axis', 'eccentricity', 'inclination',
                 'periapsis', 'apoapsis', 'motion', 'temperature', 'velocity', 'period',
                 'planet']
        for i, prop in enumerate([j for j in props if hasattr(orbit, j)]):
            value = getattr(orbit, prop)
            vt = ValueText(self, prop, 3, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            vt.text_area.set_value(value)
            vt.text_area.update()
            self.properties.add(vt)

    def fill(self):
        parametros = []
        for elemento in self.properties.widgets():
            if elemento.text == 'inclination':
                value = q(0 if elemento.text_area.value == '' else elemento.text_area.value, 'degree')
            elif elemento.text not in ['motion', 'temperature']:
                value = q(elemento.text_area.value)
            else:
                value = 'au'
            parametros.append(value)
        orbit = self.linked_planet.set_orbit(system.star, parametros)
        self.linked_marker.orbit = orbit
        self.show()
        self.parent.planet_area.delete_planet(self.linked_planet)
        self.locked = True

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

    locked = False
    orbit = None

    def __init__(self, parent, name, value, is_orbit=False, is_complete_orbit=False):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 16)
        self.f2 = font.SysFont('Verdana', 16, bold=True)
        self.name = name
        self._value = value
        if is_orbit:
            self.orbit = RawOrbit(round(value, 3))
            self.text = '{:~}'.format(value)
        elif is_complete_orbit:
            self.orbit = value
            self.text = '{:~}'.format(value.a)
        else:
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
            self.select()
            if self.locked:
                self.disable()
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
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, COLOR_TEXTO, COLOR_BOX)
        super().update()
        if self.selected:
            self.image = self.img_sel

    def __repr__(self):
        return self.name + ' @' + self.text


class OrbitButton(Meta, BaseWidget, Intertwined):
    locked = False
    hidden = False

    def __init__(self, parent):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 14)
        self.f2 = font.SysFont('Verdana', 14, bold=True)
        self.image = self.img_uns
        self._rect = Rect(3, 442, 0, 21)

    def link_marker(self, marker):
        super().link_marker(marker)
        self.create()

    def get_value(self):
        return self.linked_marker.orbit.semi_major_axis.m

    def create(self):
        orbit = self.linked_marker.orbit.semi_major_axis
        t = 'Orbit @{:~}'.format(round(orbit, 3))
        self.img_uns = self.f1.render(t, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(t, True, COLOR_TEXTO, COLOR_AREA)
        self.img_dis = self.f1.render(t, True, COLOR_DISABLED, COLOR_AREA)
        self.rect = self.img_uns.get_rect(topleft=self._rect.topleft)

    def move(self, x, y):
        self._rect.topleft = x, y
        self.create()

    def show(self):
        super().show()
        self.hidden = False

    def hide(self):
        super().hide()
        self.hidden = True

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.parent.visible_markers:
                self.parent.toggle_markers()
            self.parent.hide_orbit_types()
            self.parent.markers_button.enable()
            self.linked_type.show()
            self.lock()

    def update(self):
        if not self.locked:
            super().update()
            self.create()
            self.selected = False

    def __repr__(self):
        return 'B.Orbit @' + str(self.get_value())


class ShowMarkersButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        f1 = font.SysFont('Verdana', 14)
        f2 = font.SysFont('Verdana', 14, bold=True)
        self.img_uns = f1.render('Markers', True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = f2.render('Markers', True, COLOR_TEXTO, COLOR_AREA)
        self.img_dis = f1.render('Markers', True, COLOR_DISABLED, COLOR_AREA)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.toggle_markers()


class PlanetArea(BaseWidget):

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((200, 350))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.listed_planets = WidgetGroup()

        self.f = font.SysFont('Verdana', 14)
        self.f.set_underline(True)
        self.write('Planets', self.f, midtop=(self.rect.w / 2, 0))

    def write(self, text, fuente, **kwargs):
        render = fuente.render(text, True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(**kwargs)
        self.image.blit(render, render_rect)

    def populate(self):
        planets = [i for i in system.planets if i.orbit is None]
        for i, planet in enumerate(planets):
            listed = ListedPlanet(self, planet, self.rect.x + 3, i * 16 + self.rect.y + 21)
            self.listed_planets.add(listed)
            listed.show()

    def show(self):
        self.populate()
        super().show()

    def hide(self):
        for listed in self.listed_planets.widgets():
            listed.hide()
        super().hide()

    def delete_planet(self, planet):
        for listed in self.listed_planets.widgets():
            if listed.planet_data == planet:
                listed.kill()


class ListedPlanet(PlanetButton):
    def on_mousebuttondown(self, event):
        if not self.parent.parent.visible_markers:
            self.enabled = False
            self.parent.parent.link_planet_to_orbit(self.planet_data)

    def update(self):
        if self.enabled:
            if self.selected:
                self.image = self.img_sel
            else:
                self.image = self.img_uns
            self.selected = False


class AddOrbitButton(TextButton):
    value = 'Inward'
    anchor = None
    locked = False

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Orbit', x, y)

    def on_mousebuttondown(self, event):
        factor = round(roll(1.4, 2.0), 2)
        if event.button == 1 and self.enabled and not self.locked:
            if self.value == 'Inward':
                do_link = self.parent.add_orbit_marker(self.anchor / factor)
                if do_link:
                    self.link(self.parent.cycle(-1))
                else:
                    self.parent.get_disabled()
                    self.switch()
                    self.on_mousebuttondown(event)

            elif self.value == 'Outward':
                do_link = self.parent.add_orbit_marker(self.anchor * factor)
                if do_link:
                    self.link(self.parent.cycle(+1))
                else:
                    self.parent.get_disabled()
                    self.on_mousebuttondown(event)
            self.parent.check_orbits()

    def switch(self):
        if self.value == 'Inward':
            self.value = 'Outward'
        else:
            self.value = 'Inward'

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def link(self, orbit):
        self.anchor = orbit

    def unlink(self):
        self.anchor = None
        self.lock()
        self.disable()


class ModifyArea(BaseWidget):
    marker = None

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((32, 20))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        delta = 0
        if event.button == 4:
            delta = -1
        elif event.button == 5:
            delta = +1
        self.marker.tune_value(delta)

    def link(self, marker):
        self.marker = marker

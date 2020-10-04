from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, COLOR_AREA, COLOR_DISABLED
from engine.frontend.globales import Renderer, WidgetHandler, ANCHO, ALTO
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.widgets.basewidget import BaseWidget
from engine.frontend.globales.group import WidgetGroup
from engine.backend.eventhandler import EventHandler
from engine.equations.planetary_system import system
from engine.equations.orbit import RawOrbit
from pygame import Surface, font, Rect
from engine.backend import roll
from ..values import ValueText
from .planet_panel import Meta
from engine import q


class OrbitPanel(BaseWidget):
    current = None
    curr_idx = 0
    _loaded_orbits = None

    curr_x = 3
    curr_y = 421+21

    visible_markers = True
    current_orbit = None

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])

        self.f = font.SysFont('Verdana', 16)
        self.f.set_underline(True)
        self.write(self.name + ' Panel', self.f, centerx=self.rect.centerx, y=0)

        self.orbits = []
        self._loaded_orbits = []
        self.properties = WidgetGroup()
        self.buttons = WidgetGroup()
        self.markers = []
        self.orbit_descriptions = WidgetGroup()
        self.markers_button = ShowMarkersButton(self, 3, 421)

        centerx = self.rect.centerx
        self.antes = PositionButton(self, 'Inward', 550)
        self.despues = PositionButton(self, 'Outward', 550)
        self.antes.rect.right = centerx - 2
        self.despues.rect.left = centerx
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
        self.sort_markers()

    def add_orbit_marker(self, position):
        inner = system.star.inner_boundry
        outer = system.star.outer_boundry
        if inner < position < outer:
            new = OrbitMarker(self, 'Orbit', round(position, 3), is_orbit=True)
            self.markers.append(new)
            self.orbits.append(new)
            self.sort_markers()
            self.add_button(new)
            return True
        return False

    def add_button(self, marker):
        orbit_type = OrbitType(self)
        button = OrbitButton(self, self.curr_x, self.curr_y)
        orbit_type.link_buton(button)
        button.link_type(orbit_type)
        orbit_type.link_marker(marker)
        button.link_marker(marker)
        self.orbit_descriptions.add(orbit_type)
        if self.curr_x + button.rect.w + 10 < self.rect.w - button.rect.w + 10:
            self.curr_x += button.rect.w + 10
        else:
            self.curr_x = 0
            self.curr_y += 32
        self.buttons.add(button)
        button.enable()
        button.show()

    def sort_markers(self):
        self.markers.sort(key=lambda m: m.value)
        for i, marker in enumerate(self.markers, start=1):
            marker.rect.y = i * 2 * 10 + 50

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

    def enable_all(self):
        for marker in self.markers:
            marker.enable()

        self.antes.lock()
        self.despues.lock()

    def disable_all(self):
        for marker in self.markers:
            marker.disable()

        self.antes.lock()
        self.despues.lock()

    def anchor_maker(self, marker):
        self.get_idx(marker)

        self.antes.link(marker.value)
        self.despues.link(marker.value)

        self.antes.show()
        self.despues.show()

    def clear(self, event):
        if event.data['panel'] is self:
            for marker in self.markers:
                marker.kill()
            self.markers.clear()
            self.populate()

    def save_orbits(self, event):
        data = {'Star': {'Orbits': [marker.orbit.semi_major_axis.m for marker in self.orbits]}}
        EventHandler.trigger(event.tipo + 'Data', 'Orbit', data)

    def load_orbits(self, event):
        for position in event.data['Star']['Orbits']:
            self._loaded_orbits.append(position)

    def set_loaded_orbits(self):
        for position in self._loaded_orbits:
            self.add_orbit_marker(q(position, 'au'))

        # borrar las órbitas cargadas para evitar que se dupliquen.
        self._loaded_orbits.clear()

    def show(self):
        if system is not None and not self.markers:
            self.populate()
        for marker in self.markers:
            marker.show()
        if len(self._loaded_orbits):
            self.set_loaded_orbits()
        self.markers_button.show()

        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
        for marker in self.markers:
            marker.hide()
        self.antes.hide()
        self.despues.hide()
        self.markers_button.hide()

    def toggle_markers(self):
        if self.visible_markers:
            for marker in self.markers:
                marker.hide()
            self.visible_markers = False
        else:
            for orbit_type in self.orbit_descriptions.widgets():
                orbit_type.hide()
            for marker in self.markers:
                marker.show()
            self.visible_markers = True

    def hide_orbit_types(self):
        for orbit_type in self.orbit_descriptions.widgets():
            orbit_type.hide()

    def __repr__(self):
        return 'Orbit Panel'


class OrbitType(BaseWidget):
    linked_button = None
    linked_marker = None

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()

    def link_buton(self, button):
        """
        @type button: OrbitButton
        """
        self.linked_button = button

    def link_marker(self, marker):
        """
        @type marker: OrbitMarker
        """
        self.linked_marker = marker

    def create(self):
        orbit = self.linked_marker.orbit
        self.properties.empty()
        props = ['semi_major_axis', 'semi_minor_axis', 'eccentricity', 'inclination',
                 'periapsis', 'apoapsis', 'motion', 'temperature']
        for i, prop in enumerate([j for j in props if hasattr(orbit, j)]):
            _value = getattr(orbit, prop)
            vt = ValueText(self, prop, 3, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            value = _value
            if not type(_value) is str:
                value = str(round(_value, 3))
            vt.text_area.value = value
            vt.text_area.inner_value = _value if type(_value) is not str else None
            vt.text_area.update()
            self.properties.add(vt)

    def clear(self):
        self.properties.empty()

    def show(self):
        self.create()

        for p in self.properties.widgets():
            p.show()

    def hide(self):
        self.clear()


class OrbitMarker(Meta, BaseWidget, IncrementalValue):
    enabled = True
    name = ''

    locked = False
    orbit = None

    def __init__(self, parent, name, value, is_orbit=False):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 15)
        self.f2 = font.SysFont('Verdana', 15, bold=True)
        self.text = '{:~}'.format(value)
        self.name = name
        self._value = value
        if is_orbit:
            self.orbit = RawOrbit(value)
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)
        Renderer.add_widget(self, layer=50)
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
        self.enabled = not self.enabled

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.locked:
                self.disable()
            self.parent.anchor_maker(self)

        elif not self.locked:
            self.increment = self.update_increment()

            if event.button == 4:
                self.increment *= -1

            elif event.button == 5:
                self.increment *= +1

            self.value += q(self.increment, self.value.u)
            self.increment = 0
            self.parent.sort_markers()

    def update(self):
        super().update()
        self.reset_power()
        self.text = '{:~}'.format(self.value)
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, COLOR_TEXTO, COLOR_BOX)

    def __repr__(self):
        return self.name + ' @' + self.text


class PositionButton(Meta, BaseWidget):
    enabled = True
    anchor = None
    locked = False

    def __init__(self, parent, value, y):
        super().__init__(parent)
        self.f = font.SysFont('Verdana', 14)
        self.value = value
        self.img_sel = self.f.render(value, True, (255, 255, 255), (0, 125, 255))
        self.img_uns = self.f.render(value, True, (255, 255, 255), (125, 125, 255))
        self.image = self.img_uns
        self.rect = self.image.get_rect(y=y)

    def on_mousebuttondown(self, event):
        factor = round(roll(1.4, 2.0), 2)
        if event.button == 1 and not self.locked:
            if self.value == 'Inward':
                do_link = self.parent.add_orbit_marker(self.anchor / factor)
                if do_link:
                    self.link(self.parent.cycle(-1))
                else:
                    self.parent.get_disabled()
                    self.hide()
                    if not self.parent.despues.is_visible:
                        self.parent.enable_all()

            elif self.value == 'Outward':
                do_link = self.parent.add_orbit_marker(self.anchor * factor)
                if do_link:
                    self.link(self.parent.cycle(+1))
                else:
                    self.parent.get_disabled()
                    self.hide()
                    if not self.parent.antes.is_visible:
                        self.parent.enable_all()

    def link(self, orbit):
        self.anchor = orbit

    def lock(self):
        self.locked = True


class OrbitButton(Meta, BaseWidget):
    locked = False
    hidden = False

    linked_type = None
    linked_marker = None

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 14)
        self.f2 = font.SysFont('Verdana', 14, bold=True)
        self.image = self.img_uns
        self._rect = Rect(x, y, 0, 21)

    def link_type(self, orbit_type):
        """
        @type orbit_type: OrbitType
        """
        self.linked_type = orbit_type

    def link_marker(self, marker):
        """
        @type marker: OrbitMarker
        """
        self.linked_marker = marker
        self.create()

    def create(self):
        orbit = self.linked_marker.orbit.semi_major_axis
        t = 'Orbit @{:~}'.format(round(orbit, 3))
        self.img_uns = self.f1.render(t, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(t, True, COLOR_TEXTO, COLOR_AREA)
        self.img_dis = self.f1.render(t, True, COLOR_DISABLED, COLOR_AREA)
        self.rect = self.img_uns.get_rect(topleft=self._rect.topleft)

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
            self.linked_type.show()

    def update(self):
        super().update()
        self.create()
        if not self.locked:
            self.selected = False


class ShowMarkersButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        f1 = font.SysFont('Verdana', 14)
        f2 = font.SysFont('Verdana', 14, bold=True)
        self.img_uns = f1.render('Markers', True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = f2.render('Markers', True, COLOR_TEXTO, COLOR_AREA)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.toggle_markers()

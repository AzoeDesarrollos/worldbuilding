from engine.frontend.globales import Renderer, WidgetHandler, ANCHO, ALTO, COLOR_TEXTO, COLOR_BOX, COLOR_AREA
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.widgets.basewidget import BaseWidget
from engine.frontend.globales.group import WidgetGroup
from engine.backend.eventhandler import EventHandler
from engine.equations.planetary_system import system
from engine.equations.orbit import RawOrbit
from pygame import Surface, font
from engine.backend import roll
# from ..values import ValueText
from .planet_panel import Meta
from engine import q


class OrbitPanel(BaseWidget):
    current = None
    curr_idx = 0
    _loaded_orbits = None

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
        self.markers = []

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
            self.orbits.append(new.value)
            self.sort_markers()
            return True
        return False

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
        EventHandler.trigger(event.tipo + 'Data', 'Orbit', {'Star': {'Orbits': [orbit.m for orbit in self.orbits]}})

    def load_orbits(self, event):
        for position in event.data['Star']['Orbits']:
            self._loaded_orbits.append(position)

    def set_loaded_orbits(self):
        for position in self._loaded_orbits:
            self.add_orbit_marker(q(position, 'au'))

    def show(self):
        if system is not None and not self.markers:
            self.populate()
        for marker in self.markers:
            marker.show()
        if len(self._loaded_orbits):
            self.set_loaded_orbits()

        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
        for marker in self.markers:
            marker.hide()
        self.antes.hide()
        self.despues.hide()

    def __repr__(self):
        return 'Orbit Panel'


# class OrbitType(BaseWidget):
#     def __init__(self, parent, orbit):
#         super().__init__(parent)
#         self.data = orbit
#         self.properties = WidgetGroup()
#         self.create()
#
#     def create(self):
#         props = ['semi_major_axis', 'semi_minor_axis', 'eccentricity', 'inclination',
#                  'periapsis', 'apoapsis', 'motion', 'temperature']
#         for i, prop in enumerate([j for j in props if hasattr(self.data, j)]):
#             _value = getattr(self.data, prop)
#             vt = ValueText(self, prop, 0, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
#             value = _value
#             if not type(_value) is str:
#                 value = str(round(_value, 3))
#             vt.text_area.value = value
#             vt.text_area.inner_value = _value if type(_value) is not str else None
#             vt.text_area.update()
#             self.properties.add(vt)
#
#     def fill(self):
#         for elemento in self.properties.widgets():
#             if elemento.text not in ['motion', 'temperature']:
#                 value = q(*elemento.text_area.value.split(' '))
#             else:
#                 value = str(elemento.text_area.value)
#             setattr(self.data, elemento.text.lower(), value)
#             self.parent.reverse_match(self.data)
#             elemento.text_area.value = value
#             elemento.text_area.update_inner_value(value)
#             elemento.text_area.update()
#             elemento.text_area.show()
#
#     def clear(self):
#         self.properties.empty()
#
#     def show(self):
#         if not len(self.properties):
#             self.create()
#
#         for p in self.properties.widgets():
#             p.show()
#
#     def hide(self):
#         for p in self.properties.widgets():
#             p.text_area.hide()
#             p.hide()


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
            return round(self.orbit.a, 3)
        else:
            return self._value

    @value.setter
    def value(self, new_value):
        if self.orbit is not None:
            self.orbit.a = new_value

    def disable(self):
        self.enabled = not self.enabled

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.locked:
                self.disable()
            self.parent.anchor_maker(self)

        elif not self. locked:
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

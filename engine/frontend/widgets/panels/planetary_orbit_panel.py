from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_SELECTED, COLOR_TEXTO
from engine.frontend.globales import Renderer, WidgetHandler, WidgetGroup
from engine.frontend.widgets.incremental_value import IncrementalValue
from .common import AvailableObjects, AvailablePlanet, ModifyArea
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.frontend.widgets.meta import Meta
from pygame import Surface, Rect
from engine import q, roll


class PlanetaryOrbitPanel(BaseWidget):
    skippable = True
    skip = False
    current = None
    markers = None

    curr_x = 0
    curr_y = 0

    added = None

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Planetary Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.buttons = WidgetGroup()
        self.markers = []
        self.added = []
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 58, 380, 20 * 16)
        self.curr_x = self.area_buttons.x + 3
        self.curr_y = self.area_buttons.y + 21
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 350)
        self.f = self.crear_fuente(16, underline=True)
        f = self.crear_fuente(14, underline=True)
        self.write(self.name + ' Panel', self.f, centerx=(ANCHO // 4) * 1.5, y=0)
        self.write('Satellites', f, bg=COLOR_AREA, x=3, y=self.area_buttons.y)
        self.properties.add(self.planet_area, layer=2)
        self.objects = []
        self.area_modify = ModifyArea(self, ANCHO - 200, 399)
        self.properties.add(self.area_modify, layer=2)

    def populate(self):
        planet = self.current
        markers = {
            'Hill Sphere': planet.hill_sphere
        }
        for i, marker in enumerate(markers, start=1):
            x = Marker(self, marker, markers[marker])
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

    def hide(self):
        super().hide()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.hide()

    def select_planet(self, planet):
        if planet is not self.current:
            self.current = planet
            self.populate()
        for button in self.buttons.widgets():
            button.enable()

    def anchor_maker(self, marker):
        self.area_modify.link(marker)
        self.area_modify.visible_markers = True

    def deselect_markers(self, m):
        for marker in self.markers:
            marker.deselect()
            marker.enable()
        m.select()

    def sort_markers(self):
        self.markers.sort(key=lambda m: m.value.m)
        for i, marker in enumerate(self.markers, start=1):
            marker.rect.y = i * 2 * 10 + 38  # + self.offset
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

    def add_new(self, obj):
        if obj not in self.added:
            self.added.append(obj)
        obj_name = obj.cls
        obj_density = obj.density.to('earth_density').m
        pln_habitable = Systems.get_current().is_habitable(self.current)
        pln_hill = self.current.hill_sphere.m
        obj_type = obj.celestial_type
        roches = self.current.set_roche(obj_density)

        text = "A satellite's mass must be less than or equal to the\nmass of the planet."
        text += '\n\nConsider using a less massive satellite for this planet.'
        assert self.current.mass.m >= obj.mass.m, text

        pos = q(round(roll(self.current.roches_limit.m, self.current.hill_sphere.m/2), 3), 'earth_radius')

        obj_marker = Marker(self, obj_name, pos, color=COLOR_SELECTED, lock=False)
        roches_marker = Marker(self, "Roche's Limit", roches, lock=True)

        max_value = pln_hill
        if pln_habitable and obj_type != 'asteroid':
            max_value /= 2
        obj_marker.set_max_value(max_value)
        obj_marker.set_min_value(roches.m)

        self.markers.append(obj_marker)
        self.properties.add(obj_marker, layer=2)

        first = self.markers[0]
        if first.name == "Roche's Limit":
            self.properties.remove(first)
            self.markers[0] = roches_marker
            self.properties.add(roches_marker, layer=2)
        else:
            self.markers.append(roches_marker)
            self.properties.add(roches_marker, layer=2)
        self.sort_markers()

    def is_added(self, obj):
        return obj in self.added


class OrbitablePlanet(AvailablePlanet):
    def on_mousebuttondown(self, event):
        self.parent.parent.select_planet(self.object_data)


class AvailablePlanets(AvailableObjects):
    listed_type = OrbitablePlanet
    name = 'Planets'

    def show(self):
        system = Systems.get_current()
        if system is not None:
            planets = [planet for planet in system.planets if planet.hill_sphere != 0]
            if not len(self.listed_objects.get_widgets_from_layer(Systems.get_current_idx())):
                self.populate(planets)
        super().show()


class ObjectButton(Meta):
    enabled = False

    def __init__(self, parent, obj, x, y):
        super().__init__(parent)
        self.object_data = obj
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.img_uns = self.f1.render(obj.cls, True, obj.color, COLOR_AREA)
        self.img_sel = self.f2.render(obj.cls, True, obj.color, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if not self.parent.is_added(self.object_data) and self.parent.current is not None:
            self.parent.add_new(self.object_data)

    def move(self, x, y):
        self.rect.topleft = x, y


class Marker(Meta, IncrementalValue):
    locked = True
    enabled = True
    text = ''
    color = COLOR_TEXTO
    max_value = None
    min_value = None

    def __init__(self, parent, name, value, color=None, lock=True):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.name = name
        self._value = value.m
        self.unit = value.u

        if not lock:
            self.locked = False
            self.color = color
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def set_max_value(self, value):
        self.max_value = value

    def set_min_value(self, value):
        self.min_value = value

    @property
    def value(self):
        return q(self._value, self.unit)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if not self.locked:
                self.parent.deselect_markers(self)
                self.parent.anchor_maker(self)

        # elif event.button == 3:
        #     self.parent.delete_marker(self)

        return self

    def tune_value(self, delta):
        if not self.locked:
            self.increment = self.update_increment()
            self.increment *= delta
            t = 'Regular satellites must orbit close to their planet, that is within half of the maximun value.'
            t += '\n\nTry moving the satellite to a lower orbit.'
            test = self._value + self.increment >= 0 and self.min_value < self._value + self.increment < self.max_value
            assert test(t)
            self._value += self.increment
            self.increment = 0
            self.parent.sort_markers()

    def update(self):
        self.reset_power()
        self.text = '{:~}'.format(round(self.value, 3))
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        super().update()
        if self.selected:
            self.image = self.img_sel

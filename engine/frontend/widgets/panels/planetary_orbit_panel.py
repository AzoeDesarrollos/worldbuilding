from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_SELECTED, COLOR_TEXTO
from engine.frontend.globales import Renderer, WidgetHandler, WidgetGroup
from engine.frontend.widgets.incremental_value import IncrementalValue
from .common import AvailableObjects, AvailablePlanet, Meta
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from pygame import Surface, Rect
from math import pow
from engine import q


class PlanetaryOrbitPanel(BaseWidget):
    skippable = True
    skip = False
    current = None
    markers = []

    curr_x = 0
    curr_y = 0

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Planetary Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.buttons = WidgetGroup()
        self.markers = []
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 58, 380, 20 * 16)
        self.curr_x = self.area_buttons.x + 3
        self.curr_y = self.area_buttons.y + 21
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 350)
        self.f = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', self.f, centerx=(ANCHO // 4) * 1.5, y=0)
        self.properties.add(self.planet_area, layer=2)

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
        for obj in Systems.get_current().satellites + Systems.get_current().asteroids:
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
        self.current = planet
        self.populate()

    def sort_markers(self):
        self.markers.sort(key=lambda m: m.value)
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
        obj_name = obj.cls
        obj_density = obj.density.to('earth_density').m
        pln_density = self.current.density.to('earth_density').m
        pln_radius = self.current.radius.to('earth_radius').m
        roche = q(round(2.44 * pln_radius * pow(obj_density / pln_density, 1 / 3), 3), 'earth_radius')

        x = Marker(self, obj_name, roche, color=COLOR_SELECTED, lock=False)
        self.markers.append(x)
        self.properties.add(x, layer=2)
        self.sort_markers()


class OrbitablePlanet(AvailablePlanet):
    def on_mousebuttondown(self, event):
        self.parent.parent.select_planet(self.object_data)


class AvailablePlanets(AvailableObjects):
    listed_type = OrbitablePlanet
    name = 'Planets'

    def show(self):
        planets = [planet for planet in Systems.get_current().planets if planet.hill_sphere != 0]
        if not len(self.listed_objects.get_widgets_from_layer(Systems.get_current_idx())):
            self.populate(planets)
        super().show()


class ObjectButton(Meta, BaseWidget):
    enabled = True

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
        self.parent.add_new(self.object_data)

    def move(self, x, y):
        self.rect.topleft = x, y


class Marker(BaseWidget, Meta, IncrementalValue):
    locked = True
    text = ''
    color = COLOR_TEXTO

    def __init__(self, parent, name, value, color=None, lock=True):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.name = name
        self.value = value

        if not lock:
            self.locked = False
            self.color = color
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def on_mousebuttondown(self, event):
        if not self.locked:
            self.increment = self.update_increment()
            if event.button == 5:  # rueda abajo
                self.value += self.increment
                self.increment = 0
            elif event.button == 4 and self.value > 0:  # rueda arriba
                self.value -= self.increment
                self.increment = 0

            if event.button in (4, 5):
                self.value = round(self.value, 4)

    def update(self):
        self.reset_power()
        self.text = '{:~}'.format(self.value)
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        super().update()
        if self.selected:
            self.image = self.img_sel

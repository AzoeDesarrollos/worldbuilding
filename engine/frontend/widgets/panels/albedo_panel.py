from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup, color_areas as k
from engine.frontend.widgets import BaseWidget, ValueText
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from .common import ListedArea, ColoredBody
from pygame import Surface, Rect
from ..pie import PieChart as Pc
from engine import albedos


class AlbedoPanel(BaseWidget):
    skippable = True  # initially, we only care for the albedo of habitable planets,
    # this may change in the future because the albedo (bond) also affects the object's visibility.
    skip = False

    current = None
    locked = False

    def __init__(self, parent):
        self.name = 'Albedo'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(15, underline=True, bold=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5)

        self.properties = WidgetGroup()
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 300)
        self.properties.add(self.planet_area, layer=2)

        h = round((ALTO - 32 - 32) / 3)
        a1 = Rect(0, 32, ANCHO - self.planet_area.rect.w, h)
        b0 = Rect(0, a1.bottom, ANCHO - self.planet_area.rect.w, h)
        b1 = Rect(0, a1.bottom, b0.w / 2, h)
        b1.right = b0.right
        b2 = Rect(0, a1.bottom, b0.w / 2, h / 2)
        b3 = Rect(0, b2.bottom, b0.w / 2, h / 2)

        self.charts = WidgetGroup()

        # Section A
        d = {'Land': 50, 'Ocean': 50}  # "clouds" is a single value
        ks = [[128, 64, 0], [0, 183, 235]]
        self.pie_coverage = Pc(self, b2.centerx+150, a1.centery - 20, b3.h / 1.4, d,
                               use_handlers=1, colors=ks, is_set=0)
        self.charts.add(self.pie_coverage)

        # Section B
        n = sorted(albedos.keys())
        x, y = 'names', 'colors'
        a = {x: {n[4]: 50, n[5]: 50}, y: [k[i] for i in [4, 5]]}
        b = {x: {n[0]: 16, n[1]: 17, n[2]: 16, n[3]: 17, n[6]: 17, n[9]: 17}, y: [k[i] for i in [0, 1, 2, 3, 6, 9]]}
        c = {x: {n[7]: 50, n[8]: 50}, y: [k[i] for i in [7, 8]]}

        u = [b1.center, b2.center, b3.center]
        self.pie_ocean = Pc(self, u[1][0] + 150, u[1][1] - 30, b2.h / 2, a[x], use_handlers=True, colors=a[y], is_set=0)
        self.pie_land = Pc(self, u[0][0] + 50, u[0][1] + 170, b1.h / 2, b[x], use_handlers=True, colors=b[y], is_set=0)
        self.pie_clouds = Pc(self, u[1][0] + 150, u[2][1], b3.h / 2, c[x], use_handlers=True, colors=c[y], is_set=0)
        self.charts.add(self.pie_ocean, self.pie_land, self.pie_clouds)

        for piechart in self.charts.widgets():
            for obj in piechart.chart.widgets():
                self.properties.add(obj, layer=3)

        r = self.write('Global Coverage', f2, x=3, y=64)
        for i, arc in enumerate(self.pie_coverage.arcs):
            name = arc.name
            vt = ValueText(self, name, 3, i * 20 + r.bottom, size=14)
            vt.value = arc.get_value()
            vt.modifiable = False
            EventHandler.register(vt.text_area.get_value_from_event, "SetValue")
            self.properties.add(vt, layer=2)
        vt = ValueText(self, 'Clouds', 3, 2 * 20 + r.bottom, size=14)
        vt.modifiable = True
        vt.value = '50%'
        self.properties.add(vt, layer=2)

        r = self.write('Ocean Breakdown', f2, x=3, y=6 * 20 + r.bottom)
        for i, arc in enumerate(self.pie_ocean.arcs):
            name = arc.name
            vt = ValueText(self, name, 3, i * 20 + r.bottom, size=14)
            vt.value = arc.get_value()
            vt.modifiable = False
            EventHandler.register(vt.text_area.get_value_from_event, "SetValue")
            self.properties.add(vt, layer=2)

        r = self.write('Clouds Breakdown', f2, x=3, y=6 * 20 + r.bottom)
        for i, arc in enumerate(self.pie_clouds.arcs):
            name = arc.name
            vt = ValueText(self, name, 3, i * 20 + r.bottom, size=14)
            vt.value = arc.get_value()
            vt.modifiable = False
            EventHandler.register(vt.text_area.get_value_from_event, "SetValue")
            self.properties.add(vt, layer=2)

        r = self.write('Land Breakdown', f2, x=3, y=4 * 20 + r.bottom)
        for i, arc in enumerate(self.pie_land.arcs):
            name = arc.name
            vt = ValueText(self, name, 3, i * 20 + r.bottom, size=14)
            vt.value = arc.get_value()
            vt.modifiable = False
            EventHandler.register(vt.text_area.get_value_from_event, "SetValue")
            self.properties.add(vt, layer=2)

        vt = ValueText(self, 'Total Albedo', self.planet_area.rect.x, self.planet_area.rect.bottom + 10)
        vt.enable()
        vt.modifiable = False
        self.properties.add(vt, layer=2)

    def total_albedo(self):
        """Computes the total bond albedo (WIP)"""
        arcs = self.pie_land.arcs + self.pie_ocean.arcs + self.pie_clouds.arcs
        print(arcs)

    def total_coverage(self):
        pass

    def clear(self):
        for chart in self.charts.widgets():
            chart.disable()

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()
        for prop in self.properties.get_widgets_from_layer(3):
            prop.show()

    def hide(self):
        self.clear()
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def set_planet(self, planet):
        self.current = planet
        for chart in self.charts.widgets():
            chart.enable()


class UnbondedBody(ColoredBody):
    # because their "bond" albedo hasn't been set yet.
    def on_mousebuttondown(self, event):
        self.parent.select_one(self)
        self.parent.parent.set_planet(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = UnbondedBody

    def show(self):
        system = Systems.get_current()
        if system is not None:
            bodies = [body for body in system.astro_bodies if body.habitable is True]
            self.populate(bodies)

        super().show()

    def on_mousebuttondown(self, event):
        super().on_mousebuttondown(event)
        self.parent.clear()

from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup, color_areas as k
from engine.equations.planetary_system import Systems
from engine.frontend.widgets import BaseWidget
from .common import ListedArea, ColoredBody
from pygame import Surface, Rect
from ..pie import PieChart as Pc
from engine import albedos


class AlbedoPanel(BaseWidget):
    skippable = True  # initially, we only care for the albedo of habitable planets,
    # this may change in the future because the albedo (bond) also affects the object's visibility.
    skip = False

    def __init__(self, parent):
        self.name = 'Albedo'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5)

        self.properties = WidgetGroup()
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.properties.add(self.planet_area, layer=2)

        h = ((ALTO - 32 - 32) / 3)
        self.area_section_a = Rect(0, 32, ANCHO - self.planet_area.rect.w, h)
        self.area_section_b = Rect(0, self.area_section_a.bottom, ANCHO - self.planet_area.rect.w, h)
        self.area_section_c = Rect(0, self.area_section_b.bottom, ANCHO - self.planet_area.rect.w, h)

        charts = WidgetGroup()
        # Section a
        d = {'Land': 50, 'Ocean': 50}  # "clouds" is a single value
        ks = [[128, 64, 0], [0, 183, 235]]
        self.pie_coverage = Pc(self, *self.area_section_a.center, self.area_section_a.h//3, d, use_handlers=1, colors=ks)
        charts.add(self.pie_coverage)

        # Section B
        n = sorted(albedos.keys())
        x, y = 'names', 'colors'
        a = {x: {n[4]: 50, n[5]: 50}, y: [k[i] for i in [4, 5]]}
        b = {x: {n[0]: 16, n[1]: 17, n[2]: 16, n[3]: 17, n[6]: 17, n[9]: 17}, y: [k[i] for i in [0, 1, 2, 3, 6, 9]]}
        c = {x: {n[7]: 50, n[8]: 50}, y: [k[i] for i in [7, 8]]}

        u = [self.area_section_b.w/3, self.area_section_b.w/3*2, self.area_section_b.w/3*3]
        v = self.area_section_b.centery
        h = self.area_section_b.h//3
        self.pie_ocean = Pc(self, u[0], v, h, a[x], use_handlers=True, colors=a[y])
        self.pie_land = Pc(self, u[1], v, h, b[x], use_handlers=True, colors=b[y])
        self.pie_clouds = Pc(self, u[2], v, h, c[x], use_handlers=True, colors=c[y])
        charts.add(self.pie_ocean, self.pie_land, self.pie_clouds)

        # Section C
        e = {name: 10 for name in sorted(albedos.keys())}
        self.pie_total = Pc(self, *self.area_section_c.center, h, e, use_handlers=True, colors=k)
        charts.add(self.pie_total)

        for piechart in charts.widgets():
            for obj in piechart.chart.widgets():
                self.properties.add(obj, layer=3)

    def clear(self):
        self.image.fill(COLOR_BOX)

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

    def show_no_system_error(self):
        pass


class UnbondedBody(ColoredBody):
    # because their "bond" albedo hasn't been set yet.
    def on_mousebuttondown(self, event):
        self.parent.select_one(self)


class AvailablePlanets(ListedArea):
    listed_type = UnbondedBody

    def show(self):
        system = Systems.get_current()
        if system is not None:
            bodies = [body for body in system.astro_bodies if body.habitable is True]
            self.populate(bodies)
        else:
            self.parent.show_no_system_error()
        super().show()

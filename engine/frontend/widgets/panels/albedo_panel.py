from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, color_areas as k, Group
from engine.frontend.widgets import BaseWidget, ValueText
from engine.backend import EventHandler, albedos, q
from .common import ListedArea, ColoredBody
from engine.equations.space import Universe
from pygame import Surface, Rect, draw
from decimal import Decimal as Dc
from ..pie import PieChart as Pc


class AlbedoPanel(BaseWidget):
    skippable = False
    skip = False

    current = None
    locked = False

    show_swap_system_button = True

    def __init__(self, parent):
        self.name = 'Albedo'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        # f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(15, underline=True, bold=True)

        self.properties = Group()
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 300)
        self.properties.add(self.planet_area, layer=1)

        h = round((ALTO - 32 - 32) / 3)
        a1 = Rect(0, 32, ANCHO - self.planet_area.rect.w, h)
        b0 = Rect(0, a1.bottom, ANCHO - self.planet_area.rect.w, h)
        b1 = Rect(0, a1.bottom, b0.w / 2, h)
        b1.right = b0.right
        b2 = Rect(0, a1.bottom, b0.w / 2, h / 2)
        b3 = Rect(0, b2.bottom, b0.w / 2, h / 2)

        self.charts = Group()

        # Section A
        d = {'Land': 50, 'Ocean': 50}  # "clouds" is a single value
        ks = [[128, 64, 0], [0, 183, 235]]
        self.pie_coverage = Pc(self, b2.centerx + 150, a1.centery - 20, b3.h / 1.4, d,
                               use_handlers=1, colors=ks, is_set=0)
        self.charts.add(self.pie_coverage)

        # Section B
        n = sorted(albedos.keys())
        x, y = 'names', 'colors'

        o = Dc(16)
        p = Dc(17)
        g = Dc(50)

        a = {x: {n[4]: g, n[5]: g}, y: [k[i] for i in [4, 5]]}
        b = {x: {n[0]: o, n[1]: p, n[2]: o, n[3]: p, n[6]: p, n[9]: p}, y: [k[i] for i in [0, 1, 2, 3, 6, 9]]}
        c = {x: {n[7]: g, n[8]: g}, y: [k[i] for i in [7, 8]]}

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
        self.clouds_text = ValueText(self, 'Clouds', 3, 2 * 20 + r.bottom, size=14)
        self.clouds_text.enable()
        self.clouds_text.modifiable = True
        self.clouds_text.text_area.set_value(q(50), is_percentage=True)
        self.properties.add(self.clouds_text, layer=2)
        draw.aaline(self.image, 'black', [1, self.clouds_text.rect.top - 1], [100, self.clouds_text.rect.top - 1])

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

        self.albedo_vt = ValueText(self, 'Total Albedo', self.planet_area.rect.x, self.planet_area.rect.bottom + 10)
        self.albedo_vt.enable()
        self.albedo_vt.modifiable = False
        self.properties.add(self.albedo_vt, layer=2)

        EventHandler.register(self.conclude, 'Fin')
        EventHandler.register(self.export_data, 'ExportData')

        for chart in self.charts.widgets():
            chart.hide()

    def surface_coverage(self):
        arcs = self.pie_land.arcs + self.pie_ocean.arcs + self.pie_clouds.arcs + self.pie_coverage.arcs
        data = {'clouds': self.clouds_text.value}
        for arc in arcs:
            if arc.enabled:
                data[arc.name] = float(arc.get_value().strip(' %'))
        self.current.set_biomes(data)

    def total_albedo(self):
        """Computes the total bond albedo (WIP)"""
        arcs = self.pie_land.arcs + self.pie_ocean.arcs + self.pie_clouds.arcs
        total_albedo = Dc(0)
        for arc in arcs:
            if arc.enabled:
                coverage = 'Land' if arc in self.pie_land else 'Ocean' if arc in self.pie_ocean else 'Clouds'
                local_name = arc.name
                min_v = Dc(albedos[local_name]['min']) / Dc(100)
                max_v = Dc(albedos[local_name]['max']) / Dc(100)
                total_albedo += ((min_v + max_v) / Dc(2)) * self.total_coverage(coverage, local_name)

        value = (round(total_albedo, 2) * Dc(100))
        self.current.albedo = float(value)
        self.surface_coverage()
        self.albedo_vt.text_area.set_value(q(float(value)), is_percentage=True)

    def total_coverage(self, global_title: str, title: str):
        g_chart = None
        l_chart = None
        if global_title == 'Clouds':
            g_chart = Dc(self.clouds_text.value) / Dc(100)
            l_chart = Dc(self.pie_clouds.get_value(title).strip('%')) / Dc(100)
        elif global_title == 'Ocean':
            g_chart = Dc(self.pie_coverage.get_value(global_title).strip('%')) / Dc(100)
            l_chart = Dc(self.pie_ocean.get_value(title).strip('%')) / Dc(100)
        elif global_title == 'Land':
            g_chart = Dc(self.pie_coverage.get_value(global_title).strip('%')) / Dc(100)
            l_chart = Dc(self.pie_land.get_value(title).strip('%')) / Dc(100)

        return g_chart * l_chart

    def clear(self):
        for chart in self.charts.widgets():
            chart.disable()
        for vt in self.properties.get_widgets_from_layer(2):
            vt.text_area.clear()
            vt.text_area.unit = ''
        self.clouds_text.text_area.set_value(q(50), is_percentage=True)

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        self.clear()
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def set_planet(self, planet):
        self.current = planet
        self.clear()
        for chart in self.charts.widgets():
            chart.set_values()
            chart.disable()
        if not self.current.biomes:
            if planet.planet_subtype == 'Earth-like Planet':
                for chart in self.charts.widgets():
                    chart.enable()
            elif planet.planet_subtype == 'Water World':
                self.pie_clouds.enable()
                self.pie_ocean.enable()
                self.pie_coverage.enable()
                self.pie_coverage.set_values({'Ocean': 100, 'Land': 0}, use_names=True)
            elif planet.planet_type == 'gaseous':
                self.pie_clouds.enable()
                self.clouds_text.text_area.set_value(q(100), is_percentage=True)

        else:
            if planet.habitable:
                for chart in self.charts.widgets():
                    chart.enable()
            pb = self.current.biomes
            self.pie_coverage.set_values({'Ocean': pb['ocean'], 'Land': pb['land']}, use_names=True)
            self.clouds_text.text_area.set_value(pb['clouds'], is_percentage=True)
            self.pie_clouds.set_values({'Thin Clouds': pb['thin_clouds'],
                                        'Thick Clouds': pb['thick_clouds']},
                                       use_names=True)
            self.pie_ocean.set_values({"Sea Ice": pb['sea_ice'], 'Open Ocean': pb['open_ocean']}, use_names=True)
            self.pie_land.set_values({
                "Desert": pb['desert'],
                "Forest": pb['forest'],
                "Grassland": pb["grassland"],
                "Inland Water Bodies": pb['inland_water_bodies'],
                "Urban": pb["urban"],
                "Snow and Ice": pb["snow_and_ice"]
            }, use_names=True)

            self.total_albedo()

    @staticmethod
    def elevate_changes(key, new_value: float):
        if key.text == 'Clouds':
            if new_value < 0:
                return q(0)
            elif new_value > 100:
                return q(100)

    def conclude(self, event):
        if hasattr(event.origin, 'parent'):
            if event.origin.parent.parent is self:
                if self.current is not None:
                    self.total_albedo()

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class UnbondedBody(ColoredBody):
    # because their "bond" albedo hasn't been set yet.
    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            self.parent.select_one(self)
            self.parent.parent.set_planet(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = UnbondedBody

    def show(self):
        if Universe.current_galaxy is not None:
            for system in Universe.nei().get_p_systems():
                idx = system.id
                bodies = [body for body in system.planets]
                self.populate(bodies, layer=idx)

        super().show()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            super().on_mousebuttondown(event)
            self.parent.clear()

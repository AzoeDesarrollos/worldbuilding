from engine.frontend.globales import COLOR_IRON_DIS, COLOR_SILICATES_DIS, COLOR_WATER_ICE_DIS
from engine.frontend.globales import COLOR_IRON, COLOR_SILICATES, COLOR_WATER_ICE
from engine.frontend.globales.group import WidgetGroup
from engine.frontend.globales import WidgetHandler
from ..basewidget import BaseWidget
from . import Arc  # Handle
from pygame import Rect


class PieChart(BaseWidget):
    chart = None
    colors_a = [COLOR_IRON, COLOR_SILICATES, COLOR_WATER_ICE]
    colors_b = [COLOR_IRON_DIS, COLOR_SILICATES_DIS, COLOR_WATER_ICE_DIS]

    def __init__(self, parent, cx, cy, radius, values):
        super().__init__(parent)
        self.chart = WidgetGroup()
        self.radius = radius
        self.rect = Rect(0, 0, radius, radius)
        self.rect.center = cx, cy
        WidgetHandler.add_widget(self)

        a, b = 0, 0
        arcs, handles = [], []
        for i, name in enumerate(values):
            value = values[name]['value']
            # handle_color = values[name]['handle']

            b += round((value / 100) * 360)

            arc = Arc(self, name, self.colors_a[i], self.colors_b[i], a, b, radius)
            arc.default_value = value
            # handle = Handle(self, b, arc.handle_pos, handle_color)

            self.chart.add(arc, layer=1)
            # self.chart.add(handle, layer=2)
            arcs.append(arc)
            # handles.append(handle)
            a = b
        #
        # arcs[0].links(handles[2], handles[0])
        # arcs[1].links(handles[0], handles[1])
        # arcs[2].links(handles[1], handles[2])

        arcs[0].displace(cx, cy)
        arcs[1].displace(cx, cy)
        arcs[2].displace(cx, cy)

    def set_values(self, values: dict = None):
        names = 'iron', 'water ice', 'silicates'
        a, b = 0, 0
        for i, name in enumerate(sorted(names)):
            arc = self.get_arc(name)
            value = values[name] if values is not None else arc.default_value
            b += round((value / 100) * 360)

            if not self.parent.parent.enabled:
                arc.disable()
            else:
                arc.enable()

            if value == 0:
                arc.hide()
            elif not arc.is_visible and self.parent.parent.is_visible:
                arc.show()

            if arc is not None:
                arc.set_ab(a, b)
            else:
                arc = Arc(self, name, self.colors_a[i], self.colors_b[i], a, b, self.radius)
                self.chart.add(arc, layer=1)
                arc.displace(*self.rect.center)
            a = b

    def on_mousebuttonup(self, event):
        if self.is_visible:
            for handle in self.chart.get_widgets_from_layer(2):
                if handle.pressed:
                    handle.on_mousebuttonup(event)

    def show(self):
        self.is_visible = True
        WidgetHandler.add_widget(self)

    def hide(self):
        self.is_visible = False
        WidgetHandler.del_widget(self)

    def draw(self, fondo):
        self.chart.update()
        self.chart.draw(fondo)

    def get_arc(self, name):
        arcs = [spr for spr in self.chart.get_widgets_from_layer(1) if spr.name == name]
        if len(arcs):
            arc = arcs[0]
        else:
            arc = None
        return arc

    def get_value(self, name):
        arc = self.get_arc(name)
        return arc.get_value()

    def update(self):
        if not self.parent.parent.enabled:
            for arc in self.chart.get_widgets_from_layer(1):
                if arc.enabled:
                    arc.disable()
        elif not self.enabled:
            for arc in self.chart.get_widgets_from_layer(1):
                if not arc.enabled:
                    arc.enable()

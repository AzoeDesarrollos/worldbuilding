from engine.frontend.globales.group import WidgetGroup
from engine.frontend.globales import WidgetHandler
from ..basewidget import BaseWidget
from . import Arc, Handle
from pygame import Rect


class PieChart(BaseWidget):
    chart = None

    def __init__(self, parent, cx, cy, radius, values):
        super().__init__(parent)
        self.chart = WidgetGroup()
        self.radius = radius
        self.rect = Rect(0, 0, radius, radius)
        self.rect.center = cx, cy
        WidgetHandler.add_widget(self)

        a, b = 0, 0
        arcs, handles = [], []
        for name in values:
            color = values[name]['color']
            value = values[name]['value']
            handle_color = values[name]['handle']

            b += round((value / 100) * 360)

            arc = Arc(self, name, color, a, b, radius)
            handle = Handle(self, b, arc.handle_pos, handle_color)

            self.chart.add(arc, layer=1)
            self.chart.add(handle, layer=2)
            arcs.append(arc)
            handles.append(handle)
            a = b

        arcs[0].links(handles[2], handles[0])
        arcs[1].links(handles[0], handles[1])
        arcs[2].links(handles[1], handles[2])

        arcs[0].displace(cx, cy)
        arcs[1].displace(cx, cy)
        arcs[2].displace(cx, cy)

    def on_mousebuttonup(self, event):
        print('aca')
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

    def get_value(self, name):
        arc = [spr for spr in self.chart.get_widgets_from_layer(1) if spr.name == name][0]
        return arc.get_value()

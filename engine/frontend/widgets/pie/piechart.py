from engine.frontend.globales import COLOR_IRON, COLOR_SILICATES, COLOR_WATER_ICE
from engine.frontend.globales.group import WidgetGroup
from engine.frontend.globales import WidgetHandler
from ..basewidget import BaseWidget
from pygame import Rect, Color
from . import Arc, Handle


class PieChart(BaseWidget):
    chart = None
    colors_a = None
    colors_b = None

    def __init__(self, parent, cx, cy, radius, values, use_handlers=False, colors=None, is_set=True):
        super().__init__(parent)
        self.chart = WidgetGroup()
        self.radius = radius
        self.rect = Rect(0, 0, radius, radius)
        self.rect.center = cx, cy
        WidgetHandler.add_widget(self)
        if colors is None:
            self.use_default_colors()
        else:
            self.set_colors(colors)

        a, b = 0, 0
        arcs, handles = [], []
        handle_color = None
        for i, name in enumerate(values):
            value = values[name]
            if use_handlers:
                handle_color = 'black'

            b += round((value / 100) * 360)

            arc = Arc(self, name, self.colors_a[i], self.colors_b[i], a, b, radius, using_handlers=use_handlers,
                      is_set=is_set)
            arc.default_value = value
            arcs.append(arc)
            self.chart.add(arc, layer=1)

            if use_handlers:
                handle = Handle(self, b, name, arc.handle_pos, handle_color)
                self.chart.add(handle, layer=2)
                handles.append(handle)

            a = b
        if use_handlers:
            for i in range(len(arcs)):
                j = (i + (len(arcs) - 1)) % len(arcs)

                arcs[i].links(handles[j], handles[i])

        for arc in arcs:
            arc.displace(cx, cy)

    def set_colors(self, colors: list):
        self.colors_a = colors.copy()
        self.colors_b = [self.get_disabled_color(k) for k in colors]

    def use_default_colors(self):
        self.colors_a = [COLOR_IRON, COLOR_SILICATES, COLOR_WATER_ICE]
        self.colors_b = [self.get_disabled_color(COLOR_IRON),
                         self.get_disabled_color(COLOR_SILICATES),
                         self.get_disabled_color(COLOR_WATER_ICE)]

    @staticmethod
    def set_active(widget=None):
        WidgetHandler.set_active(widget)

    @staticmethod
    def get_disabled_color(rgb):
        disabled = Color(rgb)
        hsla = list(disabled.hsla)
        hsla[1] = 20
        hsla[2] = 70
        disabled.hsla = hsla
        return disabled

    def set_values(self, values: dict = None):
        names = 'iron', 'water ice', 'silicates'
        a, b = 0, 0
        for i, name in enumerate(sorted(names)):
            arc = self.get_arc(name)
            value = values[name] if values is not None else arc.default_value
            b += round((value / 100) * 360)

            if not self.parent.parent.enabled and arc.enabled:
                arc.disable()
            elif not arc.enabled:
                arc.enable()

            if value == 0:
                arc.hide()
            elif not arc.is_visible and self.parent.parent.is_visible:
                arc.show()

            if arc is not None:
                if arc.is_visible:
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
        "Overrides the base function because this class has no image to add to the Renderer"""
        self.is_visible = True
        WidgetHandler.add_widget(self)

    def hide(self):
        "Overrides the base function because this class has no image to remove from the Renderer"""
        self.is_visible = False
        WidgetHandler.del_widget(self)

    def enable(self):
        super().enable()
        for widget in self.chart.widgets():
            widget.enable()

    def disable(self):
        super().disable()
        for widget in self.chart.widgets():
            widget.disable()

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

    def get_default_value(self, name):
        arc = self.get_arc(name)
        return str(arc.default_value) + ' %'

    @property
    def arcs(self):
        return self.chart.get_widgets_from_layer(1)

    @property
    def handles(self):
        return self.chart.get_widgets_from_layer(2)

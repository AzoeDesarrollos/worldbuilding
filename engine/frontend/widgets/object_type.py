from ..globales.group import WidgetGroup
from engine.backend import EventHandler
from .basewidget import BaseWidget
from .values import ValueText
from engine import q


class ObjectType(BaseWidget):
    current = None
    has_values = False

    locked = False

    modifiable = True

    def __init__(self, parent, relative_names, absolute_names, relative_args, absolute_args):
        super().__init__(parent)
        EventHandler.register(self.clear_selection, 'Clear')
        EventHandler.register(self.clear, 'ClearData')

        self.relative_args = relative_args
        self.absolute_args = absolute_args

        self.properties = WidgetGroup()
        self.relatives = WidgetGroup()
        for i, button in enumerate(relative_names):
            if len(relative_names) == 6:
                vt = ValueText(self, button, 50, 55 + i * 13 * 2)
            else:
                vt = ValueText(self, button, 50, 55 + i * 15 * 2)
            self.relatives.add(vt)
            self.properties.add(vt, layer=1)

        self.absolutes = WidgetGroup()
        for i, button in enumerate(absolute_names):
            vt = None
            if len(absolute_names) in [5, 6]:
                vt = ValueText(self, button, 50, 210 + i * 15 * 2)
            elif len(absolute_names) == 7:
                vt = ValueText(self, button, 50, 180 + i * 15 * 2)
            self.absolutes.add(vt)
            self.properties.add(vt, layer=1)

    def set_modifiables(self, group: str, *indexes):
        if group == 'relatives':
            group = self.relatives
        elif group == 'absolutes':
            group = self.absolutes

        for index in indexes:
            obj = group.get_widget(index)
            obj.modifiable = True

    def show(self):
        for p in self.properties.get_widgets_from_layer(1):
            p.show()
        for p in self.properties.get_widgets_from_layer(2):
            p.show()

    def hide(self):
        for p in self.properties.widgets():
            p.hide()

    def clear_selection(self, event):
        if event.origin is not self:
            self.active = False

    def clear(self, event):
        return NotImplemented

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.active = True

    def on_mousebuttonup(self, event):
        if event.button == 1:
            EventHandler.trigger('Clear', self)

    def elevate_changes(self, key, new_value):
        arg = ''
        if key in self.relatives:
            idx = self.relatives.widgets().index(key)
            arg = self.relative_args[idx]
        elif key in self.absolutes:
            idx = self.absolutes.widgets().index(key)
            arg = self.absolute_args[idx]
        self.current.set_value(arg, new_value)

    def fill(self, tos):
        for i, elemento in enumerate(self.relatives.widgets()):
            arg = self.relative_args[i]
            if self.parent.relative_mode:
                got_attr = getattr(self.current, arg)
            else:
                got_attr = getattr(self.current, arg).to(tos[arg])
            attr = q(str(round(float(got_attr.m), 5)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento. value = attr
            elemento.text_area.show()

        for i, elemento in enumerate(self.absolutes.widgets()):
            arg = self.absolute_args[i]
            got_attr = getattr(self.current, arg)
            attr = q(str(round(got_attr.m, 3)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            elemento.text_area.show()
        self.has_values = True

    def erase(self):
        self.has_values = False
        for elemento in self.relatives.widgets() + self.absolutes.widgets():
            elemento.text_area.clear()

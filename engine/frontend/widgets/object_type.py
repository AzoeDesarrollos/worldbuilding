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

    def __init__(self, parent, relative_values, absolute_values):
        super().__init__(parent)
        EventHandler.register(self.clear_selection, 'Clear')

        self.properties = WidgetGroup()
        self.relatives = WidgetGroup()
        for i, button in enumerate(relative_values):
            if len(relative_values) == 5:
                vt = ValueText(self, button, 50, 55 + i * 15 * 2)
            elif len(relative_values) == 6:
                vt = ValueText(self, button, 50, 55 + i * 13 * 2)
            else:
                vt = ValueText(self, button, 50, 55 + i * 15 * 2)
            self.relatives.add(vt)
            self.properties.add(vt, layer=1)

        self.absolutes = WidgetGroup()
        for i, button in enumerate(absolute_values):
            vt = None
            if len(absolute_values) == 5:
                vt = ValueText(self, button, 50, 210 + i * 15 * 2)
            elif len(absolute_values) == 7:
                vt = ValueText(self, button, 50, 180 + i * 15 * 2)
            self.absolutes.add(vt)
            self.properties.add(vt, layer=1)

    def show(self):
        for p in self.properties.widgets():
            p.show()

    def hide(self):
        for p in self.properties.widgets():
            p.hide()

    def clear_selection(self, event):
        if event.origin is not self:
            self.active = False

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.active = True

    def on_mousebuttonup(self, event):
        if event.button == 1:
            EventHandler.trigger('Clear', self)

    def elevate_changes(self, key, new_value):
        setattr(self.current, key.lower(), new_value)

    def fill(self, tos):
        for elemento in self.relatives.widgets():
            if self.parent.relative_mode:
                got_attr = getattr(self.current, elemento.text.lower())
            else:
                got_attr = getattr(self.current, elemento.text.lower()).to(tos[elemento.text.capitalize()])
            attr = q(str(round(got_attr.m, 5)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento. value = attr
            elemento.text_area.show()

        for elemento in self.absolutes.widgets():
            got_attr = getattr(self.current, elemento.text.lower())
            attr = q(str(round(got_attr.m, 3)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            elemento.text_area.show()
        self.has_values = True

    def erase(self):
        self.has_values = False
        for elemento in self.relatives.widgets() + self.absolutes.widgets():
            elemento.text_area.clear()

from .basewidget import BaseWidget
from pygame.sprite import LayeredUpdates
from engine.backend import EventHandler
from .values import ValueText


class ObjectType(BaseWidget):
    current = None
    has_values = False

    def __init__(self, parent, relative_values, absolute_values):
        super().__init__(parent)
        EventHandler.register(self.clear_selection, 'Clear')

        self.properties = LayeredUpdates()
        self.relatives = LayeredUpdates()
        for i, button in enumerate(relative_values):
            if len(relative_values) == 5:
                vt = ValueText(self, button, 50, 55 + i * 15 * 2)
            elif len(relative_values) == 6:
                vt = ValueText(self, button, 50, 55 + i * 13 * 2)
            else:
                vt = ValueText(self, button, 50, 55 + i * 15 * 2)
            self.relatives.add(vt)
            self.properties.add(vt, layer=1)

        self.absolutes = LayeredUpdates()
        for i, button in enumerate(absolute_values):
            vt = None
            if len(absolute_values) == 5:
                vt = ValueText(self, button, 50, 210 + i * 15 * 2)
            elif len(absolute_values) == 7:
                vt = ValueText(self, button, 50, 180 + i * 15 * 2)
            self.absolutes.add(vt)
            self.properties.add(vt, layer=1)

    def show(self):
        for p in self.properties:
            p.show()

    def hide(self):
        for p in self.properties:
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

    def fill(self, tos):
        for elemento in self.relatives:
            if self.parent.relative_mode:
                attr = getattr(self.current, elemento.text.lower())
            else:
                attr = getattr(self.current, elemento.text.lower()).to(tos[elemento.text.capitalize()])
            elemento.text_area.value = '{:,g}'.format((round(attr, 3))) if type(attr) is not str else attr
            elemento.text_area.update()
            elemento.text_area.show()

        for elemento in self.absolutes:
            attr = getattr(self.current, elemento.text.lower())
            elemento.text_area.value = '{:,g}'.format((round(attr, 3))) if type(attr) is not str else attr
            elemento.text_area.update()
            elemento.text_area.show()

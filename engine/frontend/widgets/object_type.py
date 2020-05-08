from .basewidget import BaseWidget
from engine.frontend.globales import Renderer, WidgetHandler
from pygame.sprite import LayeredUpdates
from engine.backend import EventHandler
from pygame import font
from .values import ValueText


class ObjectType(BaseWidget):
    current = None

    def __init__(self, parent, text, x, y, relative_values, absolute_values):
        super().__init__(parent)
        bg = 125, 125, 125
        fg = 0, 0, 0

        f1 = font.SysFont('Verdana', 16)
        f2 = font.SysFont('Verdana', 16)
        f2.set_underline(True)

        self.text = text
        self.image = f1.render(text, 1, fg, bg)
        self.rect = self.image.get_rect(topleft=(x, y))
        EventHandler.register(self.clear_selection, 'Clear')

        self.properties = LayeredUpdates()
        self.relatives = LayeredUpdates()
        for i, button in enumerate(relative_values):
            vt = ValueText(self, button, self.rect.x + 50, self.rect.bottom + 1 + i * 15 * 2)
            self.relatives.add(vt)
            self.properties.add(vt)

        self.absolutes = LayeredUpdates()
        for i, button in enumerate(absolute_values):
            vt = ValueText(self, button, self.rect.x + 50, self.rect.bottom + 160 + i * 15 * 2)
            self.absolutes.add(vt)
            self.properties.add(vt)

    def show(self):
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)
        for p in self.properties:
            p.show()

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
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

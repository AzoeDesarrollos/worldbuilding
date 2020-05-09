from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX
from engine.backend.eventhandler import EventHandler
from engine.frontend import Renderer, WidgetHandler
from engine.frontend.graph.graph import graph_loop
from engine.equations import Star
from .basewidget import BaseWidget
from pygame import font, Surface


class ValueText(BaseWidget):
    selected = False
    active = False

    def __init__(self, parent, text, x, y):
        super().__init__(parent)

        bg = 125, 125, 125
        fg = 0, 0, 0
        self.text = text

        f1 = font.SysFont('Verdana', 16)
        f2 = font.SysFont('Verdana', 16)
        f2.set_underline(True)

        self.img_uns = f1.render(text + ':', 1, fg, bg)
        self.img_sel = f2.render(text + ':', 1, fg, bg)

        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        EventHandler.register(self.clear_selection, 'Clear')

        self.text_area = NumberArea(self.parent, text, self.rect.right + 3, self.rect.y)

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def show(self):
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)
        self.text_area.show()

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
        self.text_area.hide()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.parent.parent.name != 'Star' and self.parent.parent.unit.name == 'Earth':
                self.active = True
                lim = self.parent.parent.parent.system.terra_mass
                data = graph_loop(mass_upper_limit=lim.m)
                for elemento in self.parent.properties.get_sprites_from_layer(1):
                    if elemento.text.lower() in data:
                        elemento.text_area.value = str(data[elemento.text.lower()])
                        elemento.text_area.update()
                        elemento.text_area.show()
                self.parent.check_values()
                Renderer.reset()
            else:
                self.active = True
                self.text_area.enable()

    def on_mousebuttonup(self, event):
        if event.button == 1:
            EventHandler.trigger('Clear', self)

    def on_mouseover(self):
        self.select()

    def clear_selection(self, event):
        if event.origin is not self:
            self.active = False
            self.text_area.disable()

    def update(self):
        if self.selected:
            self.image = self.img_sel
        else:
            self.image = self.img_uns

        if not self.active:
            self.deselect()


class NumberArea(BaseWidget):
    value = None
    enabled = False

    def __init__(self, parent, name, x, y):
        super().__init__(parent)
        self.value = ''
        self.name = name
        self.f = font.SysFont('Verdana', 16)
        EventHandler.register(self.input, 'Key', 'BackSpace', 'Fin')
        self.image = Surface((0, self.f.get_height()))
        self.rect = self.image.get_rect(topleft=(x, y))

    def input(self, event):
        if self.enabled:
            if event.data is not None:
                char = event.data['value']
                if char.isdigit() or char == '.':
                    self.value += char
            elif event.tipo == 'BackSpace':
                self.value = self.value[0:len(self.value) - 1]
            elif event.tipo == 'Fin':
                if self.parent.parent.name == 'Planet':
                    self.parent.check_values()  # for planets
                elif self.parent.parent.name == 'Star':
                    self.parent.set_star(Star({self.name.lower(): float(self.value)}))  # for stars

    def clear(self):
        self.value = ''
        self.update()

    def enable(self):
        self.enabled = True
        self.show()
        WidgetHandler.add_widget(self)

    def disable(self):
        self.enabled = False
        WidgetHandler.del_widget(self)

    def show(self):
        Renderer.add_widget(self, layer=50)

    def hide(self):
        Renderer.del_widget(self)

    def update(self):
        self.image = self.f.render(self.value, 1, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

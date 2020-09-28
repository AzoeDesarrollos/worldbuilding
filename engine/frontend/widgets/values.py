from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX
from engine.equations.planetary_system import system
from engine.backend.eventhandler import EventHandler
from engine.frontend import Renderer, WidgetHandler
from engine.frontend.graph.graph import graph_loop
from engine.equations import Star
from .basewidget import BaseWidget
from pygame import font, Surface
from math import pow
from engine import q


class ValueText(BaseWidget):
    selected = False
    active = False

    def __init__(self, parent, text, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX):
        super().__init__(parent)
        self.text = text

        f1 = font.SysFont('Verdana', 16)
        f2 = font.SysFont('Verdana', 16)
        f2.set_underline(True)

        self.img_uns = f1.render(text + ':', True, fg, bg)
        self.img_sel = f2.render(text + ':', True, fg, bg)

        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        EventHandler.register(self.clear_selection, 'Clear')

        self.text_area = NumberArea(self.parent, text, self.rect.right + 3, self.rect.y, fg, bg)

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def disable(self):
        super().disable()
        self.text_area.disable()

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
            p = self.parent
            if p.parent.name == 'Planet' and p.parent.unit.name == 'Earth' and not p.has_values:
                self.active = True
                lim = system.terra_mass
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

    def __repr__(self):
        return self.text


class NumberArea(BaseWidget):
    value = None
    inner_value = None
    enabled = False
    ticks = 0
    clicks = 0
    increment = 0
    potencia = 0

    def __init__(self, parent, name, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX):
        super().__init__(parent)
        self.value = ''
        self.name = name
        self.fg, self.bg = fg, bg
        self.f = font.SysFont('Verdana', 16)
        # EventHandler.register(self.input, 'Key', 'BackSpace', 'Fin')
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
                self.update_inner_value(self.value)
            elif event.tipo == 'Fin' and len(self.value):
                if self.parent.parent.name == 'Planet':
                    self.parent.check_values()  # for planets
                elif self.parent.parent.name == 'Star':
                    value = self.value.split(' ')[0]
                    self.parent.set_star(Star({self.name.lower(): float(value)}))  # for stars
                elif self.parent.parent.name == 'Satellite':
                    self.parent.calculate()  # for moons
                elif self.parent.parent.name == 'Orbit':
                    self.parent.fill()

    def on_mousebuttondown(self, event):
        self.ticks = 0
        if self.clicks == 10:
            self.potencia += 1
            self.clicks = 2
        else:
            self.clicks += 1
        self.increment = round((0.001 * (pow(10, self.potencia))), 4)

        if self.inner_value is not None and not type(self.inner_value) is str:
            if event.button == 5:  # rueda abajo
                self.inner_value += q(self.increment, self.inner_value.u)
                self.increment = 0
            elif event.button == 4 and self.inner_value > 0:  # rueda arriba
                self.inner_value -= q(self.increment, self.inner_value.u)
                self.increment = 0

            elif event.button != 1:
                self.value = str(round(self.inner_value, 4))

    def update_inner_value(self, new):
        if self.inner_value is not None:
            self.inner_value = q(new, self.inner_value.u)

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
        EventHandler.deregister(self.input, 'key')

    def show(self):
        Renderer.add_widget(self, layer=50)
        EventHandler.register(self.input, 'Key', 'BackSpace', 'Fin')

    def hide(self):
        Renderer.del_widget(self)
        EventHandler.deregister(self.input, 'key')

    def update(self):
        self.ticks += 1
        if self.ticks >= 60:
            self.clicks = 0
            self.increment = 0
            self.potencia = 0

        self.image = self.f.render(str(self.value), True, self.fg, self.bg)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

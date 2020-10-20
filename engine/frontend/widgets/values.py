from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX
from engine.equations.planet import GasDwarf, Terrestial
from engine.frontend.dwarfgraph import dwarfgraph_loop
from engine.equations.planetary_system import system
from engine.backend.eventhandler import EventHandler
from engine.frontend import Renderer, WidgetHandler
from engine.frontend.graph.graph import graph_loop
from engine.frontend.gasgraph import gasgraph_loop
from .incremental_value import IncrementalValue
from engine.backend.util import add_decimal
from .basewidget import BaseWidget
from pygame import font, Surface
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

        self.text_area = NumberArea(self, text, self.rect.right + 3, self.rect.y, fg, bg)

    def elevate_changes(self, new_value, unit):
        value = q(new_value, unit)
        self.parent.elevate_changes(self.text, value)

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
        not_enough_mass = 'There is not enough mass in the system to create new bodies of this type.'
        if event.button == 1:
            p = self.parent
            data = None
            if p.parent.name == 'Planet' and not p.has_values:
                self.active = True
                available_mass = system.get_available_mass()
                if p.parent.unit.name == 'Habitable':
                    available_mass = available_mass.to('earth_mass').m
                    m_low, m_high, r_low, r_high = Terrestial
                    if available_mass < m_high:
                        m_high = available_mass
                    assert m_high <= 3.5, not_enough_mass
                    data = graph_loop(mass_lower_limit=m_low, mass_upper_limit=m_high,
                                      radius_lower_limit=r_low, radius_upper_limit=r_high)
                elif p.parent.unit.name == 'Terrestial':
                    available_mass = available_mass.to('earth_mass').m
                    m_high = 10
                    if available_mass < m_high:
                        m_high = available_mass
                    assert m_high > 0.1, not_enough_mass
                    data = graph_loop(mass_upper_limit=m_high)

                elif p.parent.unit.name == 'Gas Dwarf':
                    m_low, m_high, r_low, r_high = GasDwarf
                    if available_mass.m < m_high:
                        m_high = available_mass.m
                        assert m_high > 0.2, not_enough_mass
                        data = graph_loop(mass_lower_limit=m_low, mass_upper_limit=m_high,
                                          radius_lower_limit=r_low, radius_upper_limit=r_high)
                elif p.parent.unit.name == 'Gas Giant':
                    assert available_mass.m >= 0.03, not_enough_mass
                    data = gasgraph_loop()
                else:
                    assert available_mass.to('earth_mass').m > 0.1, not_enough_mass
                    data = dwarfgraph_loop()
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


class NumberArea(BaseWidget, IncrementalValue):
    value = None
    unit = None

    def __init__(self, parent, name, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX):
        super().__init__(parent)
        self.value = ''
        self.name = name
        self.fg, self.bg = fg, bg
        self.f = font.SysFont('Verdana', 16)
        self.image = Surface((0, self.f.get_height()))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.great_grandparent = self.parent.parent.parent
        self.grandparent = self.parent.parent

    def input(self, event):
        if self.enabled and not self.grandparent.locked:
            if event.data is not None:
                char = event.data['value']
                if char.isdigit() or char == '.':
                    self.value = str(self.value)
                    self.value += char

            elif event.tipo == 'BackSpace':
                self.value = self.value[0:len(str(self.value)) - 1]

            elif event.tipo == 'Fin' and len(str(self.value)):
                if self.great_grandparent.name == 'Planet':
                    self.grandparent.check_values()

                elif self.great_grandparent.name == 'Star':
                    self.grandparent.set_star({self.parent.text.lower(): float(self.value)})  # for stars

                elif self.great_grandparent.name == 'Satellite':
                    self.grandparent.calculate()

                elif self.great_grandparent.name == 'Orbit':
                    self.grandparent.fill()

    def set_value(self, quantity):
        if type(quantity) is q:
            self.value = float(quantity.m)
            self.unit = str(quantity.u)

        else:  # suponemos, un str
            self.value = quantity
            self.unit = None

    def on_mousebuttondown(self, event):
        self.increment = self.update_increment()
        if not type(self.value) is str and self.grandparent.modifiable:
            if event.button == 5:  # rueda abajo
                self.value += self.increment
                self.increment = 0
            elif event.button == 4 and self.value > 0:  # rueda arriba
                self.value -= self.increment
                self.increment = 0

            if event.button in (4, 5):
                self.value = round(self.value, 4)
                self.parent.elevate_changes(self.value, self.unit)

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
        Renderer.add_widget(self)
        EventHandler.register(self.input, 'Key', 'BackSpace', 'Fin')

    def hide(self):
        Renderer.del_widget(self)
        EventHandler.deregister(self.input, 'key')

    def update(self):
        self.reset_power()
        if hasattr(self.value, '__round__') and self.unit is not None:
            value = q(add_decimal(str(round(self.value, 3))), self.unit)
            if self.unit != 'year':
                value = '{:~}'.format(value)
            value = str(value)
        else:
            value = str(self.value)
        self.image = self.f.render(value, True, self.fg, self.bg)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

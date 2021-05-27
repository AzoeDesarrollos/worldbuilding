from engine.frontend.graphs import dwarfgraph_loop, gasgraph_loop, graph_loop
from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX
from engine.equations.planet import GasDwarf, Terrestial
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend import Renderer, WidgetHandler
from .incremental_value import IncrementalValue
from engine.backend.util import add_decimal
from .basewidget import BaseWidget
from pygame import Surface
from engine import q


class ValueText(BaseWidget):
    selected = False
    active = False
    do_round = True
    editable = False

    def __init__(self, parent, text, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX, kind='digits'):
        super().__init__(parent)
        self.text = text

        f1 = self.crear_fuente(16)
        f2 = self.crear_fuente(16, underline=True)

        self.img_uns = f1.render(text + ':', True, fg, bg)
        self.img_sel = f2.render(text + ':', True, fg, bg)

        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        EventHandler.register(self.clear_selection, 'Clear')

        if kind == 'digits':
            self.text_area = NumberArea(self, text, self.rect.right + 3, self.rect.y, fg, bg)

        elif kind == 'letters':
            self.text_area = TextArea(self, text, self.rect.right + 3, self.rect.y, fg, bg)

    @property
    def modifiable(self):
        return self.text_area.modifiable

    @modifiable.setter
    def modifiable(self, new_value: bool):
        self.text_area.modifiable = new_value

    @property
    def value(self):
        return self.text_area.value

    @value.setter
    def value(self, quantity):
        self.text_area.set_value(quantity)

    def elevate_changes(self, new_value, unit):
        value = q(new_value, unit)
        returned = self.parent.elevate_changes(self, value)
        if returned is not None:
            self.text_area.set_value(returned)

    def set_min_and_max(self, min_v, max_v):
        self.text_area.min = min_v
        self.text_area.max = max_v

    def disable(self):
        super().disable()
        self.text_area.disable()

    def show(self):
        super().show()
        self.text_area.show()

    def hide(self):
        super().hide()
        self.text_area.hide()

    def on_mousebuttondown(self, event):
        not_enough_mass = 'There is not enough mass in the system to create new bodies of this type.'
        if event.button == 1:
            p = self.parent
            if p.parent.name == 'Planet' and not p.has_values:
                system = Systems.get_current()
                self.active = True
                available_mass = system.get_available_mass()
                if p.parent.unit.name == 'Habitable':
                    available_mass = available_mass.to('earth_mass').m
                    m_low, m_high, r_low, r_high = Terrestial
                    if available_mass < m_high:
                        m_high = available_mass
                    assert m_high >= 3.5, not_enough_mass
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
                    if available_mass.to('earth_mass').m < m_high:
                        m_high = available_mass.m
                    assert m_high > 0.2, not_enough_mass
                    data = graph_loop(mass_lower_limit=m_low, mass_upper_limit=m_high,
                                      radius_lower_limit=r_low, radius_upper_limit=r_high)
                elif p.parent.unit.name == 'Gas Giant':
                    assert available_mass.m >= 0.03, not_enough_mass
                    data = gasgraph_loop(round(available_mass.m, 2))
                else:
                    available_mass = round(available_mass.to('earth_mass').m, 4)
                    assert available_mass > 0.0001, not_enough_mass
                    data = dwarfgraph_loop(available_mass if available_mass < 0.1 else None)
                if data is not None:
                    for elemento in self.parent.properties.get_sprites_from_layer(1):
                        attr = ''
                        if elemento in self.parent.relatives:
                            idx = self.parent.relatives.widgets().index(elemento)
                            attr = self.parent.relative_args[idx]
                        elif elemento in self.parent.absolutes:
                            idx = self.parent.absolutes.widgets().index(elemento)
                            attr = self.parent.absolute_args[idx]

                        if attr in data:
                            elemento.value = str(data[attr])
                            elemento.text_area.show()
                    self.parent.check_values(data.get('composition', None))
                    Renderer.reset()
                else:
                    self.parent.button.disable()
            elif p.parent.name == 'Orbit' and p.has_values:
                text = self.text_area
                if text.unit == 'year' and text.value < 0.01:
                    attr = q(text.value, text.unit).to('day')
                    if attr.m < 0.1:
                        attr = attr.to('hour')
                    text.set_value(attr)
                    text.update()

                elif self.editable:
                    self.active = True
                    self.text_area.enable()
            elif p.parent.name == 'Naming' and not p.has_values:
                p.parent.set_current(self)
                self.active = True
                self.text_area.enable()
            else:
                self.active = True
                self.text_area.enable()
            return self.text

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
        self.text_area.update()

    def __repr__(self):
        return self.text


class BaseArea(BaseWidget):
    modifiable = False
    unit = None

    def __init__(self, parent, name, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX):
        super().__init__(parent)
        self.value = ''
        self.name = name
        self.fg, self.bg = fg, bg
        self.f = self.crear_fuente(16)
        self.image = Surface((0, self.f.get_height()))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.great_grandparent = self.parent.parent.parent
        self.grandparent = self.parent.parent

    def set_value(self, quantity):
        return NotImplemented


class NumberArea(BaseArea, IncrementalValue):
    value = None
    min = 0
    max = None

    def input(self, event):
        if self.enabled and not self.grandparent.locked:
            assert self.modifiable, 'This value is a derivated value. It is not directly modifiable.'
            if event.data is not None:
                char = event.data['value']
                if char.isdigit() or char == '.':
                    self.value = str(self.value)
                    self.value += char

            elif event.tipo == 'BackSpace':
                if type(self.value) is str:
                    self.value = self.value[0:len(str(self.value)) - 1]

            elif event.tipo == 'Fin' and len(str(self.value)):
                if self.great_grandparent.name == 'Planet':
                    self.grandparent.check_values()

                elif self.great_grandparent.name == 'Star':
                    self.grandparent.set_star({self.parent.text.lower(): float(self.value)})  # for stars

                elif self.great_grandparent.name == 'Star System':
                    self.grandparent.fill()

                elif self.great_grandparent.name == 'Satellite':
                    self.grandparent.calculate()

                elif self.great_grandparent.name == 'Orbit':
                    self.grandparent.fill()

                elif self.great_grandparent.name == 'Asteroid':
                    self.grandparent.calculate()

                elif self.great_grandparent.name == 'Planetary Orbit':
                    self.great_grandparent.show_markers_button.enable()
                    self.grandparent.fill()

    def set_value(self, quantity):
        if type(quantity) is q:
            self.value = float(quantity.m)
            self.unit = str(quantity.u)

        elif type(quantity) is str:
            self.value = quantity
            self.unit = None

        elif hasattr(quantity, 'name'):
            self.value = quantity
            self.unit = None

    def on_mousebuttondown(self, event):
        self.increment = self.update_increment()
        v = self.value
        b = event.button
        assert self.modifiable, 'This value is a derivated value. It is not directly modifiable.'
        if not type(v) is str:
            i = 0
            if b == 5 and (self.max is None or v + self.increment <= self.max):  # rueda abajo
                self.value += self.increment
            elif b == 4 and v - self.increment >= self.min:  # rueda arriba
                self.value += -self.increment

            if event.button in (4, 5):
                self.increment = 0
                self.value = round(self.value + i, 4)
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
        EventHandler.deregister(self.input, 'Key')

    def show(self):
        super().show()
        EventHandler.register(self.input, 'Key', 'BackSpace', 'Fin')

    def hide(self):
        super().hide()
        EventHandler.deregister(self.input, 'Key', 'BackSpace', 'Fin')

    def update(self):
        self.reset_power()
        if hasattr(self.value, '__round__') and self.unit is not None:
            if self.parent.do_round:
                value = q(add_decimal(str(round(self.value, 3))), self.unit)
            else:
                value = q(add_decimal(str(self.value)), self.unit)
            if self.unit != 'year':
                value = '{:~}'.format(value)
            value = str(value)
        else:
            value = str(self.value)
        self.image = self.f.render(value, True, self.fg, self.bg)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)


class TextArea(BaseArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        EventHandler.register(self.input, 'Typed', 'BackSpace', 'Fin', 'Key')

    def input(self, tecla):
        if self.enabled and tecla.origin == self.name:
            if tecla.tipo == 'Typed' or tecla.tipo == 'Key':
                self.value += tecla.data['value']

            elif tecla.tipo == 'BackSpace':
                self.value = self.value[0:-1]

            elif tecla.tipo == 'Fin':
                self.great_grandparent.name_objects()
                self.great_grandparent.cycle(+1)

        elif tecla.origin != self.name:
            self.deselect()

        return self.grandparent

    def update(self):
        self.image = self.f.render(self.value, True, self.fg, self.bg)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def __repr__(self):
        return self.name + ' Text'

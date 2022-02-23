from engine.frontend.graphs import dwarfgraph_loop, gasgraph_loop, graph_loop
from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, COLOR_DISABLED
from engine.frontend.graphs.axial_tilt import axial_loop
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
    do_round = True
    editable = False

    def __init__(self, parent, text, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX, kind='digits', size=16):
        super().__init__(parent)
        self.text = text

        f1 = self.crear_fuente(size)
        f2 = self.crear_fuente(size, underline=True)

        self.img_uns = f1.render(text + ':', True, fg, bg)
        self.img_sel = f2.render(text + ':', True, fg, bg)
        self.img_dis = f1.render(text + ':', True, COLOR_DISABLED, bg)

        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        EventHandler.register(self.clear_selection, 'ClearData')

        if kind == 'digits':
            self.text_area = NumberArea(self, text, self.rect.right + 3, self.rect.y, fg, bg, size=size)

        elif kind == 'letters':
            self.text_area = TextArea(self, text, self.rect.right + 3, self.rect.y, fg, bg, size=size)

    def kill(self) -> None:
        super().kill()
        self.text_area.kill()

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
        self.enable()
        self.text_area.set_value(quantity)

    def elevate_changes(self, new_value, unit):
        if unit != '%':
            value = q(new_value, unit)
        else:
            value = new_value
        if hasattr(self.parent, 'elevate_changes'):
            returned = self.parent.elevate_changes(self, value)
            if returned is not None:
                self.text_area.set_value(returned, is_percentage=True if unit == '%' else False)

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
            if p.parent.name == 'Planet' and p.parent.enabled:
                data = None
                system = Systems.get_current()
                self.active = True
                available_mass = system.get_available_mass()
                if p.parent.unit.name == 'Habitable' and not p.has_values:
                    available_mass = available_mass.to('earth_mass').m
                    m_low, m_high, r_low, r_high = Terrestial
                    if available_mass < m_high:
                        m_high = available_mass
                    assert available_mass > 0.1, not_enough_mass
                    data = graph_loop(mass_lower_limit=m_low, mass_upper_limit=m_high,
                                      radius_lower_limit=r_low, radius_upper_limit=r_high)
                elif p.parent.unit.name == 'Terrestial' and not p.has_values:
                    available_mass = available_mass.to('earth_mass').m
                    m_high = 10
                    if available_mass < m_high:
                        m_high = available_mass
                    assert m_high > 0.1, not_enough_mass
                    data = graph_loop(mass_upper_limit=m_high)
                elif p.parent.unit.name == 'Gas Dwarf' and not p.has_values:
                    m_low, m_high, r_low, r_high = GasDwarf
                    if available_mass.to('earth_mass').m < m_high:
                        m_high = available_mass.m
                    assert m_high > 0.2, not_enough_mass
                    data = graph_loop(mass_lower_limit=m_low, mass_upper_limit=m_high,
                                      radius_lower_limit=r_low, radius_upper_limit=r_high,
                                      is_gas_drwaf=True)
                elif p.parent.unit.name == 'Gas Giant' and not p.has_values:
                    assert available_mass.m >= 0.03, not_enough_mass
                    data = gasgraph_loop(round(available_mass.m, 2))
                elif p.parent.unit.name == 'Dwarf Planet' and not p.has_values:
                    available_mass = round(available_mass.to('earth_mass').m, 4)
                    assert available_mass > 0.0001, not_enough_mass
                    data = dwarfgraph_loop(available_mass if available_mass < 0.1 else None)
                if not p.has_values:
                    Renderer.reset()
                if data is not None:
                    for elemento in self.parent.properties.get_widgets_from_layer(1):
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

                elif self.text == 'Axial tilt':
                    planet = self.parent.current
                    data = axial_loop(planet)
                    self.parent.update_value(self, data)

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
            elif self.modifiable:
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

    def clear(self):
        self.deselect()
        self.text_area.clear()

    def update(self):
        if self.selected and self.enabled:
            self.image = self.img_sel
        elif not self.enabled:
            self.image = self.img_dis
        else:
            self.image = self.img_uns

        self.deselect()
        self.text_area.update()

    def __repr__(self):
        return self.text

    def compare(self, other):
        if isinstance(other, ValueText):
            return self.text == other.text
        return False


class BaseArea(BaseWidget):
    modifiable = False
    unit = None

    def __init__(self, parent, name, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX, size=16):
        super().__init__(parent)
        self.value = ''
        self.name = name
        self.fg, self.bg = fg, bg
        self.f = self.crear_fuente(size)
        self.image = Surface((0, self.f.get_height()))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.great_grandparent = self.parent.parent.parent
        self.grandparent = self.parent.parent

    def set_value(self, quantity, is_percentage=False):
        return NotImplemented

    def clear(self):
        raise NotImplementedError


class NumberArea(BaseArea, IncrementalValue):
    value = None
    min = 0
    max = None

    def __init__(self, parent, name, x, y, fg=COLOR_TEXTO, bg=COLOR_BOX, size=16):
        super().__init__(parent, name, x, y, fg, bg, size=size)
        EventHandler.register(self.get_value, 'SetValue')

    def input(self, event):
        if self.enabled and not self.grandparent.locked and event.origin == self.name:
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
                if self.great_grandparent.name == 'Star':
                    self.grandparent.set_star({self.parent.text.lower(): float(self.value)})

                elif self.great_grandparent.name in ['Star System', 'Orbit', 'Multiple Stars']:
                    self.grandparent.fill()

                elif self.great_grandparent.name in ['Satellite', 'Asteroid']:
                    self.grandparent.calculate()

                elif self.great_grandparent.name == 'Planetary Orbit':
                    self.great_grandparent.show_markers_button.enable()
                    self.grandparent.fill()

                elif self.grandparent.name == 'Albedo':
                    self.grandparent.total_albedo()

    def set_value(self, quantity, is_percentage=False):
        if type(quantity) is q and not is_percentage:
            self.value = float(quantity.m)
            self.unit = str(quantity.u)

        elif type(quantity) is str:
            self.value = quantity
            self.unit = None

        elif hasattr(quantity, 'name'):
            self.value = quantity
            self.unit = None

        elif is_percentage:
            if isinstance(quantity, q):
                self.value = float(quantity.m)
            elif type(quantity) is float:
                self.value = quantity
            self.unit = '%'

    def get_value(self, event):
        if event.origin.capitalize() == self.parent.text:
            self.set_value(event.data['value'])

    def get_value_from_event(self, event):
        if event.origin == self.parent.text:
            value = float(event.data['value'].strip('%'))
            self.set_value(value, is_percentage=True)

    def on_mousebuttondown(self, event):
        self.increment = self.update_increment()
        b = event.button
        assert self.modifiable, 'This is a derivated value. It is not directly modifiable.'
        if not type(self.value) is str:
            if b == 5 and (self.max is None or float(self.value) + self.increment <= self.max):  # rueda abajo
                self.value += self.increment
            elif b == 4 and float(self.value) - self.increment >= self.min:  # rueda arriba
                self.value += -self.increment

            if event.button in (4, 5):
                self.increment = 0
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
        EventHandler.deregister(self.input, 'Key')

    def show(self):
        super().show()
        EventHandler.register(self.input, 'Key', 'BackSpace', 'Fin')

    def hide(self):
        super().hide()
        EventHandler.deregister(self.input, 'Key', 'BackSpace', 'Fin')

    def update(self):
        self.reset_power()
        if hasattr(self.value, '__round__') and self.unit is not None and self.unit != '%':
            if self.parent.do_round:
                value = q(add_decimal(str(round(self.value, 3))), self.unit)
            else:
                value = q(add_decimal(str(self.value)), self.unit)
            if self.unit != 'year':
                value = '{:~}'.format(value)
            if self.unit != "%":
                value = str(value)
        elif self.unit != "%":
            value = str(self.value)
        else:
            value = str(self.value)+self.unit
        self.image = self.f.render(value, True, self.fg, self.bg)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)


class TextArea(BaseArea):
    value = None

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
                self.great_grandparent.check()

        elif tecla.origin != self.name:
            self.deselect()

        return self.grandparent

    def update(self):
        self.image = self.f.render(self.value, True, self.fg, self.bg)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def clear(self):
        self.value = None

    def __repr__(self):
        return self.name + ' Text'

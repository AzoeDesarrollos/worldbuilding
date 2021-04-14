from engine.frontend import WidgetHandler, ANCHO, ALTO, COLOR_BOX, COLOR_TEXTO, WidgetGroup, COLOR_DISABLED
from engine.frontend.graphs.atmograph.atmograph import graph, atmo, interpolacion_lineal, convert
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.backend.textrect import render_textrect
from pygame import Surface, draw, SRCALPHA, Rect
from .common import ListedArea, AvailablePlanet
from engine import molecular_weight, q
from math import sqrt


class AtmospherePanel(BaseWidget):
    current = None
    curr_idx = 0
    pre_loaded = False
    pressure = None
    curr_planet = None

    skippable = False
    written_info = None
    total = 0

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Atmosphere'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.elements = WidgetGroup()
        self.pressure = q(0, 'psi')

        f1 = self.crear_fuente(16, underline=True)
        self.f2 = self.crear_fuente(12)
        self.f3 = self.crear_fuente(16)
        f4 = self.crear_fuente(11)
        self.f5 = self.crear_fuente(11, bold=True)

        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)
        self.write('Composition', self.f3, centerx=65, y=35)
        self.water_state_rect = self.write('State of Water at Surface: ', f4, x=3, y=ALTO-50)
        EventHandler.register(self.load_atmosphere, 'LoadData')
        EventHandler.register(self.clear, 'ClearData')
        self.area_info = Rect(190, 460, 195, 132 - 41)
        self.warning_rect = Rect(self.area_info.x, self.area_info.bottom, self.area_info.w, 21)

        for i, element in enumerate(molecular_weight):
            gas = molecular_weight[element]
            name = gas['name']

            c = None
            if name == 'Molecular Nitrogen':
                c = (255, 255, 0)
            weight = gas['weight']
            min_atm = q(gas.get('min_atm', 0), 'atm')
            max_atm = q(gas.get('max_atm', 0), 'atm')
            boiling = None if gas['boiling'] is None else q(gas.get('boiling'), 'degree_Celsius')
            melting = None if gas['melting'] is None else q(gas.get('melting'), 'degree_Celsius')
            elm = Element(self, i, element, name, weight, min_atm, max_atm, boiling, melting, 3, 21 * i + 60, color=c)
            elm.hide()
            self.elements.add(elm)
            self.write('%', self.f3, x=elm.percent.rect.right + 3, centery=elm.rect.centery)

        self.atmograph = Atmograph(self, 190, 60)
        self.show_pressure = ShownPressure(self, x=self.atmograph.rect.x, centery=self.atmograph.rect.bottom + 10)
        self.show_pressure.update_text('Not stablished')
        self.properties = WidgetGroup()
        self.planets = AvailablePlanets(self, ANCHO - 200, 460, 200, 132)
        self.properties.add(self.planets)

    def clear(self, event):
        if event.data['panel'] is self:
            for element in self.elements.widgets():
                element.percent.value = ''
        self.image.fill(COLOR_BOX, [3, ALTO - 87, 190, 21])

    def warn(self, element):
        min_atm, max_atm = element.min_atm, element.max_atm
        value = element.percent.get_value()
        warn = False
        if self.show_pressure.value is not None and value:
            partial_pressure = float(value) * self.show_pressure.value.m / 100
            warn = warn or partial_pressure <= min_atm.m != 0
            warn = warn or partial_pressure >= max_atm.m != 0
        return warn

    def show_info(self, element=None):
        if element is None:
            element = self.written_info
        else:
            self.written_info = element
        name = element.name
        max_p = element.max_atm.m
        min_p = element.min_atm.m
        value = element.percent.get_value()
        assertion = not str(value) in ('liquid', 'solid')
        assert assertion, f"{name} can't form atmospheric gas, because it is {value} at planet's temperature."
        p_pre = str(round(float(value) * self.show_pressure.value.m / 100, 3))
        t = f'{name}\nPressure at sea level: {p_pre} atm\nMinimum pressure: {min_p} atm\nMaximum pressure: {max_p} atm'

        self.image.fill(COLOR_BOX, self.area_info)
        render = render_textrect(t, self.f2, self.area_info, COLOR_TEXTO, COLOR_BOX)
        self.image.blit(render, self.area_info)
        self.show_warning(element)

    def show_warning(self, element):
        if self.warn(element):
            symbol = element.symbol
            fuente = self.crear_fuente(12, bold=True)
            fg = (255, 0, 0)
            render = render_textrect(f'Toxic concentration of {symbol}', fuente, self.warning_rect, fg, COLOR_BOX)
            self.image.blit(render, self.warning_rect)
        else:
            self.image.fill(COLOR_BOX, self.warning_rect)

    def set_planet_atmosphere(self, pressure):
        planet = self.curr_planet
        elements = [i for i in self.elements.widgets() if bool(i.value()) is not False]
        data = dict(zip([e.symbol for e in elements], [float(e.percent.get_value()) for e in elements]))
        data.update({'pressure_at_sea_level': {'value': pressure.m, 'unit': str(pressure.u)}})
        planet.set_atmosphere(data)
        self.planets.delete_objects(planet)
        self.planets.show()

    def load_atmosphere(self, event):
        if 'Planets' in event.data and len(event.data['Planets']):
            atmosphere = event.data['Planets'][0]['atmosphere']
            elements = [e.symbol for e in self.elements.widgets()]
            for elem in atmosphere:
                if elem != 'pressure_at_sea_level':
                    idx = elements.index(elem)
                    element = self.elements.widgets()[idx]
                    element.percent.value = str(atmosphere[elem])
                else:
                    value = atmosphere[elem]['value']
                    unit = atmosphere[elem]['unit']
                    self.pressure = q(value, unit)
            self.pre_loaded = True

    def show(self):
        super().show()
        for element in self.elements.widgets():
            element.show()
        self.atmograph.show()
        self.planets.show()
        self.show_name()
        self.show_pressure.show()

    def show_name(self):
        text = 'Atmosphere of planet'
        planet = self.curr_planet
        if planet is not None:
            idx = Systems.get_current().planets.index(planet)
            text += ' #' + str(idx) + ' (' + planet.clase + ')'

        self.image.fill(COLOR_BOX, (0, 21, self.rect.w, 16))
        self.write(text, self.f2, centerx=self.rect.centerx, y=21)

    def hide(self):
        super().hide()
        for element in self.elements.widgets():
            element.hide()
        self.atmograph.hide()
        self.planets.hide()
        self.show_pressure.hide()

    def set_current(self, elm):
        self.current = elm
        self.curr_idx = self.current.idx

    def set_planet(self, planet):
        for elm in self.elements.widgets():
            elm.percent.clear()

        self.curr_planet = planet
        self.show_name()

        state = 'liquid'
        if planet.temperature.m <= 0:
            state = 'solid'
        elif planet.temperature.m >= 100:
            state = 'gaseous'

        self.image.fill(COLOR_BOX, [159, 580, 52, 14])
        dx, dy = self.water_state_rect.topright
        self.write(state, self.f5, x=dx+1, y=dy)

    def cycle(self, delta):
        for elm in self.elements.widgets():
            elm.deselect()
            elm.disable()
        if 0 <= self.curr_idx + delta < len(self.elements.widgets()):
            self.curr_idx += delta
            self.current = self.elements.widgets()[self.curr_idx]

        self.current.select()
        self.current.enable()
        WidgetHandler.origin = self.current.percent.name

    def update(self):
        self.total = 0
        for element in self.elements.widgets():
            if type(element.percent.get_value()) is not str:
                self.total += element.percent.get_value()

        self.image.fill(COLOR_BOX, (0, ALTO - 87, 160, 32))
        self.write('Total: ' + str(self.total) + '%', self.f3, x=3, y=ALTO - 87)
        a = self.atmograph
        self.image.fill(COLOR_BOX, [a.rect.x, a.rect.bottom, 200, 21])


class Element(BaseWidget):
    color_ovewritten = False

    def __init__(self, parent, idx, symbol, name, weight, min_atm, max_atm, boiling, melting, x, y, color=None):
        super().__init__(parent)
        self.symbol = symbol
        self.name = name
        self.weight = weight
        self.min_atm = min_atm
        self.max_atm = max_atm
        self.idx = idx
        self.boiling = boiling
        self.melting = melting

        if color is None:
            color = COLOR_TEXTO
        else:
            self.color_ovewritten = True
            self.color = color
        self.image = self.write_name(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.percent = PercentageCell(self, 45, y)

    def value(self):
        return self.percent.compile()

    def write_name(self, color):
        base = Surface((45, 21))
        base.fill(COLOR_BOX)
        f1 = self.crear_fuente(14, bold=True)
        f2 = self.crear_fuente(12, )
        w = 12
        for i, char in enumerate(self.symbol):
            if char.isdigit():
                f = f2
                y = 5
            else:
                f = f1
                y = 0
            partial = f.render(char, 1, color, COLOR_BOX)
            rect = partial.get_rect(x=w * i, y=y)
            base.blit(partial, rect)
            w = 12 if not char.isdigit() else 10
        return base

    def on_mouseover(self):
        self.parent.show_info(self)

    def show(self):
        super().show()
        self.percent.enable()
        self.percent.show()

    def hide(self):
        super().hide()
        self.percent.hide()

    def calculate_pressure(self):
        color = (0, 0, 0) if not self.color_ovewritten else self.color
        planet = self.parent.curr_planet
        if planet is not None:
            t = planet.temperature.to('earth_temperature').m
            m = planet.mass.to('earth_mass').m
            r = planet.radius.to('earth_radius').m
            if (sqrt((3 * 8.3144598 * (t * 1500)) / self.weight)) / ((sqrt(m / r) * 11200) / 6) > 1:
                color = 255, 0, 0

        return color

    def calculate_temperature(self):
        planet = self.parent.curr_planet
        if planet is not None:
            t = planet.temperature.to('degree_Celsius')
            state = 'gas'
            if self.boiling is not None and t <= self.boiling:
                state = 'liquid'
            if self.melting is not None and t <= self.melting:
                state = 'solid'
            return state
        else:
            return ''

    def deselect(self):
        self.selected = False
        self.percent.deselect()

    def select(self):
        self.selected = True
        self.percent.select()

    def disable(self):
        self.enabled = False
        self.percent.enabled = False

    def enable(self):
        self.enabled = True
        self.percent.enabled = True

    def __repr__(self):
        return self.symbol

    def update(self):
        if self.parent.curr_planet is not None:
            color = self.calculate_pressure()
        else:
            color = 0, 0, 0
        self.image = self.write_name(color)


class PercentageCell(BaseWidget):
    enabled = False
    value = ''
    name = ''

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((12 * 8, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        r = self.rect.inflate(-1, -1)
        self.image.fill(COLOR_BOX, (1, 1, r.w - 1, r.h - 1))
        self.f = self.crear_fuente(14)
        self.name = 'Cell of ' + self.parent.symbol

        self.grandparent = self.parent.parent

    def on_keydown(self, tecla):
        if self.enabled and self.selected and tecla.origin == self.name:
            gp = self.grandparent
            if tecla.data is not None and tecla.tipo == 'Key':

                if tecla.data['value'] == '.' and not len(self.value):
                    self.value = "0."
                elif tecla.data['value'] == '.':
                    self.value += '.'
                else:
                    self.value += tecla.data['value']

            elif tecla.tipo == 'Fin' and tecla.origin == self.name:
                gp.cycle(+1)

            elif tecla.tipo == 'BackSpace':
                self.value = self.value[0:-1]

            elif tecla.tipo == 'Arrow' and tecla.origin == self.name:
                gp.cycle(tecla.data['delta'])

        elif tecla.origin != self.name:
            self.deselect()

        return self.grandparent

    def on_mousebuttondown(self, event):
        if event.button == 1:
            for element in self.grandparent.elements:
                element.percent.deselect()
            self.enabled = True
            self.select()
            self.grandparent.set_current(self.parent)
            return self.__repr__()

    def show(self):
        super().show()
        EventHandler.register(self.on_keydown, 'Arrow')

    def hide(self):
        super().hide()
        EventHandler.deregister(self.on_keydown, 'Arrow')

    def deselect(self):
        if self.enabled:
            self.selected = False
            self.image.fill((0, 0, 0))
            w, h = self.rect.size
            self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
            EventHandler.deregister(self.on_keydown)

    def select(self):
        if self.enabled:
            self.selected = True
            self.image.fill((255, 255, 255))
            w, h = self.rect.size
            self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
            EventHandler.register(self.on_keydown, 'Key', 'BackSpace', 'Fin')

    def get_value(self):
        if self.value == '':
            return 0
        elif self.value.isnumeric():
            return float(self.value)
        else:
            return self.value

    def compile(self):
        value = self.get_value()
        if type(value) is not float:
            return False
        else:
            return value

    def clear(self):
        self.value = ''

    def update(self):
        color = COLOR_DISABLED
        if self.parent.calculate_pressure() not in [(255, 255, 0), (0, 0, 0)]:
            self.enabled = False
        elif self.parent.calculate_temperature() != 'gas':
            self.enabled = False
            self.value = self.parent.calculate_temperature()
        else:
            color = COLOR_BOX
            self.enabled = True
        w, h = self.rect.size
        self.image.fill(color, [1, 1, w - 2, h - 2])
        render = self.f.render(self.value, True, COLOR_TEXTO, color)
        self.image.blit(render, (1, 1))

    def __repr__(self):
        return self.name


class Atmograph(BaseWidget):
    min_p, max_p = 0, 0
    vol_n2 = 0
    pressure = None

    enabled = False
    reached = False
    blocked = False

    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.image = Surface(graph.get_size())
        self.image.blit(graph, (0, 0))
        self.canvas = Surface(graph.get_size(), SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = 'atmograph'
        EventHandler.register(self.on_keydown, 'Fin', 'Arrow')

    def unbreatheable(self):
        planet = self.parent.curr_planet
        if planet is not None and not planet.habitable:
            t = f"The selected planet of type '{planet.clase}' can't have a breathable atmosphere."
            self.enabled = False
            base = Surface(self.image.get_size(), SRCALPHA)
            base.fill((0, 0, 0, 150))

            image = Surface((200, 200))
            rect = image.get_rect(centerx=self.rect.w // 2, centery=self.rect.centery)
            f = self.crear_fuente(16)
            render = render_textrect(t, f, rect, COLOR_TEXTO, COLOR_BOX, 1)
            base.blit(render, rect)

            return True, base
        return False, None

    def on_mousebuttondown(self, event):
        delta_y = 0
        n2 = self.parent.elements.widgets()[9]
        n2_value = n2.percent.get_value()
        if any([self.parent.curr_planet is None, n2_value == 0, not n2.percent.value.isnumeric()]):
            return
        vol_n2 = interpolacion_lineal(n2_value)
        if vol_n2 != self.vol_n2:
            self.reached = False
        self.vol_n2 = interpolacion_lineal(n2_value)
        if event.button == 1 and not self.reached:
            warning_text = 'Pressure at sea level depends on Nitrogen concentration.' \
                           ' Please, fill a value before proceeding.'
            assert n2_value, warning_text

            max_pressure, min_pressure = atmo(n2_value, self.rect)
            self.max_p, self.min_p = max_pressure, min_pressure
            selected_pressure = (max_pressure + min_pressure) // 2
            self.pressure = selected_pressure
            draw.line(self.canvas, (0, 0, 0, 255), (0, max_pressure), (self.rect.right, max_pressure))
            draw.line(self.canvas, (0, 0, 0, 255), (0, min_pressure), (self.rect.right, min_pressure))
            self.enabled = True

            pressure = convert(selected_pressure)
            self.parent.show_pressure.update_text(pressure)

        elif event.button == 4:
            if self.max_p < (self.pressure - 1) < self.min_p:
                delta_y = -1

        elif event.button == 5:
            if self.max_p < (self.pressure + 1) < self.min_p:
                delta_y = +1

        if event.button in (4, 5) and delta_y:
            self.reached = True
            self.pressure += delta_y

        return self.name

    def on_keydown(self, event):
        if event.origin == self.name:
            if event.tipo == 'Arrow':
                word = event.data['word']

                delta_y = 0

                if word == 'arriba':
                    if self.max_p < (self.pressure - 1) < self.min_p:
                        delta_y = -1
                elif word == 'abajo':
                    if self.max_p < (self.pressure + 1) < self.min_p:
                        delta_y = +1

                if delta_y:
                    self.pressure += delta_y

            elif event.tipo == 'Fin':
                self.enabled = False
                self.reached = True
                self.parent.show_pressure.elevate_pressure()

    def update(self):
        if self.enabled:
            selected_pressure = self.pressure if self.pressure is not None else 0

            self.canvas.fill((0, 0, 0, 0))
            draw.line(self.canvas, (255, 0, 0, 255), (self.vol_n2, 0), (self.vol_n2, self.rect.height))
            draw.line(self.canvas, (0, 0, 0, 255), (0, self.max_p), (self.rect.right, self.max_p))
            draw.line(self.canvas, (0, 0, 0, 255), (0, self.min_p), (self.rect.right, self.min_p))
            draw.line(self.canvas, (0, 255, 0, 255), (0, self.pressure), (self.rect.right, selected_pressure))
            self.image.blit(graph, (0, 0))
            self.image.blit(self.canvas, (0, 0))

            pressure = convert(self.pressure)
            self.parent.show_pressure.update_text(pressure)
        else:
            b, img = self.unbreatheable()
            if b and not self.blocked:
                self.parent.show_pressure.unlock()
                self.image.blit(graph, (0, 0))
                self.image.blit(img, (0, 0))
                self.blocked = True


class AvailablePlanets(ListedArea):
    def populate(self, planets):
        for i, planet in enumerate(planets):
            listed = ListedPlanet(self, planet, self.rect.x + 3, i * 16 + self.rect.y + 21)
            self.listed_objects.add(listed)

    def show(self):
        super().show()
        system = Systems.get_current()
        if system is not None:
            self.populate([planet for planet in system.planets if not len(planet.atmosphere)])
            for listed in self.listed_objects.widgets():
                listed.show()


class ListedPlanet(AvailablePlanet):
    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.select()
            self.parent.parent.set_planet(self.object_data)


class ShownPressure(BaseWidget):
    value = q(0, 'atm')
    locked = True
    _value = ''
    finished = False
    finished_text = ''

    def __init__(self, parent, x, centery):
        super().__init__(parent)
        self.f = self.crear_fuente(16)
        self.base = 'Pressure at Sea Level: '
        self.image = self.f.render(self.base, 1, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(x=x, centery=centery)
        EventHandler.register(self.on_keydown, 'Key', 'BackSpace', 'Fin')

    def unlock(self):
        self.locked = False
        self.finished_text = ''

    def on_mousebuttondown(self, event):
        if event.button == 1 and not self.locked:
            self.update_text('')

        return self

    def on_keydown(self, key):
        if not self.locked and key.origin == self:
            if key.tipo == 'Key':
                char = key.data['value']
                if char.isdigit() or char == '.':
                    self._value += char

            elif key.tipo == 'BackSpace':
                if type(self._value) is str:
                    self._value = self._value[0:len(str(self._value)) - 1]

            elif key.tipo == 'Fin':
                self.finished = True
                self.update_text(q(float(self._value), 'atm'))
                self.elevate_pressure()

    def update(self):
        if self._value != '' and not self.finished:
            value = self._value
            self.update_text(value)

    def elevate_pressure(self):
        self.parent.set_planet_atmosphere(round(self.value, 3))
        self.finished_text = ' (set)'
        self.update_text(self.value)

    def update_text(self, text):
        if type(text) is q:
            self.value = text.to('atm')
            p = '{:~}'.format(round(text.to('atm'), 3))
        else:
            p = text
        self.image = self.f.render('Pressure at Sea Level: ' + p + self.finished_text, 1, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=self.rect.copy().topleft)

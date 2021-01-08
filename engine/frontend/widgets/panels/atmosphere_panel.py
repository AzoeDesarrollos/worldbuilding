from engine.frontend import Renderer, WidgetHandler, ANCHO, ALTO, COLOR_BOX, COLOR_TEXTO, WidgetGroup, COLOR_DISABLED
from engine.frontend.graphs.atmograph.atmograph import graph, atmo, interpolacion_lineal, convert
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from .common import ListedArea, PlanetButton
from pygame import Surface, draw, SRCALPHA
from engine import molecular_weight, q
from math import sqrt


class AtmospherePanel(BaseWidget):
    current = None
    curr_idx = 0
    pre_loaded = False
    pressure = None
    curr_planet = None

    skippable = False

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

        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)
        self.write('Composition', self.f3, centerx=65, y=35)
        EventHandler.register(self.load_atmosphere, 'LoadData')
        EventHandler.register(self.clear, 'ClearData')

        for i, element in enumerate(molecular_weight):
            name = molecular_weight[element]['name']
            color = None
            if name == 'Molecular Nitrogen':
                color = (255, 255, 0)
            weight = molecular_weight[element]['weight']
            min_atm = q(molecular_weight[element].get('min_atm', 0), 'atm')
            max_atm = q(molecular_weight[element].get('max_atm', 0), 'atm')
            elm = Element(self, i, element, name, weight, min_atm, max_atm, 3, 21 * i + 60, color=color)
            elm.hide()
            self.elements.add(elm)
            self.write('%', self.f3, x=110, centery=elm.rect.centery)

        self.atmograph = Atmograph(self, 190, 60)
        self.show_pressure = ShownPressure(self, x=self.atmograph.rect.x, centery=self.atmograph.rect.bottom + 10)
        self.show_pressure.update_text(self.pressure)
        self.properties = WidgetGroup()
        self.planets = AvailablePlanets(self, ANCHO - 200, 460, 200, 132)
        self.properties.add(self.planets)

    def clear(self, event):
        if event.data['panel'] is self:
            for element in self.elements.widgets():
                element.percent.value = ''
        self.image.fill(COLOR_BOX, [3, ALTO - 87, 190, 21])

    def set_atmosphere(self, pressure):
        planet = self.curr_planet
        elements = [i for i in self.elements.widgets() if i.percent.value != '']
        data = dict(zip([e.symbol for e in elements], [float(e.percent.value) for e in elements]))
        data.update({'pressure_at_sea_level': {'value': pressure.m, 'unit': str(pressure.u)}})
        planet.set_atmosphere(data)

    def load_atmosphere(self, event):
        if 'Planets' in event.data:
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
        self.curr_planet = planet
        self.show_name()

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
        total = 0
        for element in self.elements.widgets():
            total += element.percent.get_value()

        self.write('Total: ' + str(total) + '%', self.f3, x=3, y=ALTO - 87)
        a = self.atmograph
        self.image.fill(COLOR_BOX, [a.rect.x, a.rect.bottom, 200, 21])


class Element(BaseWidget):
    color_ovewritten = False

    def __init__(self, parent, idx, symbol, name, weight, min_atm, max_atm, x, y, color=None):
        super().__init__(parent)
        self.symbol = symbol
        self.name = name
        self.weight = weight
        self.min_atm = min_atm
        self.max_atm = max_atm
        self.idx = idx

        f = self.crear_fuente(14, bold=True)
        if color is None:
            color = COLOR_TEXTO
        else:
            self.color_ovewritten = True
            self.color = color
        self.image = f.render(symbol, True, color, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.percent = PercentageCell(self, 45, y)

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
        f = self.crear_fuente(14, bold=True)
        self.image = f.render(self.symbol, True, color, COLOR_BOX)


class PercentageCell(BaseWidget):
    enabled = False
    disabled = True
    value = ''
    name = ''

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((12 * 5, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        r = self.rect.inflate(-1, -1)
        self.image.fill(COLOR_BOX, (1, 1, r.w - 1, r.h - 1))
        self.f = self.crear_fuente(14)
        self.name = 'Cell of ' + self.parent.symbol

        self.grandparent = self.parent.parent

    def on_keydown(self, tecla):
        if self.enabled and not self.disabled and self.selected:
            if tecla.data is not None and tecla.tipo == 'Key':
                self.value += tecla.data['value']

            elif tecla.tipo == 'Fin' and tecla.origin == self.name:
                self.grandparent.cycle(+1)

            elif tecla.tipo == 'BackSpace':
                self.value = self.value[0:-1]

            elif tecla.tipo == 'Arrow' and tecla.origin == self.name:
                self.grandparent.cycle(tecla.data['delta'])

    def on_mousebuttondown(self, event):
        if event.button == 1:
            for element in self.grandparent.elements:
                element.percent.deselect()
            self.enabled = True
            self.select()
            self.grandparent.set_current(self.parent)
            return self.__repr__()

    def show(self):
        EventHandler.register(self.on_keydown, 'Arrow')
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def hide(self):
        EventHandler.deregister(self.on_keydown, 'Arrow')
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)

    def deselect(self):
        self.selected = False
        self.image.fill((0, 0, 0))
        w, h = self.rect.size
        self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
        EventHandler.deregister(self.on_keydown)

    def select(self):
        if not self.disabled:
            self.selected = True
            self.image.fill((255, 255, 255))
            w, h = self.rect.size
            self.image.fill(COLOR_BOX, [1, 1, w - 2, h - 2])
            EventHandler.register(self.on_keydown, 'Key', 'BackSpace', 'Fin')

    def get_value(self):
        if self.value == '':
            return 0
        else:
            return float(self.value)

    def update(self):
        if self.parent.calculate_pressure() not in [(255, 255, 0), (0, 0, 0)]:
            color = COLOR_DISABLED
            self.disabled = True
        else:
            color = COLOR_BOX
            self.disabled = False
        w, h = self.rect.size
        self.image.fill(color, [1, 1, w - 2, h - 2])
        render = self.f.render(self.value, True, COLOR_TEXTO, COLOR_BOX)
        self.image.blit(render, (1, 1))

    def __repr__(self):
        return self.name


class Atmograph(BaseWidget):
    pressure = q(0, 'atm')
    min_p, max_p = 0, 0
    vol_n2 = 0
    pointer = None

    enabled = False

    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.image = Surface(graph.get_size())
        self.image.blit(graph, (0, 0))
        self.canvas = Surface(graph.get_size(), SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = 'atmograph'
        EventHandler.register(self.on_keydown, 'Fin', 'Arrow')

    def on_mousebuttondown(self, event):
        nitrogen = self.parent.elements.widgets()[9]
        warning_text = 'Pressure at sea level depends on Nitrogen concentration.' \
                       ' Please, fill a value before proceeding.'
        assert nitrogen.percent.get_value(), warning_text

        max_pressure, min_pressure = atmo(nitrogen.percent.get_value(), self.rect)
        self.max_p, self.min_p = max_pressure, min_pressure
        selected_pressure = (max_pressure + min_pressure) // 2
        self.pointer = selected_pressure
        draw.line(self.canvas, (0, 0, 0, 255), (0, max_pressure), (self.rect.right, max_pressure))
        draw.line(self.canvas, (0, 0, 0, 255), (0, min_pressure), (self.rect.right, min_pressure))

        self.vol_n2 = interpolacion_lineal(nitrogen.percent.get_value())

        self.enabled = True

        pressure = convert(selected_pressure)
        self.parent.show_pressure.update_text(pressure)
        return self.name

    def on_keydown(self, event):
        if event.origin == self.name:
            if event.tipo == 'Arrow':
                word = event.data['word']

                delta_y = 0

                if word == 'arriba':
                    if self.max_p < (self.pointer - 1) < self.min_p:
                        delta_y = -1
                elif word == 'abajo':
                    if self.max_p < (self.pointer + 1) < self.min_p:
                        delta_y = +1

                if delta_y:
                    self.pointer += delta_y

            elif event.tipo == 'Fin':
                self.enabled = False

    def update(self):
        if self.enabled:
            selected_pressure = self.pointer if self.pointer is not None else 0

            self.canvas.fill((0, 0, 0, 0))
            draw.line(self.canvas, (255, 0, 0, 255), (self.vol_n2, 0), (self.vol_n2, self.rect.height))
            draw.line(self.canvas, (0, 0, 0, 255), (0, self.max_p), (self.rect.right, self.max_p))
            draw.line(self.canvas, (0, 0, 0, 255), (0, self.min_p), (self.rect.right, self.min_p))
            draw.line(self.canvas, (0, 255, 0, 255), (0, self.pointer), (self.rect.right, selected_pressure))
            self.image.blit(graph, (0, 0))
            self.image.blit(self.canvas, (0, 0))

            pressure = convert(self.pointer)
            self.parent.show_pressure.update_text(pressure)


class AvailablePlanets(ListedArea):
    def populate(self, planets):
        for i, planet in enumerate(planets):
            listed = ListedPlanet(self, planet, self.rect.x + 3, i * 16 + self.rect.y + 21)
            self.listed_objects.add(listed)

    def show(self):
        super().show()
        self.populate([planet for planet in Systems.get_current().planets if not len(planet.atmosphere)])
        for listed in self.listed_objects.widgets():
            listed.show()


class ListedPlanet(PlanetButton):
    def __init__(self, parent, planet, x, y):
        super().__init__(parent, planet, x, y)
        self.object_data = planet

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.select()
            self.parent.parent.set_planet(self.object_data)


class ShownPressure(BaseWidget):
    def __init__(self, parent, x, centery):
        super().__init__(parent)
        self.f = self.crear_fuente(16)
        self.base = 'Pressure at Sea Level: '
        self.image = self.f.render(self.base, 1, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(x=x, centery=centery)

    def update_text(self, text):
        p = '{:~}'.format(round(text.to('atm'), 3))
        self.image = self.f.render('Pressure at Sea Level: ' + p, 1, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=self.rect.copy().topleft)

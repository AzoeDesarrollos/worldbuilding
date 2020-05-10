from engine.frontend.globales import Renderer, COLOR_BOX, COLOR_TEXTO, WidgetHandler, COLOR_AREA
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planet import Planet
from pygame.sprite import LayeredUpdates
from itertools import cycle
from pygame import font


class PlanetPanel(BasePanel):
    curr_x = 0
    curr_y = 440

    def __init__(self, parent):
        super().__init__('Planet', parent)
        self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.current = PlanetType(self)

        self.unit = Unit(self, 0, 416)
        self.current.properties.add(self.unit)

        self.button = TextButton(self, 490, 416)
        self.current.properties.add(self.button)

        self.planet_buttons = LayeredUpdates()

    def add_button(self, planet):
        button = PlanetButton(self.current, planet, self.curr_x, self.curr_y)
        if self.curr_x + button.w + 10 < self.rect.w - button.w + 10:
            self.curr_x += button.w + 10
        else:
            self.curr_x = 0
            self.curr_y += 32
        self.planet_buttons.add(button)
        self.current.properties.add(button)
        button.show()


class PlanetType(ObjectType):
    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Clase']
                         )
        f = font.SysFont('Verdana', 14)
        f.set_underline(True)
        render = f.render('Planets', 1, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(y=420)
        self.parent.image.blit(render, render_rect)

    def clear_values(self):
        self.parent.parent.system.add_planet(self.current)
        for button in self.properties.get_sprites_from_layer(1):
            button.text_area.clear()
        self.parent.button.disable()
        self.parent.add_button(self.current)
        self.has_values = False

    def check_values(self):
        attrs = {}
        for button in self.properties.get_sprites_from_layer(1):
            if button.text_area.value:  # not empty
                string = button.text_area.value.split(' ')[0]
                try:
                    setattr(self, button.text.lower(), float(string))
                    attrs[button.text.lower()] = float(string)
                except ValueError:
                    setattr(self, button.text.lower(), button.text_area.value)
                    attrs[button.text.lower()] = button.text_area.value

        if len(attrs) > 1:
            unit = self.parent.unit.name.lower()
            attrs['unit'] = unit if ('earth' in unit or 'jupiter' in unit) else 'earth'
            self.current = Planet(attrs)
            if unit in ('earth', 'dwarf') and self.current.mass <= self.parent.parent.system.terra_mass:
                self.parent.button.enable()
                self.parent.unit.mass_color = COLOR_TEXTO
            elif unit == 'jupiter' and self.current.mass <= self.parent.parent.system.gigant_mass:
                self.parent.button.enable()
                self.parent.unit.mass_color = COLOR_TEXTO
            else:
                self.parent.button.disable()
                self.parent.unit.mass_color = 200, 0, 0
            self.has_values = True
            self.fill()

    def fill(self, tos=None):
        tos = {
            'Mass': 'kg',
            'Radius': 'km',
            'Gravity': 'm/s**2',
            'Escape_velocity': 'km/s'
        }
        super().fill(tos)


class Meta:
    enabled = False
    img_sel = None
    img_uns = None
    img_dis = None
    selected = False
    image = None

    def show(self):
        Renderer.add_widget(self, layer=5000)
        WidgetHandler.add_widget(self)

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.add_widget(self)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.image = self.img_dis

    def on_mouseover(self):
        if self.enabled:
            self.selected = True

    def update(self):
        if self.enabled:
            if self.selected:
                self.image = self.img_sel
            else:
                self.image = self.img_uns
            self.selected = False


class Unit(Meta, BaseWidget):
    name = None
    mass_color = COLOR_TEXTO
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 12)
        self.f2 = font.SysFont('Verdana', 12, bold=True)
        render = self.f2.render('Unit: ', 1, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(bottomleft=(x, y))
        self.base_rect = self.parent.image.blit(render, render_rect)
        self.cycler = cycle(['Earth', 'Jupiter', 'Dwarf'])
        self.name = next(self.cycler)
        self.create()
        render = self.f2.render('Available mass: ', 1, COLOR_TEXTO, COLOR_BOX)
        self.mass_rect = render.get_rect(bottomleft=(x + 100, y))
        self.parent.image.blit(render, self.mass_rect)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.name = next(self.cycler)
            self.create()

    def show_mass(self):
        if self.name in ('Earth', 'Dwarf'):
            mass = self.parent.parent.system.terra_mass
        else:
            mass = self.parent.parent.system.gigant_mass
        attr = '{:,g}'.format((round(mass, 3)))
        render = self.f1.render(str(attr), 1, self.mass_color, COLOR_BOX)
        render_rect = render.get_rect(left=self.mass_rect.right + 6, bottom=self.mass_rect.bottom)
        render_rect.inflate_ip(16, 0)
        self.parent.image.fill(COLOR_BOX, render_rect)
        self.parent.image.blit(render, render_rect)

    def create(self):
        self.img_uns = self.f1.render(self.name, 1, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(self.name, 1, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(self.base_rect.right, self.base_rect.y))

    def update(self):
        self.show_mass()
        super().update()


class TextButton(Meta, BaseWidget):
    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 16)
        self.f2 = font.SysFont('Verdana', 16, bold=True)
        self.img_dis = self.f1.render('Add Planet', 1, (200, 200, 200), COLOR_BOX)
        self.img_uns = self.f1.render('Add Planet', 1, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render('Add Planet', 1, COLOR_TEXTO, COLOR_BOX)

        self.image = self.img_dis
        self.rect = self.image.get_rect(bottomleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.clear_values()


class PlanetButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, planet, x, y):
        super().__init__(parent)
        self.planet_data = planet
        self.f1 = font.SysFont('Verdana', 13)
        self.f2 = font.SysFont('Verdana', 13, bold=True)
        name = 'Terrestial'
        if planet.clase == 'Terrestial Planet':
            name = 'Terrestial'
        elif planet.clase == 'Gas Giant':
            name = 'Giant'
        elif planet.clase == 'Puffy Giant':
            name = 'Puffy'
        elif planet.clase == 'Gas Dwarf':
            name = 'Gas Dwarf'
        elif planet.clase == 'Dwarf Planet':
            name = 'Dwarf'
        self.img_uns = self.f1.render(name, 1, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, 1, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.current = self.planet_data
            self.parent.parent.parent.system.set_current(self.planet_data)
            self.parent.has_values = True
            self.parent.fill()

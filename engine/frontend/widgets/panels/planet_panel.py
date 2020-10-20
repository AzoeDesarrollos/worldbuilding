from engine.frontend.globales import COLOR_BOX, COLOR_TEXTO, COLOR_AREA, WidgetGroup
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import system
from engine.backend.eventhandler import EventHandler
from engine.equations.planet import Planet
from itertools import cycle
from pygame import font


class PlanetPanel(BasePanel):
    curr_x = 0
    curr_y = 440
    unit = None
    is_visible = False

    def __init__(self, parent):
        super().__init__('Planet', parent)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.current = PlanetType(self)

        self.unit = Unit(self, 0, 416)
        self.current.properties.add(self.unit)

        self.button = TextButton(self, 'Add Planet', 490, 416)
        self.current.properties.add(self.button)

        self.planet_buttons = WidgetGroup()

    def show(self):
        super().show()
        self.is_visible = True

    def add_button(self, planet):
        button = PlanetButton(self.current, planet, self.curr_x, self.curr_y)
        self.planet_buttons.add(button)
        self.sort_buttons()
        self.current.properties.add(button, layer=2)

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.planet_buttons.widgets():
            bt.move(x, y)
            if not self.area_buttons.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def on_mousebuttondown(self, event):
        if self.area_buttons.collidepoint(event.pos):
            buttons = self.planet_buttons.widgets()
            last_is_hidden = not buttons[-1].is_visible
            first_is_hidden = not buttons[0].is_visible
            if event.button == 4 and first_is_hidden:
                self.curr_y += 32
            elif event.button == 5 and last_is_hidden:
                self.curr_y -= 32
            self.sort_buttons()


class PlanetType(ObjectType):
    counter = 0

    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Albedo', 'Greenhouse', 'Clase']
                         )
        f = font.SysFont('Verdana', 14)
        f.set_underline(True)
        render = f.render('Planets', True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(y=420)
        self.parent.image.blit(render, render_rect)

        f = font.SysFont('Verdana', 16, bold=True)
        self.habitable = f.render('Habitable', True, (0, 255, 0), COLOR_BOX)
        self.hab_rect = self.habitable.get_rect(right=self.parent.rect.right - 10, y=self.parent.rect.y + 50)
        EventHandler.register(self.save_planet, 'Save')
        EventHandler.register(self.load_planet, 'LoadData')
        EventHandler.register(self.clear, 'ClearData')

    def save_planet(self, event):
        p = self.current
        if p is not None:
            data = {
                'name': p.name,
                'mass': p.mass.m,
                'radius': p.radius.m,
                'unit': p.unit,
                'atmosphere': p.atmosphere,
                'clase': p.clase}
            EventHandler.trigger(event.tipo + 'Data', 'Planet', {"Planets": [data]})

    def load_planet(self, event):
        if 'Planets' in event.data:
            self.current = Planet(event.data['Planets'][0])
            self.create_button()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            for button in self.properties.get_sprites_from_layer(1):
                button.text_area.clear()
        self.has_values = False
        self.parent.image.fill(COLOR_BOX, self.hab_rect)

    def create_button(self):
        create = system.add_planet(self.current)
        if create:
            for button in self.properties.get_sprites_from_layer(1):
                button.text_area.clear()
            self.parent.button.disable()
            self.parent.add_button(self.current)
            self.has_values = False
            self.parent.image.fill(COLOR_BOX, self.hab_rect)

    def toggle_habitable(self):
        if self.current.habitable:
            self.parent.image.blit(self.habitable, self.hab_rect)
        else:
            self.parent.image.fill(COLOR_BOX, self.hab_rect)

    def check_values(self):
        attrs = {}
        for button in self.properties.get_sprites_from_layer(1):
            if button.text_area.value:  # not empty
                string = str(button.text_area.value).split(' ')[0]
                try:
                    setattr(self, button.text.lower(), float(string))
                    attrs[button.text.lower()] = float(string)
                except ValueError:
                    setattr(self, button.text.lower(), button.text_area.value)
                    attrs[button.text.lower()] = button.text_area.value

        if len(attrs) > 1:
            unit = self.parent.unit.name.lower()
            attrs['unit'] = 'jupiter' if unit == 'gas giant' else 'earth'
            self.current = Planet(attrs)
            self.toggle_habitable()
            if self.current.mass <= system.body_mass:
                self.parent.button.enable()
                self.parent.unit.mass_number.mass_color = COLOR_TEXTO
            else:
                self.parent.button.disable()
                self.parent.unit.mass_number.mass_color = 200, 0, 0
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

    is_visible = False
    has_mouseover = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.image = self.img_dis

    def on_mouseover(self):
        self.has_mouseover = True
        if self.enabled:
            self.image = self.img_sel

    def select(self):
        self.selected = True
        if self.enabled:
            self.image = self.img_sel

    def deselect(self):
        self.selected = False
        self.image = self.img_uns

    def update(self):
        if all([not self.has_mouseover, not self.selected, self.enabled]):
            self.image = self.img_uns
        self.has_mouseover = False


class Unit(Meta, BaseWidget):
    name = ''
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 12)
        self.f2 = font.SysFont('Verdana', 12, bold=True)
        render = self.f2.render('Type: ', True, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(bottomleft=(x, y))
        self.base_rect = self.parent.image.blit(render, render_rect)
        self.rect = self.base_rect.copy()
        self.cycler = cycle(['Habitable', 'Terrestial', 'Dwarf Planet', 'Gas Dwarf', 'Gas Giant'])
        self.mass_number = ShownMass(self)
        self.name = next(self.cycler)
        self.create()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.name = next(self.cycler)
            self.create()

    def show(self):
        super().show()
        self.mass_number.show()

    def hide(self):
        super().hide()
        self.mass_number.hide()

    def create(self):
        self.img_uns = self.f1.render(self.name, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(self.name, True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(self.base_rect.right, self.base_rect.y))


class ShownMass(BaseWidget):
    show_jovian_mass = True
    mass_color = COLOR_TEXTO

    def __init__(self, parent):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 12, bold=True)
        self.f2 = font.SysFont('Verdana', 12)
        self.image = self.f1.render('Available mass: ', True, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(left=self.parent.rect.right + 100, bottom=self.parent.rect.bottom)
        self.mass_img = self.f2.render(self.show_mass(), True, self.mass_color, COLOR_BOX)
        self.mass_rect = self.mass_img.get_rect(left=self.rect.right + 6, bottom=self.rect.bottom)
        self.mass_rect.width += 50

        self.grandparent = self.parent.parent
        self.grandparent.image.blit(self.mass_img, self.mass_rect)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.show_jovian_mass = not self.show_jovian_mass

    def show_mass(self):
        mass = system.get_available_mass()
        if not self.show_jovian_mass:
            mass = mass.to('earth_mass')
        attr = '{:,g}'.format((round(mass, 3)))
        return attr

    def update(self):
        self.grandparent.image.fill(COLOR_BOX, self.mass_rect)
        self.mass_img = self.f2.render(self.show_mass(), True, self.mass_color, COLOR_BOX)
        self.mass_rect = self.mass_img.get_rect(left=self.rect.right + 6, bottom=self.rect.bottom)
        self.mass_rect.width += 50
        self.parent.parent.image.blit(self.mass_img, self.mass_rect)


class TextButton(Meta, BaseWidget):
    def __init__(self, parent, text, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 16)
        self.f2 = font.SysFont('Verdana', 16, bold=True)
        self.img_dis = self.f1.render(text, True, (200, 200, 200), COLOR_BOX)
        self.img_uns = self.f1.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(text, True, COLOR_TEXTO, COLOR_BOX)

        self.image = self.img_dis
        self.rect = self.image.get_rect(bottomleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.create_button()


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
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.current = self.planet_data
            system.set_current(self.planet_data)
            self.parent.has_values = True
            self.parent.fill()
            self.parent.toggle_habitable()

    def update(self):
        super().update()
        if self.parent.parent.is_visible:
            self.show()
        else:
            self.hide()

    def move(self, x, y):
        self.rect.topleft = x, y

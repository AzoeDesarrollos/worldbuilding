from engine.frontend.globales import COLOR_BOX, COLOR_TEXTO, COLOR_AREA, WidgetGroup
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from .common import PlanetButton, TextButton, Meta
from engine.equations.planet import Planet
from engine import q


class PlanetPanel(BasePanel):
    curr_x = 0
    curr_y = 440
    unit = None
    is_visible = False
    last_idx = None

    def __init__(self, parent):
        super().__init__('Planet', parent)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.current = PlanetType(self)
        self.properties = WidgetGroup()

        self.unit = Unit(self, 0, 416)
        self.properties.add(self.unit)

        self.button = AddPlanetButton(self, 490, 416)
        self.properties.add(self.button)
        self.planet_buttons = WidgetGroup()
        EventHandler.register(self.save_planets, 'Save')

    def save_planets(self, event):
        data = []
        for system in Systems.get_systems():
            for planet_button in self.planet_buttons.widgets():
                planet = planet_button.object_data
                if planet in system.planets:
                    planet_data = {
                        'name': planet.name,
                        'mass': planet.mass.m,
                        'radius': planet.radius.m,
                        'unit': planet.unit,
                        'atmosphere': planet.atmosphere,
                        'clase': planet.clase,
                        'system': system.id
                    }
                    data.append(planet_data)
        EventHandler.trigger(event.tipo + 'Data', 'Planet', {"Planets": data})

    def add_button(self, planet):
        button = CreatedPlanet(self.current, planet, self.curr_x, self.curr_y)
        self.planet_buttons.add(button, layer=Systems.get_current_idx())
        self.sort_buttons()
        self.properties.add(button, layer=2)

    def show_current(self, idx):
        for button in self.planet_buttons.widgets():
            button.hide()
        for button in self.planet_buttons.get_widgets_from_layer(idx):
            button.show()

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.planet_buttons.get_widgets_from_layer(Systems.get_current_idx()):
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
        if event.button == 1:
            super().on_mousebuttondown(event)

        elif event.button in (4, 5):
            buttons = self.planet_buttons.widgets()
            if self.area_buttons.collidepoint(event.pos) and len(buttons):
                last_is_hidden = not buttons[-1].is_visible
                first_is_hidden = not buttons[0].is_visible
                if event.button == 4 and first_is_hidden:
                    self.curr_y += 32
                elif event.button == 5 and last_is_hidden:
                    self.curr_y -= 32
                self.sort_buttons()

    def show(self):
        super().show()
        for item in self.properties.widgets():
            item.show()

    def hide(self):
        super().hide()
        for item in self.properties.widgets():
            item.hide()

    def update(self):
        idx = Systems.get_current_idx()
        if idx != self.last_idx:
            self.show_current(idx)
            self.last_idx = idx


class PlanetType(ObjectType):
    counter = 0

    loaded_data = None

    def __init__(self, parent):
        rel_props = ['Mass', 'Radius', 'Surface Gravity', 'Escape velocity']
        rel_args = ['mass', 'radius', 'gravity', 'escape_velocity']
        abs_args = ['density', 'volume', 'surface', 'circumference', 'albedo', 'greenhouse', 'clase']
        abs_props = ['Density', 'Volume', 'Surface Area', 'Circumference', 'Albedo (bond)', 'Greenhouse Effect',
                     'Clase']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        f = self.crear_fuente(14)
        f.set_underline(True)
        render = f.render('Planets', True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(y=420)
        self.parent.image.blit(render, render_rect)

        f = self.crear_fuente(16, bold=True)
        self.habitable = f.render('Habitable', True, (0, 255, 0), COLOR_BOX)
        self.hab_rect = self.habitable.get_rect(right=self.parent.rect.right - 10, y=self.parent.rect.y + 50)

        EventHandler.register(self.load_planet, 'LoadData')

    def load_planet(self, event):
        if 'Planets' in event.data:
            self.loaded_data = event.data['Planets'][0]

    def set_planet(self, planet):
        self.current = planet
        self.fill()
        self.toggle_habitable()

    def show(self):
        super().show()
        if self.loaded_data is not None:
            self.current = Planet(self.loaded_data)
            self.create_button()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            for button in self.properties.get_sprites_from_layer(1):
                button.text_area.clear()
        self.has_values = False
        self.parent.image.fill(COLOR_BOX, self.hab_rect)

    def create_button(self):
        create = Systems.get_current().add_astro_obj(self.current)
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
            if self.current.mass <= Systems.get_current().body_mass:
                self.parent.button.enable()
                self.parent.unit.mass_number.mass_color = COLOR_TEXTO
            else:
                self.parent.button.disable()
                self.parent.unit.mass_number.mass_color = 200, 0, 0
            self.fill()

    def fill(self, tos=None):
        tos = {
            'mass': 'kg',
            'radius': 'km',
            'gravity': 'm/s**2',
            'escape_velocity': 'km/s'
        }
        super().fill(tos)


class Unit(Meta, BaseWidget):
    name = ''
    enabled = True
    mass_number = None
    curr_idx = 0

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = self.crear_fuente(12)
        self.f2 = self.crear_fuente(12, bold=True)
        render = self.f2.render('Type: ', True, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(bottomleft=(x, y))
        self.base_rect = self.parent.image.blit(render, render_rect)
        self.rect = self.base_rect.copy()
        self.names = ['Habitable', 'Terrestial', 'Dwarf Planet', 'Gas Dwarf', 'Gas Giant']
        self.name = self.names[self.curr_idx]
        self.create()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.cycle(+1)

        elif event.button == 3:
            self.cycle(-1)

    def cycle(self, delta):
        self.curr_idx += delta
        if not 0 <= abs(self.curr_idx) < len(self.names):
            self.curr_idx = 0
        self.name = self.names[self.curr_idx]
        self.create()

    def show(self):
        super().show()
        if self.mass_number is None:
            self.mass_number = ShownMass(self)
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
        self.f1 = self.crear_fuente(12, bold=True)
        self.f2 = self.crear_fuente(12)
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
        try:
            mass = Systems.get_current().get_available_mass()
        except AttributeError:
            mass = q(0, 'jupiter_mass')
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


class AddPlanetButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Planet', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.create_button()


class CreatedPlanet(PlanetButton):
    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.set_planet(self.object_data)

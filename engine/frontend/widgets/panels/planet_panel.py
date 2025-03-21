from engine.frontend.globales import COLOR_BOX, COLOR_TEXTO, COLOR_AREA, ANCHO, Group, NUEVA_LINEA
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.sprite_star import PlanetSprite
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.basewidget import BaseWidget
from engine.frontend.widgets.meta import Meta
from .common import ColoredBody, TextButton
from engine.equations.space import Universe
from engine.equations.planet import Planet
from engine.backend import EventHandler
from itertools import cycle
from pygame import Rect


class PlanetPanel(BasePanel):
    unit = None
    is_visible = False
    last_id = None
    mass_number = None

    def __init__(self, parent):
        super().__init__('Planet', parent)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.current = PlanetType(self)
        self.properties = Group()
        self.unit = Unit(self, 0, 416)
        text = 'Create your planets here.\n\n'
        text += 'You can alternate among the planet types by clicking in the "Type" button below.\n\n'
        text += 'Then click any of its parameters to lauch a graph for its creation.\n\n'
        text += "Don't forget to set its axial tilt before leaving."
        self.erase_text_area = self.write2(text, self.crear_fuente(14), fg=COLOR_AREA, width=300, x=250, y=100, j=1)
        self.mass_number = ShownMass(self)
        self.button_add = AddPlanetButton(self, ANCHO - 13, 398)
        self.button_del = DelPlanetButton(self, ANCHO - 13, 416)
        self.properties.add(self.unit, self.mass_number, self.button_add, self.button_del)
        self.planet_buttons = Group()
        self.planets = []
        EventHandler.register(self.save_planets, 'Save')
        EventHandler.register(self.name_current, 'NameObject')
        EventHandler.register(self.export_data, 'ExportData')

    def save_planets(self, event):
        data = {}
        for nei in Universe.current_galaxy.stellar_neighbourhoods:
            for system in nei.get_p_systems():
                for planet in system.planets:
                    planet_data = {
                        'name': planet.name,
                        'mass': planet.mass.m,
                        'radius': planet.radius.m,
                        'unit': planet.unit,
                        'atmosphere': planet.atmosphere,
                        'composition': planet.composition,
                        'clase': planet.clase,
                        'system': system.id,  # the ID of the system is the same as the its star's ID
                        'albedo': planet.albedo.m,
                        'tilt': planet.tilt.m if type(planet.tilt) is not str else planet.tilt,
                        'flagged': planet.flagged,
                        'biomes': planet.biomes if planet.biomes is not None else None
                    }
                    data[planet.id] = planet_data
        EventHandler.trigger(event.tipo + 'Data', 'Planet', {"Planets": data})
        self.current.loaded_data = None

    def add_button(self, planet, erase=True):
        button = CreatedPlanet(self.current, planet, str(planet), self.curr_x, self.curr_y)
        if planet.system_id is not None:
            layer_number = planet.system_id
        else:
            layer_number = self.last_id
            planet.system_id = layer_number
        self.planets.append(planet)
        if planet.idx is None:
            planet.idx = len([i for i in self.planets if i.cls == planet.cls])
        self.planet_buttons.add(button, layer=layer_number)
        if self.is_visible:
            planets = self.planet_buttons.get_widgets_from_layer(self.last_id)
            self.sort_buttons(planets)
        self.properties.add(button, layer=3)
        if erase:
            self.image.fill(COLOR_BOX, self.erase_text_area)
        return button

    def del_button(self, planet):
        button = [i for i in self.planet_buttons.widgets() if i.object_data == planet][0]
        self.planet_buttons.remove(button)
        self.planets.remove(planet)
        planets = self.planet_buttons.get_widgets_from_layer(self.last_id)
        self.sort_buttons(planets)
        self.properties.remove(button)
        self.button_del.disable()

    def show_current(self, idx):
        self.current.load_data(idx)
        for button in self.planet_buttons.widgets():
            button.hide()
        if len(self.planet_buttons):
            planets = self.planet_buttons.get_widgets_from_layer(idx)
            self.sort_buttons(planets)

    def select_one(self, btn=None):
        for button in self.planet_buttons.widgets():
            button.deselect()

        if btn is not None:
            btn.select()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if event.data['button'] == 1:
                super().on_mousebuttondown(event)

            elif event.data['button'] in (4, 5):
                buttons = self.planet_buttons.widgets()
                if self.area_buttons.collidepoint(event.data['pos']) and len(buttons):
                    last_is_hidden = not buttons[-1].is_visible
                    first_is_hidden = not buttons[0].is_visible
                    if event.data['button'] == 4 and first_is_hidden:
                        self.curr_y += NUEVA_LINEA
                    elif event.data['button'] == 5 and last_is_hidden:
                        self.curr_y -= NUEVA_LINEA
                    planets = self.planet_buttons.get_widgets_from_layer(self.last_id)
                    self.sort_buttons(planets, overriden=True)

    def show(self):
        super().show()
        for item in self.properties.get_widgets_from_layer(1):
            item.show()
        self.enable_buttons()
        if self.current.has_values:
            self.current.fill()
        if self.last_id is not None:
            self.show_current(self.last_id)

    def hide(self):
        if len(self.planets) <= 1:
            self.parent.set_skippable('Double Planets', True)
        else:
            self.parent.set_skippable('Double Planets', False)

        super().hide()
        for item in self.properties.widgets():
            item.hide()

    def enable(self):
        super().enable()
        self.current.enable()

    def disable(self):
        super().disable()
        self.current.disable()

    def enable_buttons(self):
        for button in self.planet_buttons.widgets():
            button.enable()

    def disable_buttons(self):
        for button in self.planet_buttons.widgets():
            button.disable()

    def update(self):
        if Universe.current_galaxy is not None:
            idx = Universe.current_planetary().id
        else:
            idx = self.last_id

        if idx != self.last_id:
            self.show_current(idx)
            self.last_id = idx

    def name_current(self, event):
        if event.data['object'] in self.planets:
            planet = event.data['object']
            planet.set_name(event.data['name'])

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class PlanetType(ObjectType):

    def __init__(self, parent):
        rel_props = ['Mass', 'Radius', 'Surface gravity', 'Escape velocity']
        rel_args = ['mass', 'radius', 'gravity', 'escape_velocity']
        abs_args = ['density', 'volume', 'surface', 'circumference',
                    'tilt', 'spin', 'rotation', 'albedo', 'greenhouse', 'clase']
        abs_props = ['Density', 'Volume', 'Surface area', 'Circumference',
                     'Axial tilt', 'Spin', 'Rotation Rate', 'Albedo (bond)', 'Greenhouse effect', 'Class']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 0, 1)
        self.set_modifiables('absolutes', 4, 6)
        self.absolutes.widgets()[4].set_min_and_max(0, 100)
        f = self.crear_fuente(14)
        f.set_underline(True)
        render = f.render('Planets', True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(y=420)
        self.parent.image.blit(render, render_rect)

        f = self.crear_fuente(16, bold=True)
        self.habitable = f.render('Habitable', True, (0, 255, 0), COLOR_BOX)
        self.uninhabitable = f.render('Uninhabitable', True, (255, 0, 0), COLOR_BOX)
        self.hab_rect = self.habitable.get_rect(centerx=460, y=self.parent.rect.y + 250)
        self.uhb_rect = self.uninhabitable.get_rect(centerx=460, y=self.parent.rect.y + 250)

        self.held_data = {}
        EventHandler.register(self.hold_loaded_bodies, 'LoadPlanets')

    def enable(self):
        widgets = self.properties.widgets()
        for arg in widgets:
            arg.enable()
        super().enable()

    def disable(self):
        for arg in self.properties.widgets():
            arg.disable()
        super().disable()

    def hold_loaded_bodies(self, event):
        if 'Planets' in event.data and len(event.data['Planets']):
            self.held_data.update(event.data['Planets'])

    def load_data(self, idx):
        if len(self.held_data):
            for system in Universe.nei().get_p_systems():
                for i, id in enumerate(self.held_data):
                    planet_data = self.held_data[id]
                    planet_data['idx'] = i
                    if planet_data['system'] == system.id:
                        do_erase = idx == system.id
                        planet_data['id'] = id
                        if system is not None:
                            planet_data['parent'] = system

                        planet = Planet(planet_data)
                        if planet not in self.parent.planets:
                            btn = self.create_button(planet, erase=do_erase)
                            if planet.composition is not None:
                                planet.sprite = PlanetSprite(self, planet, 460, 100)
                                self.properties.add(planet.sprite, layer=3)
                            btn.hide()
            self.held_data.clear()

    def set_planet(self, planet):
        if self.current is not None and self.current.sprite is not None:
            self.current.sprite.hide()
        self.current = planet
        self.fill()
        self.toggle_habitable()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            for button in self.properties.get_widgets_from_layer(1):
                button.clear()
        self.parent.select_one()
        self.parent.button_del.disable()
        self.has_values = False
        self.parent.image.fill(COLOR_BOX, self.parent.erase_text_area)
        if self.current is not None and self.current.sprite is not None:
            self.current.sprite.kill()

    def create_button(self, planet=None, erase=True):
        if planet is None:
            planet = self.current
            system = planet.parent
        else:
            system = Universe.get_astrobody_by(planet.system_id, 'id')
        if hasattr(system, 'planetary'):
            system.planetary.add_astro_obj(planet)
        elif system.id == 'rogues':
            system.add_astro_obj(planet)

        for button in self.properties.get_widgets_from_layer(1):
            button.clear()
        self.parent.button_add.disable()
        btn = self.parent.add_button(planet, erase)
        self.has_values = False
        if erase:
            self.parent.image.fill(COLOR_BOX, self.hab_rect)
        if self.current is not None and self.current.sprite is not None:
            self.current.sprite.hide()
        planets = self.parent.planet_buttons.get_widgets_from_layer(system.id)
        self.parent.sort_buttons(planets)
        return btn

    # def destroy_button(self):
    #     destroyed = Systems.get_system_by_id(self.current.system_id).remove_astro_obj(self.current)
    #     if destroyed:
    #         self.current.sprite.kill()
    #         self.parent.image.fill(COLOR_BOX, self.uhb_rect)
    #         self.parent.del_button(self.current)
    #         self.erase()

    def toggle_habitable(self):
        self.parent.image.fill(COLOR_BOX, self.uhb_rect)
        if self.current.habitable:
            self.parent.image.blit(self.habitable, self.hab_rect)
        else:
            self.parent.image.blit(self.uninhabitable, self.uhb_rect)

    def check_values(self, composition):
        attrs = {}
        for button in self.properties.get_widgets_from_layer(1):
            attr = ''
            if button in self.relatives:
                idx = self.relatives.widgets().index(button)
                attr = self.relative_args[idx]
            elif button in self.absolutes:
                idx = self.absolutes.widgets().index(button)
                attr = self.absolute_args[idx]
            if button.text_area.value:  # not empty
                string = str(button.text_area.value).split(' ')[0]
                try:
                    setattr(self, attr, float(string))
                    attrs[attr] = float(string)
                except ValueError:
                    setattr(self, attr, button.text_area.value)
                    attrs[attr] = button.text_area.value

        if len(attrs) > 1:
            unit = self.parent.unit.name.lower()
            attrs['unit'] = 'jupiter' if unit == 'gas giant' else 'earth'
            if composition is not None:
                attrs['composition'] = composition
            system = Universe.nei().get_current()
            attrs['parent'] = system
            self.current = Planet(attrs)
            self.toggle_habitable()
            available_mass = system.get_available_mass()
            if available_mass == 'Unlimited' or system.body_mass > 0:
                self.parent.button_add.enable()
                self.parent.mass_number.mass_color = COLOR_TEXTO
            else:
                self.parent.button_add.disable()
                self.parent.mass_number.mass_color = 200, 0, 0
            self.parent.disable_buttons()
            self.fill()

    def update_value(self, button, data):
        idx = self.absolutes.widgets().index(button)
        attr = self.absolute_args[idx]
        setattr(self.current, attr, data)
        self.toggle_habitable()
        self.fill()

    def fill(self, tos=None):
        tos = {
            1: {
                'mass': 'kg',
                'radius': 'km',
                'gravity': 'm/s**2',
                'escape_velocity': 'km/s',
                'rotation': 'hours/day'
            }
        }
        self.parent.image.fill(COLOR_BOX, self.parent.erase_text_area)
        super().fill(tos)

        if self.current.sprite is None and self.current.composition is not None:
            self.current.sprite = PlanetSprite(self, self.current, 460, 100)
            self.properties.add(self.current.sprite, layer=3)
            self.parent.properties.add(self.current.sprite)

        if self.current.sprite is not None:
            self.current.sprite.show()


class Unit(Meta):
    name = ''
    enabled = True
    mass_number = None
    curr_idx = 0
    image = None

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
        if event.origin == self:
            if event.data['button'] == 1:
                self.cycle(+1)

            elif event.data['button'] == 3:
                self.cycle(-1)

    def cycle(self, delta):
        self.curr_idx += delta
        if not 0 <= abs(self.curr_idx) < len(self.names):
            self.curr_idx = 0
        self.name = self.names[self.curr_idx]
        self.create()

    def create(self):
        self.img_uns = self.f1.render(self.name, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(self.name, True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(self.base_rect.right, self.base_rect.y))


class ShownMass(BaseWidget):
    show_jovian_mass = True
    mass_color = COLOR_TEXTO
    mass_img = None

    def __init__(self, parent):
        super().__init__(parent)
        self.f1 = self.crear_fuente(12, bold=True)
        self.f2 = self.crear_fuente(12)
        self.image = self.f1.render('Available mass: ', True, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(left=200, bottom=416)
        self.mass_rect = Rect(self.rect.right + 3, self.rect.y, 150, 15)

        self.units = ['earth_mass', 'jupiter_mass', 'kg']
        self.unit_cycler = cycle(self.units)
        self.current_unit = next(self.unit_cycler)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.current_unit = next(self.unit_cycler)

    def show_mass(self):
        system = Universe.nei().get_current()
        if not self.parent.enabled:
            self.parent.enable()

        mass = system.get_available_mass().to(self.current_unit)
        if not self.parent.enabled:
            self.parent.enable()

        if mass is not None:
            rounded = round(mass, 4)
            if rounded.m <= 0:
                mass = mass.to('kg')
            else:
                mass = mass.to(self.current_unit)
            return '{:,g~}'.format(mass)
        else:
            return ''

    def update(self):
        if Universe.current_galaxy is not None:
            self.parent.image.fill(COLOR_BOX, self.mass_rect)
            self.mass_img = self.f2.render(self.show_mass(), True, self.mass_color, COLOR_BOX)
            self.parent.image.blit(self.mass_img, self.mass_rect)


class AddPlanetButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Planet', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.current.create_button()
            self.parent.enable_buttons()


class DelPlanetButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Planet', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.current.destroy_button()


class CreatedPlanet(ColoredBody):

    def disable(self):
        self.enabled = False

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.set_planet(self.object_data)
            self.parent.parent.select_one(self)
        # return self

    def update(self):
        if self.object_data.habitable is True:
            self.set_color(self.object_data)
            self.crear(str(self.object_data))
            self.image = self.img_sel
        super().update()
        if self.object_data.flagged:
            self.kill()

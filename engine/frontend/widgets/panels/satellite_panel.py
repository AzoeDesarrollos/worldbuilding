from engine.frontend.globales import COLOR_AREA, COLOR_BOX, COLOR_TEXTO, COLOR_DISABLED, COLOR_SELECTED
from engine.backend import EventHandler, material_densities, roll, choice, ureg
from engine.equations.satellite import major_moon_by_composition
from engine.frontend.globales import ANCHO, ALTO, Group
from engine.frontend.widgets.values import ValueText
from engine.frontend.widgets.meta import Meta
from .common import TextButton, ColoredBody
from engine.equations import Universe
from ..object_type import ObjectType
from .planet_panel import ShownMass
from .base_panel import BasePanel
from pygame import Surface, Rect
from itertools import cycle
from ..pie import PieChart


class SatellitePanel(BasePanel):
    mass_number = None
    last_idx = None

    with_additional_mode = False

    def __init__(self, parent):
        super().__init__('Satellite', parent, modes=3)
        self.current = SatelliteType(self)
        f1 = self.crear_fuente(16, underline=True)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 132, 178])
        self.area_buttons = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 300, 178))
        self.curr_x = self.area_buttons.x + 3
        self.curr_y = self.area_buttons.y + 21

        self.properties = Group()
        self.mass_number = ShownMass(self)
        self.button_add = AddMoonButton(self, ANCHO - 13, 398)
        self.button_del = DelMoonButton(self, ANCHO - 13, 416)
        self.f3 = self.crear_fuente(11)
        self.area_type = Rect(32, 32, ANCHO, ALTO - (self.area_buttons.h + 200))
        text = 'Create your major satellites here.\n\n'
        text += 'Input its radius first, and then select its composition below.\n\n'
        text += 'You can copy its compostition from a given planet or set it randomly.\n\n'
        text += 'You can also set the percentages manually.'
        self.erase_text_area = self.write2(text, self.crear_fuente(14), fg=COLOR_AREA, width=300, x=250, y=100, j=1)
        ra = self.write('Composition', f1, COLOR_AREA, topleft=(18, 420))
        self.write('Satellites', f1, COLOR_AREA, topleft=(self.area_buttons.x + 2, self.area_buttons.y))
        self.copy_button = CopyCompositionButton(self, ra.left, ra.bottom + 6, ra.centerx)
        self.random_button = RandomCompositionButton(self, ra.right, ra.bottom + 6, ra.centerx)

        self.planet_name_rect = Rect(0, 0, ra.w, self.f3.get_height())
        self.planet_name_rect.centerx = ra.centerx
        self.planet_name_rect.top = self.copy_button.text_rect.bottom

        self.properties.add(self.button_add, self.button_del, self.copy_button,
                            self.mass_number, self.random_button, layer=1)
        self.satellites = Group()
        self.moons = []
        EventHandler.register(self.save_satellites, 'Save')
        EventHandler.register(self.name_current, 'NameObject')
        EventHandler.register(self.hold_loaded_bodies, 'LoadSatellites')
        EventHandler.register(self.export_data, 'ExportData')
        self.held_data = {}

    def hold_loaded_bodies(self, event):
        if 'Satellites' in event.data and len(event.data['Satellites']):
            self.held_data.update(event.data['Satellites'])

    def load_satellites(self):
        self.enable()
        for idx, id in enumerate(self.held_data):
            satellite_data = self.held_data[id]
            satellite_data['id'] = id
            moon = major_moon_by_composition(satellite_data)
            moon.idx = len([i for i in Universe.current_planetary().satellites if i.cls == moon.cls])
            system_id = satellite_data['system']
            moon_system = Universe.nei().get_system(system_id).planetary
            moon_system.add_astro_obj(moon)
            self.add_button(moon)

        self.held_data.clear()

    def save_satellites(self, event):
        data = {}
        for moon_button in self.satellites.widgets():
            moon = moon_button.object_data
            moon_data = {
                'name': moon.name,
                'radius': moon.radius.m,
                'composition': moon.composition,
                'system': moon.system_id,
                'flagged': moon.flagged
            }
            data[moon.id] = moon_data
            EventHandler.trigger(event.tipo + 'Data', 'Planet', {"Satellites": data})

    def show_current(self, idx):
        for button in self.satellites.widgets():
            button.hide()
        for button in self.satellites.get_widgets_from_layer(idx):
            button.show()
        self.sort_buttons(self.satellites.get_widgets_from_layer(Universe.current_planetary().id), x=self.curr_x)

    def add_button(self, moon):
        button = SatelliteButton(self.current, moon, str(moon), self.curr_x, self.curr_y)
        if moon.system_id is not None:
            layer_number = moon.system_id
        else:
            layer_number = Universe.current_planetary().id
            moon.system_id = layer_number

        self.moons.append(moon)
        self.satellites.add(button, layer=layer_number)
        self.properties.add(button, layer=2)
        if self.is_visible:
            satellites = self.satellites.get_widgets_from_layer(Universe.current_planetary().id)
            self.sort_buttons(satellites, x=self.curr_x, y=self.curr_y)
            self.current.erase()
        self.button_add.disable()

    def del_button(self, satellite):
        button = [i for i in self.satellites.widgets() if i.object_data == satellite][0]
        self.moons.remove(satellite)
        self.satellites.remove(button)
        button.hide()
        self.sort_buttons(self.satellites.get_widgets_from_layer(Universe.current_planetary().id))
        self.properties.remove(button)
        self.button_del.disable()

    def name_current(self, event):
        if event.data['object'] in self.moons:
            moon = event.data['object']
            moon.set_name(event.data['name'])

    def select_one(self, btn):
        for button in self.satellites.widgets():
            button.deselect()
        btn.select()

    def show(self):
        super().show()
        self.load_satellites()
        for pr in self.properties.get_widgets_from_layer(1):
            pr.show()
        if self.last_idx is not None:
            self.show_current(self.last_idx)

    def hide(self):
        if len(self.moons) < 1:
            self.parent.set_skippable('Calendar', True)
        else:
            self.parent.set_skippable('Calendar', False)
        super().hide()
        for pr in self.properties.widgets():
            pr.hide()

    def enable(self):
        super().enable()
        self.current.enable()

    def clear(self):
        self.image.fill(COLOR_AREA, [0, 498, 130, 14])
        self.button_add.disable()
        self.button_del.disable()
        for button in self.satellites.widgets():
            button.deselect()

    def update(self):
        if Universe.current_galaxy is not None:
            idx = Universe.current_planetary().id
        else:
            idx = self.last_idx

        if idx != self.last_idx:
            self.image.fill(COLOR_AREA, [0, 498, 130, 14])
            self.current.pie.set_values()
            self.show_current(idx)
            self.last_idx = idx

    def write_name(self, planet):
        r = self.image.fill(COLOR_AREA, [0, 498, 130, 14])
        text = f'[{str(planet)}]'
        self.write(text, self.f3, COLOR_AREA, top=self.planet_name_rect.y, centerx=r.centerx)

    def clear_name(self):
        self.image.fill(COLOR_AREA, [0, 498, 130, 14])

    def write_button_desc(self, button):
        self.image.blit(button.text_render, button.text_rect)

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class SatelliteType(ObjectType):

    def __init__(self, parent):
        rel_props = ['Mass', 'Radius', 'Surface Gravity', 'Escape velocity']
        rel_args = ['mass', 'radius', 'gravity', 'escape_velocity']
        abs_args = ['density', 'volume', 'surface', 'circumference', 'tilt', 'spin', 'rotation', 'clase']
        abs_props = ['Density', 'Volume', 'Surface Area', 'Circumference',
                     'Axial tilt', 'Spin', 'Rotation Rate', 'Class']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 1)
        self.show_layers.append(3)

        for i, item in enumerate(self.relatives.widgets() + self.absolutes.widgets()):
            item.rect.y += i * 4
            item.text_area.rect.y += i * 4

        names = sorted(material_densities.keys())
        d = {names[0]: 33, names[1]: 33, names[2]: 34}
        self.pie = PieChart(self, 200, 500, 65, d)
        for obj in self.pie.chart.widgets():
            self.properties.add(obj, layer=3)

        for i, name in enumerate(sorted(d)):
            a = ValueText(self, name.capitalize(), 3, 500 + 30 + i * 21, bg=COLOR_AREA)
            a.text_area.value = str(d[name]) + ' %'
            self.properties.add(a, layer=2)
            a.modifiable = True

        self.pie.hide()

    def calculate(self):
        data = {'composition': None}
        if self.current is None:
            data['composition'] = {}
        else:
            data['composition'] = self.current.composition

        if not len(data['composition']):
            for material in self.properties.get_widgets_from_layer(2):
                if material.text_area.value:  # not empty
                    text = material.text_area.value.strip(' %')
                    # noinspection PyUnresolvedReferences
                    data['composition'][material.text.lower()] = float(text)

        for item in self.properties.get_widgets_from_layer(1):
            text: str = item.text_area.value
            arg = ''
            if item in self.relatives:
                idx = self.relatives.widgets().index(item)
                arg = self.relative_args[idx]
            elif item in self.absolutes:
                idx = self.absolutes.widgets().index(item)
                arg = self.absolute_args[idx]

            try:
                data[arg] = float(text)
            except ValueError:
                if text != '':
                    data[arg] = text

        if self.current is not None:
            data['radius'] = self.current.radius.m
            data['id'] = self.current.id
            data['system'] = self.current.system_id
            data['idx'] = self.current.idx
            data['parent'] = self.current.parent
            data['satellites'] = [i for i in self.current.satellites]
            data['orbit'] = self.current.orbit

        self.has_values = True
        system = Universe.current_planetary()
        data['parent'] = system.parent
        if self.current is None:
            moon = major_moon_by_composition(data)
        else:
            moon = self.current

        if moon.idx is None:
            moon.idx = len([i for i in system.satellites if i.cls == moon.cls])
        if self.current is None:
            if system.add_astro_obj(moon):
                self.current = moon

        if self.current.system_id is None:
            self.current.system_id = system.id

        if self.current not in self.parent.moons:
            self.parent.button_add.enable()
        self.fill()

    def update_value(self, button, data):
        idx = self.absolutes.widgets().index(button)
        attr = self.absolute_args[idx]
        setattr(self.current, attr, data)
        self.fill()

    def show_current(self, satellite):
        self.erase(replace=True)
        self.current = satellite
        self.calculate()

    def enable(self):
        widgets = [self.properties.get_widgets_from_layer(1)[1]]
        widgets += self.properties.get_widgets_from_layer(2)
        for arg in widgets:
            arg.enable()
            arg.modifiable = True

        for obj in self.pie.chart.widgets():
            obj.enable()
        super().enable()

    def disable(self):
        for arg in self.properties:
            arg.disable()
        for obj in self.pie.chart.widgets():
            obj.disable()
        super().disable()

    def erase(self, replace=False):
        super().erase()
        self.current = None
        self.parent.clear()
        self.has_values = False
        for vt in self.properties.get_widgets_from_layer(1):
            vt.value = ''
        for vt in self.properties.get_widgets_from_layer(2):
            vt.value = self.pie.get_default_value(vt.text.lower())

        if not replace:
            self.pie.set_values()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def destroy_button(self):
        destroyed = Universe.current_planetary().remove_astro_obj(self.current)
        if destroyed:
            self.parent.del_button(self.current)
            self.erase()

    def fill(self, tos=None):
        tos = {
            1: {
                'mass': 'kg',
                'radius': 'km',
                'gravity': 'm/s**2',
                'escape_velocity': 'km/s'
            },
            2: {
                'mass': 'Mm',
                'radius': 'Rm',
                'gravity': 'Gm',
                'escape_velocity': 'EVm'
            }
        }
        if self.parent.with_additional_mode:
            tos[3] = {
                'mass': 'Mp',
                'radius': 'Rp',
                'gravity': 'Gp',
                'escape_velocity': 'Ep'
            }
        for element in self.properties.get_widgets_from_layer(1)[1:]:
            element.enable()
        super().fill(tos)
        self.parent.image.fill(COLOR_BOX, self.parent.erase_text_area)

        comp = {}
        for elemento in self.properties.get_widgets_from_layer(2):
            got_attr = self.current.composition.get(elemento.text.lower(), 0)
            attr = str(round(got_attr, 3)) + ' %'
            elemento.value = attr
            elemento.text_area.show()
            comp[elemento.text.lower()] = got_attr
        self.pie.set_values(comp)

    def paste_composition(self, new):
        for elemento in self.properties.get_widgets_from_layer(2):
            elemento.value = str(round(new[elemento.text.lower()], 2)) + ' %'
            elemento.text_area.show()
        # self.has_values = True
        self.pie.set_values(new)


class AddMoonButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Satellite', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.add_button(self.parent.current.current)


class DelMoonButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Satellite', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.current.destroy_button()


class SatelliteButton(ColoredBody):
    enabled = True

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.parent.show_current(self.object_data)
            self.parent.parent.select_one(self)
            self.parent.parent.button_del.enable()


class CopyCompositionButton(Meta):
    enabled = True
    current = None

    last_idx = None

    def __init__(self, parent, x, y, text_center_x):
        super().__init__(parent)
        self.f1 = self.crear_fuente(12)
        self.f2 = self.crear_fuente(12, bold=True)
        self.img_uns = self.crear(self.f1, COLOR_TEXTO)
        self.img_sel = self.crear(self.f2, COLOR_SELECTED)
        self.img_dis = self.crear(self.f1, COLOR_DISABLED)
        self.image = self.img_uns
        self.rect = self.image.get_rect(y=y)
        self.rect.left = x
        self.rocky_planets = {}
        self.current_cycler = None
        self.cyclers = {}
        EventHandler.register(self.manage_rocky_planets, 'RockyPlanet')

        self.text = 'Copy the values from a selected planet'
        self.text_render = self.write3(self.text, self.parent.f3, 130, bg=COLOR_AREA, j=1)
        self.text_rect = self.text_render.get_rect(top=self.rect.bottom, centerx=text_center_x)

    def manage_rocky_planets(self, event):
        planet = event.data['planet']
        id = event.data['system_id']
        if id not in self.rocky_planets:
            self.rocky_planets[id] = []

        if event.data['operation'] == 'add':
            self.rocky_planets[id].append(planet)
            if id not in self.cyclers:
                self.cyclers[id] = cycle(self.rocky_planets[id])
        elif event.data['operation'] == 'remove':
            self.rocky_planets[id].remove(event.data['planet'])
            if not len(self.rocky_planets[id]):
                del self.rocky_planets[id]
                del self.cyclers[id]

        if self.current_cycler is None:
            self.current_cycler = self.cyclers[id]

    @staticmethod
    def crear(fuente, fg):
        render = fuente.render('Copy', True, fg, COLOR_AREA)
        rect = render.get_rect()
        canvas = Surface(rect.inflate(+6, +6).size)
        canvas.fill(fg)
        canvas_rect = canvas.get_rect()
        canvas.fill(COLOR_AREA, [1, 1, canvas_rect.w - 2, canvas_rect.h - 2])
        rect.center = canvas_rect.center
        canvas.blit(render, rect)
        return canvas

    def select(self):
        super().select()
        self.rect = self.image.get_rect(center=self.rect.center)

    def deselect(self):
        super().deselect()
        self.rect = self.image.get_rect(center=self.rect.center)

    def enable(self):
        super().enable()
        self.rect = self.image.get_rect(center=self.rect.center)

    def disable(self):
        super().disable()
        self.rect = self.image.get_rect(center=self.rect.center)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.current = next(self.current_cycler)
            d = {'water ice': 0, 'silicates': 0, 'iron': 0}
            for element in d:
                d[element] = self.current.composition[element]

            attrs = "mass", "radius", "gravity", "escape_velocity", "density", "volume"
            units = 'kg', 'km', 'm/s**2', 'km/s', "g/cm ** 3", "km ** 3"
            for i, attr in enumerate(attrs):
                value = getattr(self.current, attr).to(units[i]).m
                txt = f"{attr[0].upper()}p = {value} * {units[i]}"
                ureg.define(txt)
            self.parent.update_modes(4)
            self.parent.with_additional_mode = True

            self.parent.current.paste_composition(d)
            self.parent.write_name(self.current)

    def on_mouseover(self):
        self.parent.write_button_desc(self)

    def update(self):
        super().update()
        if len(self.rocky_planets) and self.parent.enabled:
            if not self.enabled:
                self.enable()
        elif self.enabled:
            self.disable()

        if Universe.current_galaxy is not None:
            idx = Universe.current_planetary().id
        else:
            idx = self.last_idx

        if idx != self.last_idx:
            self.last_idx = idx
            self.current_cycler = self.cyclers[idx] if idx in self.cyclers else None

    def __repr__(self):
        return f'Copy Composition Button of {self.parent.name}'


class RandomCompositionButton(Meta):
    enabled = True

    def __init__(self, parent, x, y, text_center_x):
        super().__init__(parent)
        self.f1 = self.crear_fuente(12)
        self.f2 = self.crear_fuente(12, bold=True)
        self.img_uns = self.crear(self.f1, COLOR_TEXTO)
        self.img_sel = self.crear(self.f2, COLOR_SELECTED)
        self.img_dis = self.crear(self.f1, COLOR_DISABLED)
        self.image = self.img_uns
        self.rect = self.image.get_rect(y=y)
        self.rect.right = x

        self.text = 'Generate a random composition'
        self.text_render = self.write3(self.text, self.parent.f3, 130, bg=COLOR_AREA, j=1)
        self.text_rect = self.text_render.get_rect(top=self.rect.bottom, centerx=text_center_x)

    @staticmethod
    def crear(fuente, fg):
        render = fuente.render('Random', True, fg, COLOR_AREA)
        rect = render.get_rect()
        canvas = Surface(rect.inflate(+6, +6).size)
        canvas.fill(fg)
        canvas_rect = canvas.get_rect()
        canvas.fill(COLOR_AREA, [1, 1, canvas_rect.w - 2, canvas_rect.h - 2])
        rect.center = canvas_rect.center
        canvas.blit(render, rect)
        return canvas

    def on_mouseover(self):
        self.parent.write_button_desc(self)

    def on_mousebuttondown(self, event):
        if event.origin == self:
            self.parent.clear_name()
            d = {}
            if event.data['button'] == 1 and self.enabled:
                materials = ['silicates', 'water ice', 'iron']
                primary = choice(materials)
                materials.remove(primary)
                value = round(roll(0.0, 100.0), 2)
                new_max = value
                d[primary] = value

                delta = 100 - value
                secondary = choice(materials)
                materials.remove(secondary)
                value = round(roll(0.0, delta), 2)
                new_max += value
                d[secondary] = value

                tertiary = materials[0]
                d[tertiary] = 100 - new_max
                self.parent.current.paste_composition(d)

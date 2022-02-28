from engine.frontend.globales import COLOR_AREA, ANCHO, COLOR_TEXTO, COLOR_DISABLED, COLOR_SELECTED, Group
from engine.backend import EventHandler, Systems, material_densities
from engine.equations.satellite import major_moon_by_composition
from engine.frontend.widgets.values import ValueText
from engine.frontend.widgets.meta import Meta
from ..object_type import ObjectType
from .planet_panel import ShownMass
from .base_panel import BasePanel
from .common import TextButton
from pygame import Surface
from ..pie import PieChart
from itertools import cycle


class SatellitePanel(BasePanel):
    curr_x = 0
    curr_y = 0

    mass_number = None
    last_idx = None

    def __init__(self, parent):
        super().__init__('Satellite', parent, modes=3)
        self.current = SatelliteType(self)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 132, 200])
        self.area_satellites = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 300, 200))
        self.curr_x = self.area_satellites.x + 3
        self.curr_y = self.area_satellites.y + 21
        f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(13, underline=True)
        r = self.write('Composition', f1, COLOR_AREA, topleft=(18, 420))
        self.write('Satellites', f2, COLOR_AREA, x=self.area_satellites.x + 3, y=self.area_satellites.y)
        self.properties = Group()
        self.mass_number = ShownMass(self)
        self.button_add = AddMoonButton(self, ANCHO - 13, 398)
        self.button_del = DelMoonButton(self, ANCHO - 13, 416)
        self.copy_button = CopyCompositionButton(self, r.centerx, r.bottom + 6)
        txt = 'Copy the values from a selected planet'
        self.f3 = self.crear_fuente(11)
        self.txt_a = self.write2(txt, self.f3, 130, COLOR_AREA, centerx=r.centerx, y=self.area_satellites.y + 50, j=1)
        self.properties.add(self.button_add, self.button_del, self.copy_button, self.mass_number)
        self.satellites = Group()
        self.moons = []
        EventHandler.register(self.load_satellites, 'LoadData')
        EventHandler.register(self.save_satellites, 'Save')
        EventHandler.register(self.name_current, 'NameObject')

    def load_satellites(self, event):
        if 'Satellites' in event.data and len(event.data['Satellites']):
            self.enable()
            for idx, id in enumerate(event.data['Satellites']):
                satellite_data = event.data['Satellites'][id]
                satellite_data['id'] = id
                moon = major_moon_by_composition(satellite_data)
                moon.idx = len([i for i in Systems.get_current().satellites if i.cls == moon.cls])
                system = Systems.get_system_by_id(satellite_data['system'])
                if system is not None and system.add_astro_obj(moon):
                    self.add_button(moon)

    def save_satellites(self, event):
        data = {}
        for moon_button in self.satellites.widgets():
            moon = moon_button.object_data
            moon_data = {
                'name': moon.name,
                'radius': moon.radius.m,
                'composition': moon.composition,
                'system': moon.system_id
            }
            data[moon.id] = moon_data
            EventHandler.trigger(event.tipo + 'Data', 'Planet', {"Satellites": data})

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.satellites.get_widgets_from_layer(Systems.get_current().id):
            bt.move(x, y)
            if not self.area_satellites.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def show_current(self, idx):
        for button in self.satellites.widgets():
            button.hide()
        for button in self.satellites.get_widgets_from_layer(idx):
            button.show()
        self.sort_buttons()

    def add_button(self, moon):
        button = SatelliteButton(self.current, moon, self.curr_x, self.curr_y)
        if moon.system_id is not None:
            layer_number = moon.system_id
        else:
            layer_number = Systems.get_current().id
            moon.system_id = layer_number

        self.moons.append(moon)
        self.satellites.add(button, layer=layer_number)
        self.properties.add(button)
        if self.is_visible:
            self.sort_buttons()
            self.current.erase()
        self.button_add.disable()

    def del_button(self, satellite):
        button = [i for i in self.satellites.widgets() if i.object_data == satellite][0]
        self.moons.remove(satellite)
        self.satellites.remove(button)
        self.sort_buttons()
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
        if self.mass_number is None:
            self.properties.add()
        for pr in self.properties.widgets():
            pr.show()

    def hide(self):
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
        idx = Systems.get_current_id(self)

        if idx != self.last_idx:
            self.show_current(idx)
            self.last_idx = idx

    def write_name(self, planet):
        self.image.fill(COLOR_AREA, [0, 498, 130, 14])
        text = f'[{str(planet)}]'
        self.write(text, self.f3, COLOR_AREA, top=self.txt_a.bottom, centerx=self.txt_a.centerx)


class SatelliteType(ObjectType):

    def __init__(self, parent):
        rel_props = ['Radius', 'Mass', 'Surface Gravity', 'Escape velocity']
        rel_args = ['radius', 'mass', 'gravity', 'escape_velocity']
        abs_args = ['density', 'volume', 'surface', 'circumference', 'clase']
        abs_props = ['Density', 'Volume', 'Surface Area', 'Circumference', 'Clase']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 0)
        self.show_layers.append(3)

        for item in self.relatives.widgets() + self.absolutes.widgets():
            item.rect.y += 50
            item.text_area.rect.y += 50

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
                    data['composition'][material.text.lower()] = float(text)

        for item in self.properties.get_widgets_from_layer(1):
            text = item.text_area.value
            try:
                data[item.text.lower()] = float(text)
            except ValueError:
                data[item.text.lower()] = text

        if self.current is not None:
            data['radius'] = self.current.radius.m
            data['id'] = self.current.id
            data['system'] = self.current.system_id
            data['idx'] = self.current.idx
            data['parent'] = self.current.parent
            data['satellites'] = [i for i in self.current.satellites]
            data['orbit'] = self.current.orbit

        self.has_values = True

        moon = major_moon_by_composition(data)
        if moon.idx is None:
            moon.idx = len([i for i in Systems.get_current().satellites if i.cls == moon.cls])
        if self.current is None:
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon
        else:
            Systems.get_current().remove_astro_obj(self.current)
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon

        if self.current.system_id is None:
            self.current.system_id = Systems.get_current().id

        if self.current not in self.parent.moons:
            self.parent.button_add.enable()
        self.fill()

    def show_current(self, satellite):
        self.erase(replace=True)
        self.current = satellite
        self.calculate()

    def enable(self):
        widgets = self.properties.get_widgets_from_layer(1)[0:1]
        widgets += self.properties.get_widgets_from_layer(2)
        for arg in widgets:
            arg.enable()

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
        destroyed = Systems.get_current().remove_astro_obj(self.current)
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
        for element in self.properties.get_widgets_from_layer(1)[1:]:
            element.enable()
        super().fill(tos)

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
        self.has_values = True
        self.pie.set_values(new)


class AddMoonButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Satellite', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.add_button(self.parent.current.current)


class DelMoonButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Satellite', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.destroy_button()


class SatelliteButton(Meta):
    enabled = True

    def __init__(self, parent, satellite, x, y):
        super().__init__(parent)
        self.object_data = satellite
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.img_uns = self.f1.render(str(satellite), True, satellite.color, COLOR_AREA)
        self.img_sel = self.f2.render(str(satellite), True, satellite.color, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.show_current(self.object_data)
            self.parent.parent.select_one(self)
            self.parent.parent.button_del.enable()

    def move(self, x, y):
        self.rect.topleft = x, y


class CopyCompositionButton(Meta):
    enabled = True
    current = None

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = self.crear_fuente(12)
        self.f2 = self.crear_fuente(12, bold=True)
        self.img_uns = self.crear(self.f1, COLOR_TEXTO)
        self.img_sel = self.crear(self.f2, COLOR_SELECTED)
        self.img_dis = self.crear(self.f1, COLOR_DISABLED)
        self.image = self.img_uns
        self.rect = self.image.get_rect(y=y)
        self.rect.centerx = x
        self.rocky_planets = []
        self.rocky_cycler = cycle(self.rocky_planets)
        EventHandler.register(self.manage_rocky_planets, 'RockyPlanet')

    def manage_rocky_planets(self, event):
        if event.data['operation'] == 'add':
            self.rocky_planets.append(event.data['planet'])
            if len(self.rocky_planets) == 1:
                self.current = next(self.rocky_cycler)
        elif event.data['operation'] == 'remove':
            self.rocky_planets.remove(event.data['planet'])

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
        if event.button == 1 and self.enabled:
            d = {'water ice': 0, 'silicates': 0, 'iron': 0}
            for element in d:
                d[element] = self.current.composition[element]
            self.parent.current.paste_composition(d)
            self.parent.write_name(self.current)
            self.current = next(self.rocky_cycler)

    def update(self):
        super().update()
        if len(self.rocky_planets) and self.parent.enabled:
            if not self.enabled:
                self.enable()
        elif self.enabled:
            self.disable()

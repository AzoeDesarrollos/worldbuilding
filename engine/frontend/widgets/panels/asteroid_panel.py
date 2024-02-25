from engine.frontend.widgets.panels.satellite_panel import CopyCompositionButton, RandomCompositionButton
from engine.frontend.globales import COLOR_AREA, ALTO, ANCHO, COLOR_TEXTO, COLOR_BOX, Group
from engine.backend import EventHandler, Systems, material_densities, q
from engine.equations.satellite import minor_moon_by_composition
from engine.frontend.widgets.basewidget import BaseWidget
from .common import TextButton, ColoredBody
from engine.equations.space import Universe
from .planet_panel import ShownMass
from .base_panel import BasePanel
from ..values import ValueText
from ..pie import PieChart
from pygame import Rect


class AsteroidPanel(BasePanel):
    last_idx = None

    def __init__(self, parent):
        super().__init__('Asteroid', parent)
        self.properties = Group()
        self.current = AsteroidType(self)
        f = self.crear_fuente(16, underline=True)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 132, 178])
        ro = self.write('Composition', f, COLOR_AREA, topleft=(18, 420))
        self.area_buttons = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 300, 178))
        self.write('Asteroids', f, COLOR_AREA, topleft=(self.area_buttons.x+2, self.area_buttons.y))
        self.area_type = Rect(32, 32, ANCHO, ALTO - (self.area_buttons.h + 200))
        text = 'Create your asteroids here.\n\n'
        text += 'Input its three axes first, and then select its composition below.\n\n'
        text += ('For a Tri-Axial Ellipsoid: A > B > C\n\n'
                 'For a Obleate Spheroid: A = B > C\n\n'
                 'For a Prolate Spheroid: A = B < C\n\n')
        text += 'You can copy its compostition from a given planet or set it randomly.\n\n'
        text += 'You can also set the percentages manually.'
        self.erase_text_area = self.write2(text, self.crear_fuente(14), fg=COLOR_AREA, width=300, x=250, y=50, j=1)
        self.curr_x = self.area_buttons.x + 3
        self.curr_y = self.area_buttons.y + 21

        self.button_add = AddAsteroidButton(self, ANCHO - 13, 398)
        self.button_del = DelAsteroidButton(self, ANCHO - 13, 416)
        self.f3 = self.crear_fuente(11)

        self.copy_button = CopyCompositionButton(self, ro.left, ro.bottom + 6, ro.centerx)
        self.random_button = RandomCompositionButton(self, ro.right, ro.bottom + 6, ro.centerx)

        self.name_rect = Rect(0, 0, r.w, self.f3.get_height())
        self.name_rect.centerx = r.centerx
        self.name_rect.top = self.copy_button.text_rect.bottom

        self.mass_number = ShownMass(self)
        self.properties.add(self.current, self.mass_number, self.button_add,
                            self.random_button, self.button_del, self.copy_button, layer=1)
        self.asteroids = Group()
        self.moons = []
        EventHandler.register(self.save_satellites, 'Save')
        EventHandler.register(self.name_current, 'NameObject')
        EventHandler.register(self.load_satellites, 'LoadData')

    def load_satellites(self, event):
        for id in event.data['Asteroids']:
            asteorid_data = event.data['Asteroids'][id]
            moon = minor_moon_by_composition(asteorid_data)
            moon.idx = len([i for i in Systems.get_current().planets if i.clase == moon.clase])
            self.asteroids.add(moon)
            Universe.add_astro_obj(moon)

    def load_data(self):
        self.enable()
        for moon in self.asteroids.widgets():
            system = Systems.get_system_by_id(moon.system_id)
            if system is not None and system.add_astro_obj(moon):
                self.add_button(moon)

    def save_satellites(self, event):
        data = {}
        for moon_button in [i for i in self.asteroids.widgets() if not i.object_data.flagged]:
            moon = moon_button.object_data
            moon_data = {
                'name': moon.name,
                'a axis': moon.a_axis.m,
                'b axis': moon.b_axis.m,
                'c axis': moon.c_axis.m,
                'composition': moon.composition,
                'system': moon.system_id,
                'idx': moon.idx
            }
            data[moon.id] = moon_data
            EventHandler.trigger(event.tipo + 'Data', 'Asteroid', {"Asteroids": data})

    def name_current(self, event):
        if event.data['object'] in self.moons:
            moon = event.data['object']
            moon.set_name(event.data['name'])

    def add_button(self, asteroid=None):
        if asteroid is None:
            asteroid = self.current.current
        button = AsteroidButton(self.current, asteroid, str(asteroid), self.curr_x, self.curr_y)
        if self.current.current.system_id is not None:
            layer_number = self.current.current.system_id
        else:
            layer_number = Systems.get_current().id
            self.current.current.system_id = layer_number
        self.moons.append(self.current.current)
        self.asteroids.add(button, layer=layer_number)
        self.properties.add(button, layer=layer_number)
        if self.is_visible:
            asteroids = self.asteroids.get_widgets_from_layer(Systems.get_current().id)
            self.sort_buttons(asteroids, x=self.curr_x, y=self.curr_y)
        self.current.erase()
        self.button_add.disable()

    def del_button(self, satellite):
        button = [i for i in self.asteroids.widgets() if i.object_data == satellite][0]
        self.moons.remove(satellite)
        self.asteroids.remove(button)
        button.hide()
        self.sort_buttons(self.asteroids.get_widgets_from_layer(Systems.get_current().id))
        self.properties.remove(button)
        self.button_del.disable()

    def show_current(self, idx):
        for button in self.asteroids.widgets():
            button.hide()
        for button in self.asteroids.get_widgets_from_layer(idx):
            button.show()
        self.sort_buttons(self.asteroids.get_widgets_from_layer(Systems.get_current().id))

    def select_one(self, btn):
        for button in self.asteroids.widgets():
            button.deselect()
        btn.select()

    def enable(self):
        super().enable()
        self.current.enable()

    def show(self):
        super().show()
        self.load_data()
        for pr in self.properties.get_widgets_from_layer(1):
            pr.show()
        for pr in self.properties.get_widgets_from_layer(Systems.get_current_id(self)):
            pr.show()

    def hide(self):
        super().hide()
        self.is_visible = False
        for pr in self.properties.widgets():
            pr.hide()

        flag = Systems.get_current() is not None
        flag = not len(Systems.get_current().asteroids + Systems.get_current().satellites) if flag else False
        self.parent.set_skippable('Planetary Orbit', flag)

    def update(self):
        idx = Systems.get_current_id(self)
        if idx != self.last_idx:
            self.image.fill(COLOR_AREA, [0, 498, 130, 14])
            self.current.pie.set_values()
            self.show_current(idx)
            self.last_idx = idx

    def clear(self):
        self.image.fill(COLOR_AREA, [0, 498, 130, 14])
        self.button_add.disable()
        self.button_del.disable()
        for button in self.asteroids.widgets():
            button.deselect()

    def write_name(self, planet):
        r = self.image.fill(COLOR_AREA, [0, 498, 130, 14])
        text = f'[{str(planet)}]'
        self.write(text, self.f3, COLOR_AREA, top=self.name_rect.y, centerx=r.centerx)

    def clear_name(self):
        self.image.fill(COLOR_AREA, [0, 498, 130, 14])

    def write_button_desc(self, button):
        self.image.blit(button.text_render, button.text_rect)


class AsteroidType(BaseWidget):
    current = None
    has_values = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = Group()

        EventHandler.register(self.clear, 'ClearData')
        self.relative_args = ['mass', 'density', 'volume']

        names = sorted(material_densities.keys())
        d = {names[0]: 33, names[1]: 33, names[2]: 34}
        self.pie = PieChart(self, 200, 500, 65, d)
        for obj in self.pie.chart.widgets():
            self.properties.add(obj, layer=5)

        names = ["Mass", "Density",  "Volume", 'Axial tilt', 'Spin',
                 'Rotation Rate', "A Axis", "B Axis", "C Axis", "Shape"]
        for i, prop in enumerate(names, start=0):
            vt = ValueText(self, prop, 50, 40 + i * 36, COLOR_TEXTO, COLOR_BOX)
            if i in (0, 1, 2):
                layer = 2
            elif i in (6, 7, 8):
                layer = 3
                vt.modifiable = True
            elif i in (3, 4, 5):
                layer = 6
            else:
                # "Shape" is not directly modifiable.
                layer = 3

            self.properties.add(vt, layer=layer)

        for i, name in enumerate(sorted(material_densities)):
            a = ValueText(self, name.capitalize(), 3, 500 + 30 + i * 21, bg=COLOR_AREA)
            a.text_area.value = str(d[name]) + ' %'
            self.properties.add(a, layer=4)
            a.modifiable = True

        self.pie.hide()

    def calculate(self):
        data = {'composition': None}
        if self.current is None:
            data['composition'] = {}
        else:
            data['composition'] = self.current.composition

        for item in self.properties.get_widgets_from_layer(3):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        if not len(data['composition']):
            for material in self.properties.get_widgets_from_layer(4):
                if material.text_area.value:  # not empty
                    data['composition'][material.text.lower()] = float(material.text_area.value.strip(' %'))

        if self.current is not None:
            data['a axis'] = self.current.a_axis.m
            data['b axis'] = self.current.b_axis.m
            data['c axis'] = self.current.c_axis.m
            data['id'] = self.current.id
            data['system'] = self.current.system_id
            data['idx'] = self.current.idx

        if self.current is None:
            moon = minor_moon_by_composition(data)
        else:
            moon = self.current

        if self.current is None:
            if Systems.get_current().add_astro_obj(moon):
                Universe.add_astro_obj(moon)
                self.current = moon
                self.parent.button_add.enable()
        elif moon != self.current:
            Systems.get_current().remove_astro_obj(self.current)
            Universe.remove_astro_obj(self.current)
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon

        if self.current.system_id is None:
            self.current.system_id = Systems.get_current().id
        if self.current not in self.parent.moons:
            self.parent.button_add.enable()
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self, replace=False):
        self.current = None
        self.has_values = False
        self.parent.clear()
        for vt in self.properties.get_widgets_from_layer(2) + self.properties.get_widgets_from_layer(3):
            vt.text_area.set_value('')
            vt.disable()
        for vt in self.properties.get_widgets_from_layer(4):
            vt.value = self.pie.get_default_value(vt.text.lower())

        if not replace:
            self.pie.set_values()
        self.enable()

    def enable(self):
        widgets = self.properties.get_widgets_from_layer(3)[:3]
        widgets += self.properties.get_widgets_from_layer(4)
        for arg in widgets:
            arg.enable()
        for obj in self.pie.chart.widgets():
            obj.enable()
        super().enable()

    def disable(self):
        for arg in self.properties.widgets():
            arg.disable()
        for obj in self.pie.chart.widgets():
            obj.disable()
        super().disable()

    def destroy_button(self):
        destroyed = Systems.get_current().remove_astro_obj(self.current)
        if destroyed:
            self.parent.del_button(self.current)
            self.erase()

    def show_current(self, asteroid):
        self.erase(replace=True)
        self.current = asteroid
        self.calculate()

    def fill(self):
        tos = {
            1: {
                'Mass': 'Me',
                'Density': 'De',
                'Volume': 'Ve'
            }
        }
        self.parent.image.fill(COLOR_BOX, self.parent.erase_text_area)
        elementos = self.properties.get_widgets_from_layer(2)
        for elemento in elementos:
            elemento.enable()
            idx = elementos.index(elemento)
            attr = self.relative_args[idx]

            if self.parent.mode == 0:
                got_attr = getattr(self.current, attr)
            else:
                got_attr = getattr(self.current, attr).to(tos[self.parent.mode][elemento.text.capitalize()])
            attr = q(str(got_attr.m), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            if elemento.text_area.unit == 'earth_mass':
                elemento.do_round = False
            elemento.text_area.show()

        for elemento in self.properties.get_widgets_from_layer(3):
            elemento.enable()
            name = elemento.text
            if ' ' in elemento.text:
                name = name.replace(' ', '_')
            got_attr = getattr(self.current, name.lower())
            attr = q(str(round(got_attr.m, 3)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            elemento.text_area.show()

        comp = {}
        for elemento in self.properties.get_widgets_from_layer(4):
            got_attr = self.current.composition.get(elemento.text.lower(), 0)
            attr = str(round(got_attr, 3)) + ' %'
            elemento.value = attr
            elemento.text_area.show()
            comp[elemento.text.lower()] = got_attr
        self.pie.set_values(comp)

        self.has_values = True

    def paste_composition(self, new):
        for elemento in self.properties.get_widgets_from_layer(4):
            elemento.value = str(round(new[elemento.text.lower()], 2)) + ' %'
            elemento.text_area.show()
        self.has_values = True
        self.pie.set_values(new)

    def show(self):
        for p in self.properties.widgets():
            p.show()

    def hide(self):
        for p in self.properties.widgets():
            p.hide()


class AddAsteroidButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Asteroid', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.add_button()


class DelAsteroidButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Asteroid', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.current.destroy_button()


class AsteroidButton(ColoredBody):
    enabled = True

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.parent.show_current(self.object_data)
            self.parent.parent.select_one(self)
            self.parent.parent.button_del.enable()

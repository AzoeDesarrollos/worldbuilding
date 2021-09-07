from engine.frontend.globales import COLOR_AREA, WidgetGroup, COLOR_TEXTO, COLOR_BOX, ANCHO
from engine.equations.satellite import minor_moon_by_composition
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets.meta import Meta
from engine import material_densities, q
from .planet_panel import ShownMass
from .base_panel import BasePanel
from ..values import ValueText
from .common import TextButton


class AsteroidPanel(BasePanel):
    curr_x = 0
    curr_y = 0
    mass_number = None
    loaded_data = None
    last_idx = None

    def __init__(self, parent):
        super().__init__('Asteroid', parent)
        self.properties = WidgetGroup()
        self.current = AsteroidType(self)
        f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(13, underline=True)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 132, 200])
        self.write('Composition', f1, COLOR_AREA, topleft=(0, 420))
        self.area_asteroids = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 300, 200))
        self.write('Asteroids', f2, COLOR_AREA, x=self.area_asteroids.x + 3, y=self.area_asteroids.y)
        self.curr_x = self.area_asteroids.x + 3
        self.curr_y = self.area_asteroids.y + 21
        self.properties.add(self.current)
        self.button_add = AddAsteroidButton(self, ANCHO - 13, 398)
        self.button_del = DelAsteroidButton(self, ANCHO - 13, 416)
        self.properties.add(self.button_add, self.button_del)
        self.asteroids = WidgetGroup()
        self.moons = []
        EventHandler.register(self.load_satellites, 'LoadData')
        EventHandler.register(self.save_satellites, 'Save')
        EventHandler.register(self.name_current, 'NameObject')

    def name_current(self, event):
        if event.data['object'] in self.moons:
            moon = event.data['object']
            moon.name = event.data['name']
            moon.has_name = True

    def load_satellites(self, event):
        if 'Asteroids' in event.data and len(event.data['Asteroids']):
            self.loaded_data = event.data['Asteroids']

    def show_loaded(self):
        if self.loaded_data is not None:
            for id in self.loaded_data:
                satellite_data = self.loaded_data[id]
                satellite_data['id'] = id
                moon = minor_moon_by_composition(satellite_data)
                system = Systems.get_system_by_id(satellite_data['system'])
                if system.add_astro_obj(moon):
                    self.current.current = moon
                    self.add_button()
            self.loaded_data.clear()

    def save_satellites(self, event):
        data = {}
        for moon_button in self.asteroids.widgets():
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

    def add_button(self):
        button = AsteroidButton(self.current, self.current.current, self.curr_x, self.curr_y)
        if self.current.current.system_id is not None:
            layer_number = Systems.get_system_idx_by_id(self.current.current.system_id)
        else:
            layer_number = Systems.get_current_idx()
            self.current.current.system_id = Systems.get_current().id
        self.moons.append(self.current.current)
        self.asteroids.add(button, layer=layer_number)
        self.properties.add(button)
        self.sort_buttons()
        self.current.erase()
        self.button_add.disable()

    def del_button(self, satellite):
        button = [i for i in self.asteroids.widgets() if i.object_data == satellite][0]
        self.moons.remove(satellite)
        self.asteroids.remove(button)
        self.sort_buttons()
        self.properties.remove(button)
        self.button_del.disable()

    def show_current(self, idx):
        for button in self.asteroids.widgets():
            button.hide()
        for button in self.asteroids.get_widgets_from_layer(idx):
            button.show()
        self.sort_buttons()

    def select_one(self, btn):
        for button in self.asteroids.widgets():
            button.deselect()
        btn.select()

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.asteroids.get_widgets_from_layer(Systems.get_current_idx()):
            bt.move(x, y)
            if not self.area_asteroids.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def show(self):
        super().show()
        self.show_loaded()
        self.is_visible = True
        if self.mass_number is None:
            self.properties.add(ShownMass(self))
        for pr in self.properties.widgets():
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
        idx = Systems.get_current_idx()
        if idx != self.last_idx:
            self.show_current(idx)
            self.last_idx = idx

    def next_idx(self, form):
        types = 'Obleate', 'Tri-Axial', 'Prolate'
        type_a = len([moon.idx for moon in self.moons if moon.cls == types[0]])
        type_b = len([moon.idx for moon in self.moons if moon.cls == types[1]])
        type_c = len([moon.idx for moon in self.moons if moon.cls == types[2]])
        if form == types[0]:
            return type_a + 1
        elif form == types[1]:
            return type_b + 1
        elif form == types[2]:
            return type_c + 1


class AsteroidType(BaseWidget):
    current = None
    has_values = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.create()
        EventHandler.register(self.clear, 'ClearData')
        self.relative_args = ['density', 'mass', 'volume']

    def create(self):
        for i, prop in enumerate(["Density", "Mass", "Volume"]):
            vt = ValueText(self, prop, 50, 64 + i * 48, COLOR_TEXTO, COLOR_BOX)
            self.properties.add(vt, layer=2)

        for i, prop in enumerate(["A Axis", "B Axis", "C Axis", "Shape"], start=4):
            vt = ValueText(self, prop, 50, 52 + i * 40, COLOR_TEXTO, COLOR_BOX)
            self.properties.add(vt, layer=3)
            vt.modifiable = True

        for i, name in enumerate(sorted(material_densities)):
            a = ValueText(self, name.capitalize(), 3, 420 + 21 + i * 21, bg=COLOR_AREA)
            self.properties.add(a, layer=4)
            a.modifiable = True

    def calculate(self):
        data = {'composition': None}
        if self.current is None:
            data['composition'] = {}
        else:
            data['composition'] = self.current.composition

        for item in self.properties.get_widgets_from_layer(2):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        for item in self.properties.get_widgets_from_layer(3):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        for material in self.properties.get_widgets_from_layer(4):
            if material.text_area.value:  # not empty
                data['composition'][material.text.lower()] = float(material.text_area.value)

        if self.current is not None:
            data['a axis'] = self.current.a_axis.m
            data['b axis'] = self.current.b_axis.m
            data['c axis'] = self.current.c_axis.m
            data['id'] = self.current.id
            data['system'] = self.current.system_id

        moon = minor_moon_by_composition(data)
        moon.idx = self.parent.next_idx(moon.cls)
        if self.current is None:
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon
                self.parent.button_add.enable()
        else:
            Systems.get_current().remove_astro_obj(self.current)
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon

        if self.current.system_id is None:
            self.current.system_id = Systems.get_current().id

        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self):
        self.current = None
        self.has_values = False
        for vt in self.properties:
            vt.value = ''

    def destroy_button(self):
        destroyed = Systems.get_current().remove_astro_obj(self.current)
        if destroyed:
            self.parent.del_button(self.current)
            self.erase()

    def show_current(self, asteroid):
        self.erase()
        self.current = asteroid
        self.calculate()

    def fill(self):
        tos = {
            'Mass': 'Me',
            'Density': 'De',
            'Volume': 'Ve'
        }

        for elemento in self.properties.get_widgets_from_layer(2):
            idx = self.properties.widgets().index(elemento)
            attr = self.relative_args[idx]

            if not self.parent.relative_mode:
                got_attr = getattr(self.current, attr)
            else:
                got_attr = getattr(self.current, attr).to(tos[elemento.text.capitalize()])
            attr = q(str(got_attr.m), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            if elemento.text_area.unit == 'earth_mass':
                elemento.do_round = False
            elemento.text_area.show()

        for elemento in self.properties.get_widgets_from_layer(3):
            name = elemento.text
            if ' ' in elemento.text:
                name = name.replace(' ', '_')
            got_attr = getattr(self.current, name.lower())
            attr = q(str(round(got_attr.m, 3)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            elemento.text_area.show()

        for elemento in self.properties.get_widgets_from_layer(4):
            got_attr = self.current.composition.get(elemento.text.lower(), 0)
            attr = str(round(got_attr, 3)) + ' %'
            elemento.value = attr
            elemento.text_area.show()

        self.has_values = True

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
        if event.button == 1 and self.enabled:
            self.parent.add_button()


class DelAsteroidButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Asteroid', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.destroy_button()


class AsteroidButton(Meta):
    enabled = True

    def __init__(self, parent, satellite, x, y):
        super().__init__(parent)
        self.object_data = satellite
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        if satellite.has_name:
            name = satellite.name
        else:
            name = "{} #{}".format(satellite.cls, satellite.idx)
        self.img_uns = self.f1.render(name, True, satellite.color, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, satellite.color, COLOR_AREA)
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

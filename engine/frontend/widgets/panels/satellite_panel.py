from engine.frontend.globales import WidgetGroup, COLOR_AREA, ANCHO
from engine.equations.satellite import major_moon_by_composition
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets.values import ValueText
from engine.frontend.widgets.meta import Meta
from engine import material_densities
from ..object_type import ObjectType
from .planet_panel import ShownMass
from .base_panel import BasePanel
from .common import TextButton


class SatellitePanel(BasePanel):
    curr_x = 0
    curr_y = 0

    mass_number = None
    loaded_data = None

    def __init__(self, parent):
        super().__init__('Satellite', parent)
        self.current = SatelliteType(self)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 32, 200])
        self.area_satellites = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 400, 200))
        self.curr_x = self.area_satellites.x + 3
        self.curr_y = self.area_satellites.y + 21
        f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(13, underline=True)
        self.write('Composition', f1, COLOR_AREA, topleft=(0, 420))
        self.write('Satellites', f2, COLOR_AREA, x=self.area_satellites.x + 3, y=self.area_satellites.y)
        self.properties = WidgetGroup()

        self.button_add = AddMoonButton(self, ANCHO - 13, 398)
        self.button_del = DelMoonButton(self, ANCHO - 13, 416)
        self.properties.add(self.button_add, self.button_del)
        self.satellites = WidgetGroup()
        EventHandler.register(self.load_satellites, 'LoadData')
        EventHandler.register(self.save_satellites, 'Save')

    def load_satellites(self, event):
        if 'Satellites' in event.data and len(event.data['Satellites']):
            self.loaded_data = event.data['Satellites']

    def show_loaded(self):
        if self.loaded_data is not None:
            for satellite_data in self.loaded_data:
                moon = major_moon_by_composition(satellite_data)
                if Systems.get_current().add_astro_obj(moon):
                    self.current.current = moon
                    self.add_button()
            self.loaded_data.clear()

    def save_satellites(self, event):
        data = []
        for moon_button in self.satellites.widgets():
            moon = moon_button.object_data
            moon_data = {
                'name': moon.name,
                'radius': moon.radius.m,
                'composition': moon.composition,
                'id': moon.id
            }
            data.append(moon_data)
            EventHandler.trigger(event.tipo + 'Data', 'Planet', {"Satellites": data})

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.satellites.get_widgets_from_layer(Systems.get_current_idx()):
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

    def add_button(self):
        button = SatelliteButton(self.current, self.current.current, self.curr_x, self.curr_y)
        self.satellites.add(button, layer=Systems.get_current_idx())
        self.properties.add(button)
        self.sort_buttons()
        self.current.erase()
        self.button_add.disable()

    def del_button(self, satellite):
        button = [i for i in self.satellites.widgets() if i.object_data == satellite][0]
        self.satellites.remove(button)
        self.sort_buttons()
        self.properties.remove(button)
        self.button_del.disable()

    def select_one(self, btn):
        for button in self.satellites.widgets():
            button.deselect()
        btn.select()

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
        for pr in self.properties.widgets():
            pr.hide()


class SatelliteType(ObjectType):

    def __init__(self, parent):
        rel_props = ['Mass', 'Radius', 'Surface Gravity', 'Escape velocity']
        rel_args = ['mass', 'radius', 'gravity', 'escape_velocity']
        abs_args = ['density', 'volume', 'surface', 'circumference', 'clase']
        abs_props = ['Density', 'Volume', 'Surface Area', 'Circumference', 'Clase']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 1)

        for item in self.relatives:
            item.rect.y += 16
            item.text_area.rect.y += 16

        for i, name in enumerate(sorted(material_densities)):
            a = ValueText(self, name.capitalize(), 3, 420 + 21 + i * 21, bg=COLOR_AREA)
            self.properties.add(a, layer=7)
            a.modifiable = True

    def calculate(self):
        data = {'composition': None}
        if self.current is None:
            data['composition'] = {}
        else:
            data['composition'] = self.current.composition

        for material in self.properties.get_sprites_from_layer(7):
            if material.text_area.value:  # not empty
                text = material.text_area.value.strip(' %')
                data['composition'][material.text.lower()] = float(text)
        for item in self.properties.get_widgets_from_layer(1):
            text = item.text_area.value
            if type(text) is not str:
                data[item.text.lower()] = float(text)
            elif text != '' and not text.isalpha():
                data[item.text.lower()] = float(text)
            else:
                data[item.text.lower()] = text

        if self.current is not None:
            data['radius'] = self.current.radius.m

        self.has_values = True

        moon = major_moon_by_composition(data)
        if self.current is None:
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon
        else:
            Systems.get_current().remove_astro_obj(self.current)
            if Systems.get_current().add_astro_obj(moon):
                self.current = moon
        self.parent.button_add.enable()
        self.fill()

    def show_current(self, satellite):
        self.erase()
        self.current = satellite
        self.calculate()

    def erase(self):
        super().erase()
        for vt in self.properties:
            vt.value = ''
        self.current = None

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
            'mass': 'kg',
            'radius': 'km',
            'gravity': 'm/s**2',
            'escape_velocity': 'km/s'
        }
        super().fill(tos)

        for elemento in self.properties.get_widgets_from_layer(7):
            got_attr = self.current.composition.get(elemento.text.lower(), 0)
            attr = str(round(got_attr, 3)) + ' %'
            elemento.value = attr
            elemento.text_area.show()


class AddMoonButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Satellite', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.add_button()


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
        self.img_uns = self.f1.render(satellite.cls, True, satellite.color, COLOR_AREA)
        self.img_sel = self.f2.render(satellite.cls, True, satellite.color, COLOR_AREA)
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

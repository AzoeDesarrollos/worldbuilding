from engine.frontend.globales import COLOR_AREA, WidgetGroup, COLOR_TEXTO, COLOR_BOX
from engine.equations.satellite import minor_moon_by_composition
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine import material_densities, q
from .common import TextButton, Meta
from .base_panel import BasePanel
from ..values import ValueText


class AsteroidPanel(BasePanel):
    curr_x = 0
    curr_y = 0

    def __init__(self, parent):
        super().__init__('Asteroid', parent)
        self.properties = WidgetGroup()
        self.current = AsteroidType(self)
        f1 = self.crear_fuente(16, underline=True)
        f2 = self.crear_fuente(13, underline=True)
        r = self.image.fill(COLOR_AREA, [0, 420, (self.rect.w // 4) + 32, 200])
        self.write('Composition', f1, COLOR_AREA, topleft=(0, 420))
        self.area_asteroids = self.image.fill(COLOR_AREA, (r.right + 10, r.y, 400, 200))
        self.write('Asteroids', f2, COLOR_AREA, x=self.area_asteroids.x + 3, y=self.area_asteroids.y)
        self.curr_x = self.area_asteroids.x + 3
        self.curr_y = self.area_asteroids.y + 21
        self.properties.add(self.current)
        self.button = AddAsteroidButton(self, 476, 416)
        self.properties.add(self.button)
        self.asteroids = WidgetGroup()

    def add_button(self):
        button = AsteroidButton(self.current, self.current.current, self.curr_x, self.curr_y)
        self.asteroids.add(button, layer=Systems.get_current_idx())
        self.properties.add(button)
        self.sort_buttons()
        self.current.erase()

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
        self.is_visible = True
        for pr in self.properties.widgets():
            pr.show()

    def hide(self):
        super().hide()
        self.is_visible = False
        for pr in self.properties.widgets():
            pr.hide()
        if not len(Systems.get_current().asteroids + Systems.get_current().satellites):
            self.parent.set_skippable('Planetary Orbit')


class AsteroidType(BaseWidget):
    current = None
    has_values = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.create()
        EventHandler.register(self.clear, 'ClearData')

    def create(self):
        for i, prop in enumerate(["Density", "Mass", "Volume"]):
            vt = ValueText(self, prop, 50, 64 + i * 48, COLOR_TEXTO, COLOR_BOX)
            self.properties.add(vt, layer=2)

        for i, prop in enumerate(["A Axis", "B Axis", "C Axis", "Shape"], start=4):
            vt = ValueText(self, prop, 50, 52 + i * 40, COLOR_TEXTO, COLOR_BOX)
            self.properties.add(vt, layer=3)

        for i, name in enumerate(sorted(material_densities)):
            a = ValueText(self, name.capitalize(), 3, 420 + 21 + i * 21, bg=COLOR_AREA)
            self.properties.add(a, layer=4)

    def calculate(self):
        data = {}
        for item in self.properties.get_widgets_from_layer(2):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        for item in self.properties.get_widgets_from_layer(3):
            if item.text_area.value:
                data[item.text.lower()] = float(item.text_area.value)

        data['composition'] = {}
        for material in self.properties.get_widgets_from_layer(4):
            if material.text_area.value:  # not empty
                data['composition'][material.text.lower()] = float(material.text_area.value)

        if self.current is None:
            self.current = minor_moon_by_composition(data)
            Systems.get_current().add_astro_obj(self.current)
            self.parent.button.enable()
        else:
            for item in self.properties.get_widgets_from_layer(4):
                if item.text.lower() in self.current.composition:
                    item.value = str(self.current.composition[item.text.lower()]) + ' %'
                else:
                    item.value = '0'
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self):
        self.current = None
        self.has_values = False
        for vt in self.properties:
            vt.value = ''

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
            if self.parent.relative_mode:
                got_attr = getattr(self.current, elemento.text.lower())
            else:
                got_attr = getattr(self.current, elemento.text.lower()).to(tos[elemento.text.capitalize()])
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

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.add_button()


class AsteroidButton(Meta, BaseWidget):
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

    def move(self, x, y):
        self.rect.topleft = x, y

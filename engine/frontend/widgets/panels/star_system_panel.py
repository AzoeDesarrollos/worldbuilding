from engine.frontend.globales import WidgetGroup, ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_TEXTO
from engine.frontend.widgets.panels.common import ListedArea, Meta, TextButton
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.star_systems import system_type
from engine.equations.planetary_system import system
from engine.backend.eventhandler import EventHandler
from pygame import Surface, font
from ..values import ValueText


class StarSystemPanel(BaseWidget):
    selected = None

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Star System'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()
        self.f = font.SysFont('Verdana', 16)
        self.f.set_underline(True)
        self.write(self.name + ' Panel', self.f, centerx=self.rect.centerx, y=0)
        self.f2 = font.SysFont('Verdana', 16)
        self.stars_area = AvailableStars(self, ANCHO - 200, 32, 200, 350)
        self.properties.add(self.stars_area)
        self.current = SystemType(self)
        self.properties.add(self.current)

        self.setup_button = SetupButton(self, 490, 416)
        self.properties.add(self.setup_button)

        self.stars = []

    def setup(self, star):
        self.stars.append(star.object_data)
        self.stars_area.delete_objects(star.object_data)
        if len(self.stars) == 2:
            self.stars.sort(key=lambda s: s.mass.m, reverse=True)
            self.current.set_stars(*self.stars)

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def update(self):
        text = 'Stars in System: {}'.format(len(self.stars))
        self.write(text, self.f2, x=self.stars_area.rect.x, y=420)


class SystemType(BaseWidget):
    locked = False
    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.primary = None
        self.secondary = None
        self.separation = None
        self.ecc_p = None
        self.ecc_s = None
        self.create()
        EventHandler.register(self.clear, 'ClearData')

    def create(self):
        props = [
            'Primary Star', 'Secondary Star', 'Average Separation',  'Eccentriciy (primary)', 'Eccentricty (secondary)',
            'Barycenter', 'Maximun Separation', 'Minimun Separation', 'Forbbiden Zone Inner edge',
            'Forbbiden Zone Outer edge', 'System Type']

        for i, prop in enumerate([j for j in props]):
            self.properties.add(ValueText(self, prop, 3, 64 + i * 25, COLOR_TEXTO, COLOR_BOX))

        attrs = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        for idx, attr in enumerate(attrs):
            setattr(self, attr, self.properties.get_sprite(idx))

    def set_stars(self, primary, secondary):
        self.primary.value = primary
        self.secondary.value = secondary

    def get_determinants(self):
        names = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        dets = [self.primary.value, self.secondary.value]
        return dets + [float(getattr(self, name).value) for name in names if name not in ('primary', 'secondary')]

    def fill(self):
        if all([vt.value != '' for vt in self.properties.widgets()[0:4]]):
            sistema = system_type(self.separation.value)(*self.get_determinants())
            props = ['barycenter', 'max_sep', 'min_sep', 'inner_forbbiden_zone', 'outer_forbbiden_zone', 'system_name']
            for i, attr in enumerate(props, start=5):
                value = getattr(sistema, attr)
                pr = self.properties.get_widget(i)
                pr.value = value

    def clear(self, event):
        if event.data['panel'] is self.parent:
            for button in self.properties.widgets():
                button.text_area.clear()
            self.has_values = False

    def show(self):
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        for prop in self.properties.widgets():
            prop.hide()


class AvailableStars(ListedArea):
    def populate(self, stars):
        for i, star in enumerate(stars):
            listed = ListedStar(self, star, i, self.rect.x + 3, i * 16 + self.rect.y + 21)
            self.listed_objects.add(listed)

    def show(self):
        super().show()
        self.populate(system.stars)
        for listed in self.listed_objects.widgets():
            listed.show()


class ListedStar(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, star, idx, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 13)
        self.f2 = font.SysFont('Verdana', 13, bold=True)
        name = star.classification + ' #{}'.format(idx)
        self.object_data = star
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.select()
            self.parent.parent.selected = self
            self.parent.parent.setup_button.enable()

    def move(self, x, y):
        self.rect.topleft = x, y


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add Star'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.setup(self.parent.selected)
            self.disable()

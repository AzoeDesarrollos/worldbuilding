from engine.frontend.globales import WidgetGroup, ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_TEXTO
from engine.frontend.widgets.panels.common import ListedArea, Meta, TextButton
from engine.equations.star_systems import PTypeSystem, STypeSystem
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import system
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

        self.stars_area = AvailableStars(self, ANCHO - 200, 32, 200, 350)
        self.properties.add(self.stars_area, layer=2)
        self.current = SystemType(self)
        self.properties.add(self.current, layer=2)

        self.setup_button = SetupButton(self, 490, 416)
        self.properties.add(self.setup_button, layer=2)

        self.stars = []

    def setup(self, star):
        self.stars.append(star)
        self.stars_area.delete_objects(star)
        if len(self.stars) >= 2:
            pass

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()


class SystemType(BaseWidget):
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()

    def create(self, sistema):
        props = {
            'Primary Star': 'primary',
            'Secondary Star': 'secondary',
            'Average Separation': 'average_separation',
            'Eccentriciy (primary)': 'e_p',
            'Eccentricty (secondary)': 'e_s',
            'Barycenter': 'barycenter',
            'Maximun Separation': 'max_sep',
            'Minimun Separation': 'min_sep',
            'Forbbiden Zone Inner edge': 'inner_forbbiden_zone',
            'Forbbiden Zone Outer edge': 'outer_forbbiden_zone'
        }
        for i, prop in enumerate([j for j in props if hasattr(sistema, props[j])]):
            value = getattr(sistema, props[prop])
            vt = ValueText(self, prop, 3, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            vt.text_area.set_value(value)
            vt.text_area.update()
            self.properties.add(vt)

    def show(self):
        for prop in self.properties.widgets():
            prop.show()


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
        self.star_data = star
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.select()
            self.parent.parent.selected = self

    def move(self, x, y):
        self.rect.topleft = x, y


class SetupButton(TextButton):
    enabled = True

    def __init__(self, parent, x, y):
        name = 'Add Star'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.setup(self.parent.selected)

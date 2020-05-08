from engine.frontend.globales import Renderer, COLOR_BOX, COLOR_TEXTO, WidgetHandler
from engine.equations.planet import Planet
from .object_type import ObjectType
from .basewidget import BaseWidget
from .base_panel import BasePanel
from itertools import cycle
from pygame import font


class PlanetPanel(BasePanel):

    def __init__(self):
        super().__init__('Planet')
        self.current = PlanetType(self)

        self.unit = Unit(self, 'Earth', 0, 400)
        self.current.properties.add(self.unit)


class PlanetType(ObjectType):
    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Clase']
                         )

    def check_values(self):
        attrs = {}
        for button in self.properties.get_sprites_from_layer(1):
            if button.text_area.value:  # not empty
                try:
                    setattr(self, button.text.lower(), float(button.text_area.value))
                    attrs[button.text.lower()] = float(button.text_area.value)
                except ValueError:
                    setattr(self, button.text.lower(), button.text_area.value)
                    attrs[button.text.lower()] = button.text_area.value

        if len(attrs) > 1:
            attrs['unit'] = self.parent.unit.name.lower()
            self.current = Planet(attrs)
            self.has_values = True
            self.fill()

    def fill(self, tos=None):
        tos = {
            'Mass': 'kg',
            'Radius': 'km',
            'Gravity': 'm/s**2',
            'Escape_velocity': 'km/s'
        }
        super().fill(tos)


class Unit(BaseWidget):
    selected = False
    img_uns = None
    img_sel = None
    name = None

    def __init__(self, parent, name, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 12)
        self.f2 = font.SysFont('Verdana', 12, bold=True)
        self.base_rect = self.parent.image.blit(self.f2.render('Unit: ', 1, COLOR_TEXTO, COLOR_BOX), (x, y))
        self.name = name
        self.create()
        self.cycler = cycle(['Earth', 'Jupiter'])

    def show(self):
        Renderer.add_widget(self, layer=5000)
        WidgetHandler.add_widget(self)

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.add_widget(self)

    def on_mouseover(self):
        self.selected = True

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.name = next(self.cycler)
            self.create()

    def create(self):
        self.img_uns = self.f1.render(self.name, 1, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(self.name, 1, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(self.base_rect.right, self.base_rect.y))

    def update(self):
        if self.selected:
            self.image = self.img_sel
        else:
            self.image = self.img_uns
        self.selected = False

from engine.frontend.globales import Renderer, COLOR_BOX, COLOR_TEXTO, WidgetHandler
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planet import Planet
from itertools import cycle
from pygame import font


class PlanetPanel(BasePanel):

    def __init__(self, parent):
        super().__init__('Planet', parent)
        self.current = PlanetType(self)

        self.unit = Unit(self, 0, 416)
        self.current.properties.add(self.unit)

        self.button = TextButton(self, 490, 416)
        self.current.properties.add(self.button)


class PlanetType(ObjectType):
    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Clase']
                         )

    def clear_values(self):
        self.parent.parent.system.add_planet(self.current)
        for button in self.properties.get_sprites_from_layer(1):
            button.text_area.clear()
        self.has_values = False

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
            self.parent.button.enable()
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

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 12)
        self.f2 = font.SysFont('Verdana', 12, bold=True)
        render = self.f2.render('Unit: ', 1, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(bottomleft=(x, y))
        self.base_rect = self.parent.image.blit(render, render_rect)
        self.cycler = cycle(['Earth', 'Jupiter'])
        self.name = next(self.cycler)
        self.create()
        render = self.f2.render('Available mass: ', 1, COLOR_TEXTO, COLOR_BOX)
        self.mass_rect = render.get_rect(bottomleft=(x+100, y))
        self.parent.image.blit(render, self.mass_rect)

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

    def show_mass(self):
        if self.name == 'Earth':
            mass = self.parent.parent.system.terra_mass
        else:
            mass = self.parent.parent.system.gigant_mass
        attr = '{:,g}'.format((round(mass, 3)))
        render = self.f1.render(str(attr), 1, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(left=self.mass_rect.right+6, bottom=self.mass_rect.bottom)
        render_rect.inflate_ip(16, 0)
        self.parent.image.fill(COLOR_BOX, render_rect)
        self.parent.image.blit(render, render_rect)

    def create(self):
        self.img_uns = self.f1.render(self.name, 1, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(self.name, 1, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(self.base_rect.right, self.base_rect.y))

    def update(self):
        self.show_mass()
        if self.selected:
            self.image = self.img_sel
        else:
            self.image = self.img_uns
        self.selected = False


class TextButton(BaseWidget):
    selected = False
    enabled = False

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 16)
        self.f2 = font.SysFont('Verdana', 16, bold=True)
        self.img_dis = self.f1.render('Add Planet', 1, (200, 200, 200), COLOR_BOX)
        self.img_uns = self.f1.render('Add Planet', 1, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render('Add Planet', 1, COLOR_TEXTO, COLOR_BOX)

        self.image = self.img_dis
        self.rect = self.image.get_rect(bottomleft=(x, y))

    def show(self):
        Renderer.add_widget(self, layer=5000)
        WidgetHandler.add_widget(self)

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.add_widget(self)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.parent.current.clear_values()

    def on_mouseover(self):
        if self.enabled:
            self.selected = True

    def enable(self):
        self.enabled = True

    def update(self):
        if self.enabled:
            if self.selected:
                self.image = self.img_sel
            else:
                self.image = self.img_uns
        self.selected = False

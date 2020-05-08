from engine.frontend.graph.graph import graph_loop
from engine.frontend.globales import Renderer
from engine.equations.planet import Planet
from pygame.sprite import LayeredUpdates
from .object_type import ObjectType
from .base_panel import BasePanel
from itertools import cycle


class PlanetPanel(BasePanel):

    def __init__(self):
        super().__init__('Planet', 12, 90)
        x, y = 0, 50
        self.planet_types = LayeredUpdates()
        t = TerrestialType(self, x, y)
        p1 = PlanetType(self, 'Gas Giant', x, y)
        p2 = PlanetType(self, 'Dwarf Planet', x, y)
        self.planet_types.add(t, p1, p2)
        self.cycler = cycle([t, p1, p2])
        self.current = p1


class PlanetType(ObjectType):
    selected = False

    mass = 0
    radius = 0
    density = 0
    gravity = 0

    has_values = False

    def __init__(self, parent, text, x, y):
        super().__init__(parent, text, x, y,
                         ['Mass', 'Radius', 'Gravity', 'escape_velocity'],
                         ['Density', 'Volume', 'Surface', 'Circumference', 'Clase']
                         )

    def check_values(self):
        attrs = {}
        for button in self.properties:
            if button.text_area.value:  # not empty
                setattr(self, button.text.lower(), float(button.text_area.value))
                attrs[button.text.lower()] = float(button.text_area.value)

        if len(attrs) > 1:
            if 'Giant' in self.text:
                attrs['unit'] = 'jupiter'
            else:
                attrs['unit'] = 'earth'
            attrs['class'] = self.text
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


class TerrestialType(PlanetType):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Terrestial', x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.active = True
            data = graph_loop()
            for elemento in self.properties:
                if elemento.text.lower() in data:
                    elemento.text_area.value = str(data[elemento.text.lower()])
                    elemento.text_area.update()
                    elemento.text_area.show()
            self.check_values()
            Renderer.reset()

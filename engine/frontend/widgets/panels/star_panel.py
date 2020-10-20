from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.sprite_star import StarSprite
from engine.frontend.widgets.object_type import ObjectType
from engine.equations.star import Star
from engine.backend.eventhandler import EventHandler


class StarPanel(BasePanel):
    def __init__(self, parent):
        super().__init__('Star', parent)
        self.current = StarType(self)


class StarType(ObjectType):
    def __init__(self, parent):
        super().__init__(parent,
                         ['Mass', 'Luminosity', 'Radius', 'Lifetime', 'Temperature'],
                         ['Volume', 'Density', 'Circumference', 'Surface', 'Classification'])
        EventHandler.register(self.load_star, 'LoadData')
        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.save_star, 'Save')

    def set_star(self, star_data):
        star = Star(star_data)
        self.parent.parent.set_system(star)
        self.current = star
        self.has_values = True
        self.fill()

    def load_star(self, event):
        if not isinstance(self.current, Star):
            mass = event.data['Star']['mass']
            self.set_star({'mass': mass})

    def save_star(self, event):
        EventHandler.trigger(event.tipo + 'Data', 'Star',
                             {'Star': {'name': self.current.name, 'mass': self.current.mass.m}})

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()
        self.current.sprite.kill()

    def fill(self, tos=None):
        tos = {
            'Mass': 'kg',
            'Radius': 'km',
            'Luminosity': 'W',
            'Lifetime': 'year',
            'Temperature': 'kelvin'
        }
        super().fill(tos)

        a = StarSprite(self, self.current, 460, 100)
        self.properties.add(a)

    def hide(self):
        super().hide()
        for value in self.properties.widgets():
            value.disable()

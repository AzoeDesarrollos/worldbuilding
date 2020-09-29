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

    def set_star(self, star):
        self.parent.parent.set_system(star)
        self.current = star
        self.has_values = True
        self.fill()

    def load_star(self, event):
        mass = event.data['star']
        self.set_star(Star({'mass': mass}))

    def clear(self, event):
        if event.data['panel'] is self:
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

        StarSprite(self.current, 460, 100)

    def hide(self):
        super().hide()
        for value in self.properties.widgets():
            value.disable()

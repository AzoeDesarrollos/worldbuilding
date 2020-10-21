from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.sprite_star import StarSprite
from engine.frontend.widgets.object_type import ObjectType
from engine.equations.star import Star
from engine.backend.eventhandler import EventHandler
from engine.frontend.globales import COLOR_AREA, WidgetGroup
from engine.frontend.widgets.panels.common import TextButton, Meta
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import font


class StarPanel(BasePanel):
    curr_x = 0
    curr_y = 440

    def __init__(self, parent):
        super().__init__('Star', parent)
        self.current = StarType(self)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.button = AddStarButton(self.current, 490, 416)
        self.current.properties.add(self.button)
        self.stars = WidgetGroup()

    def show(self):
        super().show()
        self.is_visible = True

    def add_button(self, star):
        button = StarButton(self.current, star, self.curr_x, self.curr_y)
        self.stars.add(button)
        self.sort_buttons()
        self.current.properties.add(button, layer=2)

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.stars.widgets():
            bt.move(x, y)
            if not self.area_buttons.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def on_mousebuttondown(self, event):
        if event.button == 1:
            super().on_mousebuttondown(event)

        elif event.button in (4, 5):
            buttons = self.stars.widgets()
            if self.area_buttons.collidepoint(event.pos) and len(buttons):
                last_is_hidden = not buttons[-1].is_visible
                first_is_hidden = not buttons[0].is_visible
                if event.button == 4 and first_is_hidden:
                    self.curr_y += 32
                elif event.button == 5 and last_is_hidden:
                    self.curr_y -= 32
                self.sort_buttons()


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


class AddStarButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Star', x, y)

    def on_mousebuttondown(self, event):
        star = self.parent.current
        self.parent.parent.add_button(star)


class StarButton(Meta, BaseWidget):
    def __init__(self, parent, star, x, y):
        super().__init__(parent)
        self.planet_data = star
        self.f1 = font.SysFont('Verdana', 13)
        self.f2 = font.SysFont('Verdana', 13, bold=True)
        name = star.classification+' #{}'.format(len(self.parent.parent.stars))
        self.img_uns = self.f1.render(name, True, star.color, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, star.color, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        pass

    def update(self):
        super().update()
        if self.parent.parent.is_visible:
            self.show()
        else:
            self.hide()

    def move(self, x, y):
        self.rect.topleft = x, y

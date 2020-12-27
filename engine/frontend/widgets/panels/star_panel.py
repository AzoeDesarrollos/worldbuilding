from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, WidgetGroup
from engine.frontend.widgets.panels.common import TextButton, Meta
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.sprite_star import StarSprite
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.equations.star import Star


class StarPanel(BasePanel):
    curr_x = 3
    curr_y = 440

    add_on_exit = False

    def __init__(self, parent):
        super().__init__('Star', parent)
        self.current = StarType(self)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        f = self.crear_fuente(14, underline=True)
        render = f.render('Stars', True, COLOR_TEXTO, COLOR_AREA)
        self.image.blit(render, self.area_buttons.topleft)
        self.button = AddStarButton(self.current, 490, 416)
        self.current.properties.add(self.button)
        self.stars = WidgetGroup()
        EventHandler.register(self.save_stars, 'Save')
        EventHandler.register(self.load_stars, 'LoadData')

    def save_stars(self, event):
        data = []
        for star_button in self.stars.widgets():
            star = star_button.object_data
            star_data = {
                'name': star.name,
                'mass': star.mass.m,
            }
            data.append(star_data)
        EventHandler.trigger(event.tipo + 'Data', 'Star', {"Stars": data})

    def load_stars(self, event):
        for star_data in event.data.get('Stars', []):
            star = Star({'mass': star_data['mass']})
            self.add_button(star)

    def show(self):
        super().show()
        self.button.show()
        for star in self.stars.widgets():
            star.show()

    def hide(self):
        super().hide()
        self.button.hide()
        if self.add_on_exit:
            s = self.current.current
            Systems.set_system(s)
        for star in self.stars.widgets():
            star.hide()

    def add_button(self, star):
        button = StarButton(self.current, star, self.curr_x, self.curr_y)
        self.stars.add(button)
        Systems.add_star(star)
        self.sort_buttons()
        self.current.properties.add(button, layer=2)
        self.current.erase()
        self.button.disable()

        self.add_on_exit = len(self.stars) == 1
        self.parent.set_skippable(self.add_on_exit)

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

    def set_star(self, star_data):
        star = Star(star_data)
        self.parent.button.enable()
        self.current = star
        self.fill()

    def show_current(self, star):
        self.erase()
        self.current = star
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self):
        if self.has_values:
            self.current.sprite.kill()
        super().erase()

    def fill(self, tos=None):
        tos = {
            'Mass': 'kg',
            'Radius': 'km',
            'Luminosity': 'W',
            'Lifetime': 'year',
            'Temperature': 'kelvin'
        }
        super().fill(tos)

        if self.current.sprite is None:
            self.current.sprite = StarSprite(self, self.current, 460, 100)
            self.properties.add(self.current.sprite)
        else:
            self.current.sprite.show()


class AddStarButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Star', x, y)

    def on_mousebuttondown(self, event):
        if self.enabled and self.parent.has_values:
            star = self.parent.current
            self.parent.parent.add_button(star)
            self.disable()


class StarButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, star, x, y):
        super().__init__(parent)
        self.object_data = star
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        name = star.classification + ' #{}'.format(len(self.parent.parent.stars))
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.show_current(self.object_data)

    def move(self, x, y):
        self.rect.topleft = x, y

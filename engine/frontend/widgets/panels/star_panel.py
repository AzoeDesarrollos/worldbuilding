from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, WidgetGroup, ANCHO
from engine.frontend.widgets.panels.common import TextButton
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.sprite_star import StarSprite
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets.meta import Meta
from engine.equations.star import Star


class StarPanel(BasePanel):
    curr_x = 3
    curr_y = 440

    add_on_exit = False

    def __init__(self, parent):
        super().__init__('Star', parent)
        self.properties = WidgetGroup()
        self.current = StarType(self)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        f = self.crear_fuente(14, underline=True)
        render = f.render('Stars', True, COLOR_TEXTO, COLOR_AREA)
        self.image.blit(render, self.area_buttons.topleft)
        self.button_add = AddStarButton(self, ANCHO - 13, 398)
        self.button_del = DelStarButton(self, ANCHO - 13, 416)
        self.properties.add(self.button_add, self.button_del, layer=1)
        self.stars = []
        EventHandler.register(self.save_stars, 'Save')
        EventHandler.register(self.load_stars, 'LoadData')

    @property
    def star_buttons(self):
        # adds readability
        return self.properties.get_widgets_from_layer(2)

    def save_stars(self, event):
        data = []
        for star_button in self.star_buttons:
            star = star_button.object_data
            star_data = {
                'name': star.name,
                'mass': star.mass.m,
                'id': star.id,
                'spin': star.spin
            }
            data.append(star_data)
        EventHandler.trigger(event.tipo + 'Data', 'Star', {"Stars": data})

    def load_stars(self, event):
        for idx, star_data in enumerate(event.data.get('Stars', [])):
            star_data.update({'idx': idx})
            star = Star(star_data)
            if star not in self.stars:
                self.stars.append(star)
                self.add_button(star)
                # Systems.set_system(star)

        if len(self.star_buttons):
            self.current.current = self.star_buttons[0].object_data

    def show(self):
        super().show()
        for obj in self.properties.widgets():
            obj.show()
        if self.current.has_values:
            self.current.current.sprite.show()

    def hide(self):
        super().hide()
        for obj in self.properties.widgets():
            obj.hide()
        if self.add_on_exit:
            self.parent.set_skippable('Star System', True)
            Systems.set_system(self.current.current)
        else:
            self.parent.set_skippable('Star System', False)

    def add_button(self, star):
        button = StarButton(self.current, star, self.curr_x, self.curr_y)
        self.properties.add(button, layer=2)
        Systems.add_star(star)
        if star not in self.stars:
            self.stars.append(star)
        self.sort_buttons()
        self.current.erase()
        self.button_add.disable()

    def del_button(self, planet):
        button = [i for i in self.star_buttons if i.object_data == planet][0]
        self.properties.remove(button)
        self.sort_buttons()
        self.button_del.disable()
        self.stars.remove(button.object_data)

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.star_buttons:
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

    def select_one(self, btn):
        for button in self.star_buttons:
            button.deselect()
        btn.select()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            super().on_mousebuttondown(event)

        elif event.button in (4, 5):
            buttons = self.star_buttons
            if self.area_buttons.collidepoint(event.pos) and len(buttons):
                last_is_hidden = not buttons[-1].is_visible
                first_is_hidden = not buttons[0].is_visible
                if event.button == 4 and first_is_hidden:
                    self.curr_y += 32
                elif event.button == 5 and last_is_hidden:
                    self.curr_y -= 32
                self.sort_buttons()

    def update(self):
        self.add_on_exit = len(self.stars) == 1


class StarType(ObjectType):
    def __init__(self, parent):
        rel_props = ['Mass', 'Luminosity', 'Radius', 'Lifetime', 'Surface temperature']
        rel_args = ['mass', 'luminosity', 'radius', 'lifetime', 'temperature']
        abs_args = ['density', 'volume', 'circumference', 'surface', 'spin', 'classification']
        abs_props = ['Density', 'Volume', 'Circumference', 'Surface area', 'Spin', 'Classification']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 0, 1)

    def set_star(self, star_data):
        star_data.update({'idx': len(self.parent.star_buttons)})
        star = Star(star_data)
        self.parent.button_add.enable()
        self.current = star
        self.fill()

    def destroy_button(self):
        Systems.remove_star(self.current)
        self.parent.del_button(self.current)
        self.erase()

    def show_current(self, star):
        self.erase()
        self.current = star
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()
            self.parent.button_del.disable()
            self.parent.button_add.disable()

    def erase(self):
        if self.has_values:
            self.current.sprite.kill()
        super().erase()

    def fill(self, tos=None):
        tos = {
            'mass': 'kg',
            'radius': 'km',
            'luminosity': 'W',
            'lifetime': 'year',
            'temperature': 'kelvin'
        }
        super().fill(tos)
        system = Systems.get_current()
        if system is not None:
            system.update()

        if self.current.sprite is None:
            self.current.sprite = StarSprite(self, self.current, 460, 100)
            self.properties.add(self.current.sprite)
        self.current.sprite.show()


class AddStarButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Star', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if self.enabled and self.parent.current.has_values:
            star = self.parent.current.current
            self.parent.add_button(star)
            self.disable()


class DelStarButton(TextButton):
    current = None

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Star', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if self.enabled and event.button == 1:
            self.parent.current.destroy_button()


class StarButton(Meta):
    enabled = True

    def __init__(self, parent, star, x, y):
        super().__init__(parent)
        self.object_data = star
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        name = star.classification + ' #{}'.format(len(self.parent.parent.star_buttons))
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.show_current(self.object_data)
            if not self.object_data.sprite.is_visible:
                self.object_data.sprite.show()
            self.parent.parent.select_one(self)
            self.parent.parent.button_del.enable()

    def move(self, x, y):
        self.rect.topleft = x, y

    def hide(self):
        super().hide()
        if self.object_data.sprite is not None:
            self.object_data.sprite.hide()

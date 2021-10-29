from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, WidgetGroup, ANCHO, COLOR_BOX, COLOR_SELECTED
from engine.frontend.widgets.panels.common import TextButton
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.sprite_star import StarSprite
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets.meta import Meta
from pygame import Surface, mouse, draw
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
        EventHandler.register(self.name_current, 'NameObject')

        self.age_bar = AgeBar(self, 50, 420 - 32)
        self.properties.add(self.age_bar, layer=1)
        f2 = self.crear_fuente(10)
        self.write('start', f2, centerx=self.age_bar.rect.left, top=self.age_bar.rect.bottom + 1)
        self.write('end', f2, centerx=self.age_bar.rect.right, top=self.age_bar.rect.bottom + 1)

    @property
    def star_buttons(self):
        # adds readability
        return self.properties.get_widgets_from_layer(2)

    def save_stars(self, event):
        data = {}
        for star_button in self.star_buttons:
            star = star_button.object_data
            star_data = {
                'name': star.name,
                'mass': star.mass.m,
                'spin': star.spin,
                'age': star.age.m
            }
            data[star.id] = star_data
        EventHandler.trigger(event.tipo + 'Data', 'Star', {"Stars": data})

    def load_stars(self, event):
        for idx, id in enumerate(event.data['Stars']):
            star_data = event.data['Stars'][id]
            star_data.update({'idx': idx, 'id': id})
            star = Star(star_data)
            if star not in self.stars:
                self.stars.append(star)
                self.add_button(star)

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
        if self.is_visible:
            self.sort_buttons()
        self.current.erase()
        self.button_add.disable()

    def del_button(self, star):
        button = [i for i in self.star_buttons if i.object_data == star][0]
        self.properties.remove(button)
        if self.is_visible:
            self.sort_buttons()
        self.button_del.disable()
        self.stars.remove(button.object_data)
        Systems.remove_star(star)

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

    def on_mousebuttonup(self, event):
        if event.button == 1:
            self.age_bar.on_mousebuttonup(event)

    def update(self):
        self.add_on_exit = len(self.stars) == 1

    def name_current(self, event):
        if event.data['object'] in self.stars:
            star = event.data['object']
            star.name = event.data['name']
            star.has_name = True


class StarType(ObjectType):
    def __init__(self, parent):
        rel_props = ['Mass', 'Luminosity', 'Radius', 'Lifetime', 'Surface temperature']
        rel_args = ['mass', 'luminosity', 'radius', 'lifetime', 'temperature']
        abs_args = ['density', 'volume', 'circumference', 'surface', 'spin', 'classification', 'age']
        abs_props = ['Density', 'Volume', 'Circumference', 'Surface area', 'Spin', 'Classification', 'Age']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 0, 1)

        f = self.crear_fuente(16, bold=True)
        self.habitable = f.render('Habitable', True, (0, 255, 0), COLOR_BOX)
        self.hab_rect = self.habitable.get_rect(right=self.parent.rect.right - 10, y=self.parent.rect.y + 50)

    def set_star(self, star_data):
        cls = Star.get_class(star_data['mass'])
        star_data.update({'idx': len([s for s in self.parent.stars if s.cls == cls])})
        star = Star(star_data)
        self.parent.button_add.enable()
        self.current = star
        self.fill()
        self.toggle_habitable()
        self.parent.age_bar.cursor.set_x(star)

    def destroy_button(self):
        Systems.remove_star(self.current)
        self.parent.del_button(self.current)
        self.erase()

    def show_current(self, star):
        self.erase()
        self.current = star
        self.parent.age_bar.cursor.set_x(star)
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()
            self.parent.button_del.disable()
            self.parent.button_add.disable()

    def erase(self):
        if self.has_values:
            self.current.sprite.kill()
            self.parent.image.fill(COLOR_BOX, self.hab_rect)
            self.parent.age_bar.cursor.hide()
        super().erase()

    def toggle_habitable(self):
        if self.current.habitable:
            self.parent.image.blit(self.habitable, self.hab_rect)
        else:
            self.parent.image.fill(COLOR_BOX, self.hab_rect)

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
        self.parent.age_bar.enable()

    def set_age(self, age_percent):
        if self.has_values:
            age = self.current.set_age(age_percent)
            self.fill()
            system = Systems.get_system_by_star(self.current)
            if system is not None:
                system.age = age
                for astrobody in system.astro_bodies:
                    astrobody.update_everything()


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
        if not star.has_name:
            name = star.classification + ' #{}'.format(star.idx)
        else:
            name = star.name
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
            self.parent.toggle_habitable()

    def move(self, x, y):
        self.rect.topleft = x, y

    def hide(self):
        super().hide()
        if self.object_data.sprite is not None:
            self.object_data.sprite.hide()


class AgeBar(Meta):
    cursor = None

    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.image = Surface((401, 7))
        self.rect = self.image.get_rect(topleft=[x, y])
        self.image.fill(COLOR_BOX, [0, 0, 400, 7])
        draw.aaline(self.image, COLOR_TEXTO, [0, 3], [self.rect.w, 3])
        for i in range(11):
            dx = round((i / 10) * self.rect.w)
            draw.aaline(self.image, COLOR_TEXTO, [dx, 0], [dx, 7])
        self.cursor = AgeCursor(self, self.rect.centery)

    def on_mousebuttonup(self, event):
        if self.cursor is not None:
            self.cursor.pressed = False

    def on_mousemotion(self, rel):
        x = mouse.get_pos()[0]
        if self.cursor is not None and abs(x - self.cursor.rect.centerx) <= 3:
            mouse.set_pos(*self.cursor.rect.center)

    def enable(self):
        self.cursor.show()

    def show(self):
        super().show()
        if self.parent.current.has_values:
            self.cursor.show()

    def hide(self):
        super().hide()
        self.cursor.hide()


class AgeCursor(Meta):
    pressed = False
    enabled = True

    def __init__(self, parent, y):
        super().__init__(parent)
        self.img_uns = self.crear(1, COLOR_TEXTO)
        self.img_sel = self.crear(3, COLOR_SELECTED)
        self.img_dis = self.crear(5, COLOR_TEXTO)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centery=y)
        self.center = self.rect.centerx
        self.show()

    @staticmethod
    def crear(w, color):
        image = Surface((w, 13))
        image.fill(color)
        return image

    def select(self):
        super().select()
        self.rect = self.image.get_rect(centerx=self.center)

    def deselect(self):
        super().deselect()
        self.rect = self.image.get_rect(centerx=self.center)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.pressed = True

    def on_mousebuttonup(self, event):
        if event.button == 1:
            self.pressed = False

    def on_movement(self, x: int):
        self.parent.parent.current.set_age((x - 50) / 400)

    def set_x(self, star):
        age = round(star.age.m/star.lifetime.to('years').m, 3)
        self.rect.x = round(age*(self.parent.rect.w-1))+self.parent.rect.x

    def update(self):
        super().update()
        x = mouse.get_pos()[0]
        if self.pressed:
            mouse.set_pos(x, self.rect.centery)
            self.has_mouseover = True
            self.rect.x = x if 50 <= x <= 450 else self.rect.x
            self.on_movement(self.rect.x)

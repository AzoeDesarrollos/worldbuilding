from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, ANCHO, COLOR_BOX, COLOR_SELECTED, Renderer, Group
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.panels.common import TextButton
from engine.frontend.widgets.object_type import ObjectType
from engine.frontend.widgets.sprite_star import StarSprite
from engine.backend import EventHandler, Systems
from engine.frontend.widgets.meta import Meta
from pygame import Surface, mouse, draw
from engine.equations.star import Star
from .common import ColoredBody


class StarPanel(BasePanel):
    default_spacing = 7

    add_on_exit = False

    def __init__(self, parent):
        super().__init__('Star', parent)
        self.properties = Group()
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
        self.write('past', f2, centerx=self.age_bar.rect.left, top=self.age_bar.rect.bottom + 1)
        self.write('present', f2, centerx=234, top=self.age_bar.rect.bottom + 1)
        self.write('future', f2, centerx=self.age_bar.rect.right, top=self.age_bar.rect.bottom + 1)

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
                'age': star.age.m,
                'pos': dict(zip(['x', 'y', 'z'], star.position))
            }
            data[star.id] = star_data
        EventHandler.trigger(event.tipo + 'Data', 'Star', {"Stars": data})

    def load_stars(self, event):
        systems = []
        for id in event.data['Stars']:
            star_data = event.data['Stars'][id]
            star_data.update({'id': id})
            star = Star(star_data)
            star.idx = len([i for i in self.stars if i.cls == star.cls])
            Systems.add_star(star)
            if star not in self.stars:
                self.stars.append(star)
                self.add_button(star)
                Renderer.update()
            for id_p in event.data['Stellar Orbits']:
                orbit_data = event.data['Stellar Orbits'][id_p]
                if orbit_data['star_id'] == id and star.id not in systems:
                    Systems.set_system(star)
                    systems.append(star.id)

        if len(self.star_buttons):
            # self.current.current = self.star_buttons[0].object_data
            self.current.enable()

    def deselect_buttons(self):
        for button in self.star_buttons:
            button.deselect()

    def show(self):
        super().show()
        self.sort_buttons(self.star_buttons)
        for obj in self.properties.widgets():
            obj.show()
        if self.current.has_values:
            self.current.current.sprite.show()
        else:
            self.deselect_buttons()

    def hide(self):
        super().hide()
        for obj in self.properties.widgets():
            obj.hide()
        if self.add_on_exit or not len(self.stars):
            self.parent.set_skippable('Star System', True)
            self.parent.set_skippable('Multiple Stars', True)
            if len(self.stars) == 1:
                Systems.set_system(self.stars[0])
        else:
            self.parent.set_skippable('Star System', False)

    def add_button(self, star):
        button = StarButton(self.current, star, str(star), self.curr_x, self.curr_y)
        self.properties.add(button, layer=2)
        Systems.add_star(star)
        if star not in self.stars:
            self.stars.append(star)
        if self.is_visible:
            self.sort_buttons(self.star_buttons)
        self.current.erase()
        self.button_add.disable()
        return button

    def del_button(self, star):
        button = [i for i in self.star_buttons if i.object_data == star][0]
        self.properties.remove(button)
        if self.is_visible:
            self.sort_buttons(self.star_buttons)
        self.button_del.disable()
        self.stars.remove(button.object_data)
        Systems.remove_star(star)

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
                self.sort_buttons(self.star_buttons)

    def on_mousebuttonup(self, event):
        if event.button == 1:
            self.age_bar.on_mousebuttonup(event)

    def update(self):
        self.add_on_exit = len(self.stars) == 1

    def name_current(self, event):
        if event.data['object'] in self.stars:
            star = event.data['object']
            star.set_name(event.data['name'])


class StarType(ObjectType):
    def __init__(self, parent):
        rel_props = ['Mass', 'Luminosity', 'Radius', 'Lifetime', 'Surface temperature']
        rel_args = ['mass', 'luminosity', 'radius', 'lifetime', 'temperature']
        abs_args = ['density', 'volume', 'circumference', 'surface', 'spin', 'classification', 'age']
        abs_props = ['Density', 'Volume', 'Circumference', 'Surface area', 'Spin', 'Classification', 'Age']
        super().__init__(parent, rel_props, abs_props, rel_args, abs_args)
        self.set_modifiables('relatives', 0, 1)
        self.relatives.widgets()[0].enable()

        f = self.crear_fuente(16, bold=True)
        self.habitable = f.render('Habitable', True, (0, 255, 0), COLOR_BOX)
        self.hab_rect = self.habitable.get_rect(right=self.parent.rect.right - 10, y=self.parent.rect.y + 50)

    def set_star(self, star_data):
        cls = Star.get_class(star_data['mass'])
        star = Star(star_data)
        star.idx = len([s for s in self.parent.stars if s.cls == cls])
        self.parent.button_add.enable()
        if self.current is not None:
            self.current.sprite.kill()
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
            self.parent.deselect_buttons()
            self.parent.button_del.disable()
            self.parent.button_add.disable()

    def enable(self):
        super().enable()
        for arg in self.properties.widgets():
            arg.enable()

    def disable(self):
        for arg in self.properties.widgets():
            arg.disable()
        super().disable()

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
            1: {
                'mass': 'kg',
                'radius': 'km',
                'luminosity': 'W',
                'lifetime': 'year',
                'temperature': 'kelvin'
            }
        }
        super().fill(tos)
        system = Systems.get_current()
        if system is not None:
            system.update()

        new = StarSprite(self, self.current, 460, 100)
        if new.is_distict(self.current.sprite):
            self.current.sprite = new
            self.properties.add(self.current.sprite, layer=3)

        self.current.sprite.show()
        self.parent.age_bar.enable()
        self.parent.enable()

    def set_age(self, age_percent):
        if self.has_values:
            self.current.set_age(age_percent)
            system = Systems.get_system_by_star(self.current)
            if system is not None:
                system.age = self.current.age
            self.fill()

    def propagate_age_changes(self):
        system = Systems.get_system_by_star(self.current)
        if system is not None:
            for astrobody in system.astro_bodies:
                astrobody.update_everything()


class AddStarButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Star', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled and self.parent.current.has_values:
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


class StarButton(ColoredBody):
    enabled = True

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.show_current(self.object_data)
            if not self.object_data.sprite.is_visible:
                self.object_data.sprite.show()
            self.parent.parent.select_one(self)
            self.parent.parent.button_del.enable()
            self.parent.toggle_habitable()
        elif event.button in (4, 5):
            self.parent.parent.on_mousebuttondown(event)

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
        draw.aaline(self.image, COLOR_TEXTO, [0, 0], [0, 7])
        draw.aaline(self.image, COLOR_TEXTO, [184, 0], [184, 7])
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
        self.centerx = self.rect.centerx

    @staticmethod
    def crear(w, color):
        image = Surface((w, 13))
        image.fill(color)
        return image

    def select(self):
        super().select()
        self.rect = self.image.get_rect(centerx=self.centerx)

    def deselect(self):
        super().deselect()
        self.rect = self.image.get_rect(centerx=self.centerx)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            EventHandler.trigger('DeselectOthers', self, {})
            self.pressed = True

    def on_mousebuttonup(self, event):
        if event.button == 1:
            self.pressed = False
            self.parent.parent.current.propagate_age_changes()

    def on_movement(self, x: int):
        self.parent.parent.current.set_age((x - 50) / 400)

    def set_x(self, star):
        age = round(star.age.m / star.lifetime.to('years').m, 3)
        self.rect.x = round(age * (self.parent.rect.w - 1)) + self.parent.rect.x

    def update(self):
        super().update()
        x = mouse.get_pos()[0]
        if self.pressed:
            mouse.set_pos(x, self.rect.centery)
            self.has_mouseover = True
            self.rect.x = x if 50 <= x <= 450 else self.rect.x
            self.on_movement(self.rect.x)

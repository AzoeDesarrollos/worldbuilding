from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, ANCHO, COLOR_BOX, Renderer, Group
from engine.frontend.widgets.panels.common import TextButton, BaseSlider, BaseCursor
from engine.frontend.widgets.panels.base_panel import BasePanel
from engine.frontend.widgets.object_type import ObjectType
from engine.backend import EventHandler, roll
from pygame import Surface, SRCALPHA, Color, draw
from engine.frontend.widgets.meta import Meta
from .common import ColoredBody, ListedArea
from engine.equations.space import Universe
from engine.equations.star import Star


class StarPanel(BasePanel):
    default_spacing = 7

    add_on_exit = False

    show_swap_system_button = False

    last_id = -1

    def __init__(self, parent):
        super().__init__('Star', parent)
        self.properties = Group()
        self.button_group = Group()
        self.current = StarType(self)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        f = self.crear_fuente(14, underline=True)
        render = f.render('Stars', True, COLOR_TEXTO, COLOR_AREA)
        self.image.blit(render, self.area_buttons.topleft)
        self.button_add = AddStarButton(self, ANCHO - 13, 398)
        self.button_del = DelStarButton(self, ANCHO - 13, 416)
        self.button_auto = AutomaticButton(self, 4, 50)
        self.properties.add(self.button_add, self.button_del, self.button_auto, layer=1)
        self.stars = []
        EventHandler.register(self.save_stars, 'Save')
        EventHandler.register(self.load_stars, 'LoadStars')
        EventHandler.register(self.name_current, 'NameObject')
        EventHandler.register(self.export_data, 'ExportData')

        self.age_bar = AgeBar(self, 50, 420 - 32)
        self.properties.add(self.age_bar, layer=1)
        f2 = self.crear_fuente(10)
        self.write('past', f2, centerx=self.age_bar.rect.left, top=self.age_bar.rect.bottom + 1)
        self.write('present', f2, centerx=234, top=self.age_bar.rect.bottom + 1)
        self.write('future', f2, centerx=self.age_bar.rect.right, top=self.age_bar.rect.bottom + 1)

        self.potential_stars = PotentialStars(self, ANCHO - 150, 32, 150, 340)
        self.properties.add(self.potential_stars, layer=1)
        self.selected_proto = None

        _right = self.potential_stars.rect.left - 50
        self.true_color_block = ColorBlock(self, 'True Color', right=_right, y=40)
        self.peak_light_block = ColorBlock(self, 'Peak Light', right=_right, y=self.true_color_block.rect.bottom + 18)
        self.properties.add(self.true_color_block, self.peak_light_block, layer=1)

    @property
    def star_buttons(self):
        # adds readability
        return self.button_group.get_widgets_from_layer(self.last_id)

    def save_stars(self, event):
        data1, data2 = {}, {}
        for star in self.stars:
            star_data = {
                'name': star.name if star.name is not None else str(star),
                'mass': star.mass.m,
                'spin': star.spin,
                'age': star.age.m,
                "neighbourhood_id": star.neighbourhood_id,
                'flagged': star.flagged
            }
            data1[star.id] = star_data

            if star.position is not None:
                system_data = {
                    "neighbourhood_id": Universe.nei().id,
                    'position': dict(zip(['x', 'y', 'z'], star.position)),
                }
                data2[star.id] = system_data

        if len(data1):
            EventHandler.trigger(event.tipo + 'Data', 'Star', {"Stars": data1})
        if len(data2):
            EventHandler.trigger(event.tipo + 'Data', 'Star', {"Single Systems": data2})

    def load_stars(self, event):
        for id in event.data['Stars']:
            star_data = event.data['Stars'][id]
            star_data.update({'id': id})
            star = self.current.set_star(star_data, inactive=True)
            if star not in self.stars:
                self.stars.append(star)
                self.add_button(star)
                Renderer.update()

        if len(self.star_buttons):
            self.current.enable()

    def deselect_buttons(self):
        for button in self.star_buttons:
            button.deselect()

    def show(self):
        super().show()
        if Universe.nei() is not None:
            self.last_id = Universe.nei().id
        for obj in self.properties.get_widgets_from_layer(1):
            obj.show()

        self.sort_buttons(self.star_buttons)
        self.deselect_buttons()
        self.parent.swap_neighbourhood_button.unlock()

    def hide(self):
        super().hide()
        # binary_systems = 1
        # if Universe.current_galaxy is not None:
        #     binary_systems = Universe.nei().quantities['Binary']
        #     value_brown = Universe.nei().other['brown']
        #     value_white = Universe.nei().other['white']
        #     value_black_or_neutron = Universe.nei().other['black']
        #     if not any([value_brown, value_white, value_black_or_neutron]):
        #         self.parent.set_skippable('Compact Objects', True)

        for obj in self.properties.widgets():
            obj.hide()
        for button in self.button_group.widgets():
            button.hide()
        #
        if not len(self.stars):
            self.parent.set_skippable('Star System', True)
            self.parent.set_skippable('Multiple Stars', True)
            self.parent.swap_neighbourhood_button.lock()
        # # elif binary_systems == 0:
        # #     self.parent.set_skippable('Star System', True)
        # else:
        #     self.parent.set_skippable('Star System', False)

    # @staticmethod
    # def add_stars(star):
    #     singles = [system for system in Universe.systems if system.composition == 'single']
    #     chosen = choice(singles)
    #     Universe.remove_astro_obj(chosen)
    #     system = SingleSystem(star)
    #     system.cartesian = chosen.location
    #     offset = Universe.nei().location
    #     system.set_orbit(offset)
    #     Systems.set_planetary_system(star)
    #     Universe.nei().add_true_system(system)

    def add_button(self, star):
        button = StarButton(self.current, star, str(star), 0, 0)
        Universe.add_loose_star(star, star.neighbourhood_id)
        if star.neighbourhood_id is not None:
            self.button_group.add(button, layer=star.neighbourhood_id)
        else:
            self.button_group.add(button, layer=Universe.nei().id)

        self.selected_proto = None
        if star not in self.stars:
            self.stars.append(star)
        if self.is_visible:
            self.sort_buttons(self.star_buttons)
        self.current.erase()
        self.button_add.disable()
        return button

    def del_button(self, star):
        button = [i for i in self.star_buttons if i.object_data == star][0]
        self.button_group.remove(button)
        button.kill()
        if self.is_visible:
            self.sort_buttons(self.star_buttons)
        self.button_del.disable()
        self.stars.remove(button.object_data)
        list_of_dicts = [{'class': star.cls, 'idx': star.idx}]
        Universe.nei().add_proto_stars(list_of_dicts)
        self.potential_stars.show()
        Universe.remove_astro_obj(star)
        Universe.remove_loose_star(star, star.neighbourhood_id)

    def show_current_set(self, new_id):
        for button in self.button_group.widgets():
            button.hide()

        for button in self.button_group.get_widgets_from_layer(new_id):
            button.show()

        self.sort_buttons(self.star_buttons)

    def clear(self):
        self.deselect_buttons()
        self.button_del.disable()
        self.button_add.disable()
        self.true_color_block.erase()
        self.peak_light_block.erase()
        if self.selected_proto is not None:
            self.current.unset_star(self.selected_proto)
        self.potential_stars.deselect_all()

    def select_one(self, btn):
        for button in self.star_buttons:
            button.deselect()
        btn.select()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if event.data['button'] == 1:
                super().on_mousebuttondown(event)

            elif event.data['button'] in (4, 5):
                buttons = self.star_buttons
                if self.area_buttons.collidepoint(event.data['pos']) and len(buttons):
                    last_is_hidden = not buttons[-1].is_visible
                    first_is_hidden = not buttons[0].is_visible
                    if event.data['button'] == 4 and first_is_hidden:
                        self.curr_y += 32
                    elif event.data['button'] == 5 and last_is_hidden:
                        self.curr_y -= 32
                    self.sort_buttons(self.star_buttons)

    def on_mousebuttonup(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.age_bar.on_mousebuttonup(event)

    def update(self):
        self.add_on_exit = len(self.stars) == 1

        current = Universe.nei()
        if current is not None and current.id != self.last_id:
            self.last_id = current.id
            self.show_current_set(current.id)

    def name_current(self, event):
        if event.data['object'] in self.stars:
            star = event.data['object']
            star.set_name(event.data['name'])

    def hold_proto(self, proto):
        self.selected_proto = proto

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


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

    def set_star(self, star_data, inactive=False):
        if 'neighbourhood_id' not in star_data:
            neighbourhood = Universe.nei()
            star_data.update({'neighbourhood_id': neighbourhood.id})
        else:
            n_id = star_data['neighbourhood_id']
            neighbourhood = Universe.current_galaxy.get_neighbourhood(n_id)

        star = Star(star_data)

        if neighbourhood is not None:
            protos = [s for s in neighbourhood.proto_stars if s.cls == star.cls]
            assert len(protos), f"You are not building\nthe star correctly.\n\nCheck it's mass."
            proto = protos.pop(0)
            star.idx = proto.idx
            neighbourhood.proto_stars.remove(proto)
            Universe.add_astro_obj(star)

            self.parent.hold_proto(proto)
            if not inactive:
                self.parent.button_add.set_link(proto)
                self.parent.button_add.enable()
                self.current = star
                self.fill()
                self.toggle_habitable()
                self.parent.age_bar.cursor.set_x(star)
            return star

    def unset_star(self, proto):
        Universe.nei().proto_stars.append(proto)
        Universe.remove_astro_obj(self.current)
        self.current = None

    def destroy_button(self):
        self.parent.del_button(self.current)
        self.erase()

    def show_current(self, star):
        self.erase()
        self.current = star
        self.parent.age_bar.cursor.set_x(star)
        self.parent.true_color_block.create(star, 'true')
        self.parent.peak_light_block.create(star, 'peak')
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.parent.clear()
            self.erase()

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
        # system = Systems.get_current()
        # if system is not None:
        #     system.update()

        self.parent.age_bar.enable()
        self.parent.enable()

    def set_age(self, age_percent):
        if self.has_values:
            self.current.set_age(age_percent)
            # system = Systems.get_system_by_star(self.current)
            # if system is not None:
            #     system.age = self.current.age
            self.fill()

    # def propagate_age_changes(self): # WORK IN PROGRESS
    #     system = Systems.get_system_by_star(self.current)
    #     if system is not None:
    #         for astrobody in system.astro_bodies:
    #             astrobody.update_everything(system.age)


class AddStarButton(TextButton):
    linked_astro = None

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Add Star', x, y)
        self.rect.right = x

    def set_link(self, astro=None):
        """Without arguments, unlinks completely.
        With an argument, it links that argument instead."""
        self.linked_astro = astro

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and self.parent.current.has_values and event.origin == self:
            self.trigger()

    def trigger(self):
        star = self.parent.current.current
        if self.linked_astro is not None:
            self.parent.potential_stars.delete_objects(self.linked_astro)
        self.parent.add_button(star)
        self.disable()


class DelStarButton(TextButton):
    current = None

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Del Star', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if self.enabled and event.data['button'] == 1 and event.origin == self:
            self.parent.current.destroy_button()


class StarButton(ColoredBody):
    enabled = True

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if event.data['button'] == 1:
                self.parent.show_current(self.object_data)
                self.parent.parent.select_one(self)
                self.parent.parent.button_del.enable()
                self.parent.toggle_habitable()
            elif event.data['button'] in (4, 5):
                self.parent.parent.on_mousebuttondown(event)


class AgeBar(BaseSlider):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 401)
        self.cursor = AgeCursor(self, self.rect.centery)
        draw.aaline(self.image, COLOR_TEXTO, [184, 0], [184, 7])

    def show(self):
        super().show()
        if self.parent.current.has_values:
            self.cursor.show()


class AgeCursor(BaseCursor):

    def on_mousebuttonup(self, event):
        super().on_mousebuttonup(event)
        # if event.data['button'] == 1 and event.origin == self:
        #     self.parent.parent.current.propagate_age_changes()

    def on_movement(self, x: int):
        self.parent.parent.current.set_age((x - 50) / 400)

    def set_x(self, star):
        age = round(star.age.m / star.lifetime.to('years').m, 3)
        self.rect.x = round(age * (self.parent.rect.w - 1)) + self.parent.rect.x

    def update(self):
        super().update()
        if self.pressed:
            self.on_movement(self.rect.x)


class ListedStar(ColoredBody):
    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            text = 'To create this star, input a mass '
            if self.object_data.cls.startswith('O'):
                text += 'of 16 solar masses or more.'
            elif self.object_data.cls.startswith('B'):
                text += 'between 2.1 and 16 solar masses.'
            elif self.object_data.cls.startswith('A'):
                text += 'between 1.4 and 2.1 solar masses.'
            elif self.object_data.cls.startswith('F'):
                text += 'between 1.04 and 1.4 solar masses.'
            elif self.object_data.cls.startswith('G'):
                text += 'between 0.8 and 1.04 solar masses.'
            elif self.object_data.cls.startswith('K'):
                text += 'between 0.45 and 0.8 solar masses.'
            elif self.object_data.cls.startswith('M'):
                text += 'between 0.08 and 0.45 solar masses.'
            self.parent.select_one(self)
            raise AssertionError(text)


class PotentialStars(ListedArea):
    listed_type = ListedStar
    name = 'Potential Stars'

    def show(self):
        super().show()
        self.clear()
        if Universe.current_galaxy is not None:
            for neighbourhood in Universe.current_galaxy.stellar_neighbourhoods:
                pop = [star for star in neighbourhood.proto_stars]
                self.populate(pop, layer=neighbourhood.id)

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
        neighbourhood = None
        if Universe.current_galaxy is not None:
            neighbourhood = Universe.nei()
        idx = -1 if neighbourhood is None else neighbourhood.id
        if idx != self.last_id:
            self.last_id = idx
        self.show_current(self.last_id)


class AutomaticButton(TextButton):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent, '[Auto]', x, y, font_size=10)
        self.rect.centery = y

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            nei = Universe.nei()
            proto_stars = nei.proto_stars.copy()
            for proto in proto_stars:
                mass = round(roll(proto.min_mass, proto.max_mass), 3)
                self.parent.current.set_star({'mass': mass, 'neighbourhood_id': nei.id})
                self.parent.button_add.trigger()
                Renderer.update()


class ColorBlock(Meta):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent)
        render = self.write3(text, self.crear_fuente(10), 65, j=1)
        image = Surface((32, 16))
        canvas = Surface((80, image.get_height() + render.get_height() + 15), SRCALPHA)
        canvas_rect = canvas.get_rect()

        self.sp_f = self.crear_fuente(10)
        ultraviolet = self.write3('ULTRA-VIOLET', self.sp_f, 80, j=1)

        self.image_rect = image.get_rect(centerx=canvas_rect.centerx, y=0)
        self.render_rect = render.get_rect(centerx=canvas_rect.centerx, top=image.get_height() + 1)
        self.no_color_rect = ultraviolet.get_rect(centerx=canvas_rect.centerx, top=self.render_rect.bottom + 1)

        self.color_image = image
        self.text_rect = render
        self.image = canvas
        self.rect = image.get_rect(**kwargs)

    def create(self, star, light='true'):
        color = None
        if light == 'true':
            color = star.light_color
        elif light == 'peak':
            spectrum = star.peak_light.spectrum
            if spectrum == 'VISIBLE':
                color = star.peak_light.color
                self.image.fill(COLOR_BOX, self.no_color_rect)
            else:
                color = Color('black' if spectrum == 'INFRARED' else 'white')
                spectrum_render = self.write3(spectrum, self.sp_f, self.rect.w + 50, j=1)
                spectrum_rect = spectrum_render.get_rect(x=self.no_color_rect.x, y=self.no_color_rect.y)
                self.image.blit(spectrum_render, spectrum_rect)

        self.color_image.fill((color.r, color.g, color.b))
        self.image.blit(self.color_image, self.image_rect)
        self.image.blit(self.text_rect, self.render_rect)

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self):
        self.image.fill(COLOR_BOX)

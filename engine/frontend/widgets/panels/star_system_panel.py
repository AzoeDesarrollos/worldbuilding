from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_TEXTO, Group
from engine.frontend.widgets.basewidget import BaseWidget
from .common import ListedArea, ColoredBody, TextButton
from engine.backend import EventHandler, Systems
from engine.equations.binary import system_type
from engine.equations.space import Universe
from ..values import ValueText
from pygame import Surface
from random import choice


class StarSystemPanel(BaseWidget):
    selected = None
    skip = False
    skippable = True

    show_swap_system_button = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Star System'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.properties = Group()
        self.stars_area = AvailableStars(self, ANCHO - 200, 32, 200, 340)

        self.current = SystemType(self)

        self.systems = []
        self.setup_button = SetupButton(self, 484, 416)
        self.dissolve_button = DissolveButton(self, 334, 416)
        self.undo_button = UndoButton(self, 234, 416)
        self.properties.add(self.setup_button, self.dissolve_button, self.undo_button, self.stars_area, self.current)
        self.system_buttons = Group()
        EventHandler.register(self.save_systems, 'Save')
        EventHandler.register(self.load_systems, 'LoadData')
        EventHandler.register(self.name_current, 'NameObject')

        f = self.crear_fuente(14, underline=True)
        self.write('Systems', f, COLOR_AREA, x=3, y=420)

        self.remaining = ValueText(self, 'Binary Pairs remaining', 3, self.area_buttons.top - 50, size=14)
        self.properties.add(self.remaining)

        self.discarded_protos = []

    def name_current(self, event):
        if event.data['object'] in self.systems:
            system = event.data['object']
            system.set_name(event.data['name'])

    def set_current(self, system_data):
        self.current.reset(system_data)

    def show_current(self, star):
        self.current.erase()
        self.current.current = star
        self.current.reset(star)

    def create_button(self, system_data):
        binary_systems = [system for system in Universe.systems if system.composition == 'binary']
        if len(binary_systems):
            chosen = choice(binary_systems)
            Universe.systems.remove(chosen)
            self.discarded_protos.append(chosen)
            system_data.position = chosen.location
            Universe.current_galaxy.current_neighbourhood.quantities['Binary'] -= 1

        if system_data not in self.systems:
            idx = len([s for s in self.systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, self.curr_x, self.curr_y)
            self.systems.append(system_data)
            self.system_buttons.add(button)
            self.properties.add(button)
            Systems.set_system(system_data)
            Universe.current_galaxy.current_neighbourhood.add_true_system(system_data)
            self.current.enable()
            self.load_universe_data()
            return button

    @staticmethod
    def save_systems(event):
        data = {}
        systems = Systems.get_systems()
        for system in [s.star_system for s in systems if s.is_a_system and s.star_system.letter is not None]:
            if system.celestial_type == 'system':
                d = {
                    'primary': system.primary.id,
                    'secondary': system.secondary.id,
                    'avg_s': system.average_separation.m,
                    'ecc_p': system.ecc_p.m,
                    "ecc_s": system.ecc_s.m,
                    "name": system.name,
                    "position": dict(zip(['x', 'y', 'z'], system.position)),
                    "neighbourhood_id": Universe.current_galaxy.current_neighbourhood.id
                }
                data[system.id] = d

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Binary Systems': data})

    def load_universe_data(self):
        binary_systems = Universe.current_galaxy.current_neighbourhood.quantities['Binary']
        self.remaining.value = str(binary_systems)

    def load_systems(self, event):
        for id in event.data['Binary Systems']:
            system_data = event.data['Binary Systems'][id]
            avg_s = system_data['avg_s']
            ecc_p = system_data['ecc_p']
            ecc_s = system_data['ecc_s']
            prim = Systems.get_star_by_id(system_data['primary'])
            scnd = Systems.get_star_by_id(system_data['secondary'])
            Systems.remove_star(prim)
            Systems.remove_star(scnd)
            name = system_data['name']
            x = system_data['position']['x']
            y = system_data['position']['y']
            z = system_data['position']['z']

            system = system_type(avg_s)(prim, scnd, avg_s, ecc_p, ecc_s, id=id, name=name)
            system.position = x, y, z
            Universe.add_astro_obj(system)

            button = self.create_button(system)
            button.hide()

    def create_systems(self):
        triple_systems = Universe.current_galaxy.current_neighbourhood.quantities['Triple']
        multiple_systems = Universe.current_galaxy.current_neighbourhood.quantities['Multiple']
        if triple_systems == 0 and multiple_systems == 0:
            widgets = self.stars_area.listed_objects.widgets()
            singles = [system for system in Universe.systems if system.composition == 'single']
            stars = [s.object_data for s in widgets if s.object_data.celestial_type == 'star']
            if len(singles):
                for star in stars:
                    try:
                        chosen = choice(singles)
                        singles.remove(chosen)
                        Universe.remove_astro_obj(chosen)
                        star.position = chosen.location
                        Systems.set_system(star)
                        Universe.current_galaxy.current_neighbourhood.add_true_system(star)
                    except IndexError as error:
                        raise AssertionError(error)

            self.parent.set_skippable('Multiple Stars', True)

    def select_one(self, btn):
        for button in self.system_buttons.widgets():
            button.deselect()
        btn.select()

    def del_button(self, system):
        button = [i for i in self.system_buttons.widgets() if i.object_data == system][0]
        self.systems.remove(system)
        self.system_buttons.remove(button)
        self.sort_buttons(self.system_buttons.widgets())
        self.properties.remove(button)
        self.dissolve_button.disable()
        if system in self.systems:
            Systems.dissolve_system(system)

    def show(self):
        self.parent.swap_neighbourhood_button.unlock()
        if Universe.current_galaxy is not None:
            for system in Universe.current_galaxy.current_neighbourhood.systems:
                self.create_button(system)
            self.load_universe_data()
        self.sort_buttons(self.system_buttons.widgets())
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        if Universe.current_galaxy is not None:
            self.create_systems()
        for prop in self.properties.widgets():
            prop.hide()

    def transfer_proto_system(self, discarded):
        proto = [sys for sys in self.discarded_protos if sys.location == discarded.position]
        if len(proto):
            proto = proto.pop()
        else:
            raise ValueError(f'{discarded} has an invalid location.')
        Universe.systems.append(proto)
        self.discarded_protos.remove(proto)
        self.load_universe_data()


class SystemType(BaseWidget):
    locked = False
    has_values = False
    current = None

    primary = None
    secondary = None
    separation = None
    ecc_p = None
    ecc_s = None

    def __init__(self, parent, props=None):
        super().__init__(parent)
        self.properties = Group()

        if props is None:
            props = [
                'Primary Star', 'Secondary Star', 'Average Separation',
                'Eccentriciy (primary)', 'Eccentricty (secondary)',
                'Barycenter', 'Maximun Separation', 'Minimun Separation',
                'Forbbiden Zone Inner edge', 'Forbbiden Zone Outer edge',
                'System Type', 'System Name']

        self.create(props)
        EventHandler.register(self.clear, 'ClearData')

    def create(self, props):
        for i, prop in enumerate([j for j in props]):
            vt = ValueText(self, prop, 3, 64 + i * 25, COLOR_TEXTO, COLOR_BOX)
            self.properties.add(vt, layer=2)
            if i in [2, 3, 4]:
                vt.modifiable = True
            if i in [0, 1]:
                vt.enable()

        attrs = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        for idx, attr in enumerate(attrs):
            setattr(self, attr, self.properties.get_widget(idx))

    def set_bodies(self, obj):
        if str(self.primary.value) == '':
            self.primary.value = obj
            self.has_values = True
        else:
            self.secondary.value = obj
            self.has_values = True

        self.parent.undo_button.enable()

        if obj in Systems.loose_stars:
            Systems.loose_stars.remove(obj)

        if self.primary.value != '' and self.secondary.value != '':
            for obj in self.properties.get_widgets_from_layer(2):
                obj.enable()

    def unset_stars(self):
        self.parent.stars_area.populate(Systems.loose_stars, layer='one')
        self.erase()

    def get_determinants(self):
        names = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        dets = [self.primary.value, self.secondary.value]
        return dets + [float(getattr(self, name).value) for name in names if name not in ('primary', 'secondary')]

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                self.current = system_type(self.separation.value)(*self.get_determinants())
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep',
                     'min_sep', 'inner_forbbiden_zone', 'outer_forbbiden_zone', 'system_name', 'name']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            self.parent.setup_button.enable()

    def reset(self, system_data):
        self.set_bodies(system_data.primary)
        self.set_bodies(system_data.secondary)
        self.separation.value = system_data.average_separation
        self.ecc_p.value = system_data.ecc_p
        self.ecc_s.value = system_data.ecc_s
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self):
        for button in self.properties.widgets():
            button.text_area.clear()
        self.has_values = False
        self.current = None

    def destroy(self):
        self.parent.transfer_proto_system(self.current)
        self.parent.del_button(self.current)
        self.erase()

    def show(self):
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        for prop in self.properties.widgets():
            prop.hide()

    def enable(self):
        super().enable()
        for arg in self.properties.widgets():
            arg.enable()

    def disable(self):
        for arg in self.properties.widgets():
            arg.disable()
        super().disable()


class ListedStar(ColoredBody):
    enabled = True

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.parent.parent.current.set_bodies(self.object_data)
            self.parent.remove_listed(self)
            self.kill()
            self.parent.sort()

    def move(self, x, y):
        self.rect.topleft = x, y

    def __repr__(self):
        return f'Listed: {str(self.object_data)}'


class AvailableStars(ListedArea):
    name = 'Stars'
    listed_type = ListedStar

    def show(self):
        self.clear()
        self.populate(Systems.loose_stars, layer='one')
        super().show()

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
        self.show_current('one')


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            sistema = self.parent.current.current
            self.parent.create_button(sistema)
            self.parent.current.erase()
            self.parent.sort_buttons(self.parent.system_buttons.widgets())
            self.disable()


class DissolveButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Dissolve System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            system = self.parent.current.current
            Systems.dissolve_system(system)
            self.parent.stars_area.show()
            self.parent.current.destroy()


class SystemButton(ColoredBody):
    enabled = True

    def __init__(self, parent, system_data, idx, x, y):
        system_data.idx = idx
        super().__init__(parent, system_data, str(system_data), x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            if self.object_data.letter is not None:
                self.parent.show_current(self.object_data)
            else:
                self.parent.current.current = self.object_data
            self.parent.setup_button.disable()
            self.parent.select_one(self)
            if hasattr(self.parent, 'dissolve_button'):
                self.parent.dissolve_button.enable()


class UndoButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Undo'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if self.enabled and event.data['button'] == 1 and event.origin == self:
            self.parent.current.unset_stars()
            self.disable()

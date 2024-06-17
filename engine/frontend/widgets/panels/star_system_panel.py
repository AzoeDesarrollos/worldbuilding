from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_TEXTO, Group
from engine.frontend.widgets.basewidget import BaseWidget
from .common import ListedArea, ColoredBody, TextButton
from engine.equations.system_binary import system_type
from engine.backend import EventHandler, roll, q
from engine.equations.space import Universe
from pygame import Surface, mouse
from ..values import ValueText
from random import choice


class StarSystemPanel(BaseWidget):
    selected = None
    skip = False
    skippable = True

    show_swap_system_button = False

    quantity = None

    last_id = -1

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
        self.auto_button = AutomaticSystemDataButton(self, ANCHO - 260, 133)
        self.properties.add(self.setup_button, self.dissolve_button, self.undo_button,
                            self.stars_area, self.current, self.auto_button)
        self.system_buttons = Group()
        EventHandler.register(self.save_systems, 'Save')
        EventHandler.register(self.hold_loaded_bodies, 'LoadBinary')
        EventHandler.register(self.name_current, 'NameObject')
        EventHandler.register(self.export_data, 'ExportData')

        f = self.crear_fuente(14, underline=True)
        self.write('Systems', f, COLOR_AREA, x=3, y=420)

        self.remaining = ValueText(self, 'Binary Pairs remaining', 3, self.area_buttons.top - 50, size=14)
        self.properties.add(self.remaining)

        self.discarded_protos = []
        self.held_data = {}

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

    def create_button(self, system_data, new=False):
        nei = Universe.current_galaxy.get_neighbourhood(system_data.neighbourhood_id)
        binary_systems = [system for system in nei.proto_systems if system.composition == 'binary']
        if len(binary_systems) and system_data not in self.systems:
            if new is False:
                chosen = [proto for proto in binary_systems if proto.id == system_data.id].pop(0)
            else:
                chosen = binary_systems.pop(0)
            nei.remove_proto_system(chosen)
            self.discarded_protos.append(chosen)
            system_data.cartesian = chosen.location
            offset = nei.location
            system_data.set_orbit(offset)
            nei.quantities['Binary'] -= 1
            Universe.add_astro_obj(system_data)

            idx = len([s for s in self.systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, self.curr_x, self.curr_y)
            self.systems.append(system_data)
            self.system_buttons.add(button, layer=system_data.neighbourhood_id)
            # self.properties.add(button)
            nei.add_true_system(system_data)
            self.current.enable()
            if self.is_visible:
                self.sort_buttons(self.system_buttons.get_widgets_from_layer(system_data.neighbourhood_id))
            return button

    @staticmethod
    def save_systems(event):
        data = {}
        systems = []
        if Universe.nei() is not None:
            # this evades a crash when saving an empty panel.
            systems = [s for s in Universe.nei().true_systems]

        for system in systems:
            if system.celestial_type == 'system' and system.system_number not in ('single', None):
                data[system.id] = {
                    'primary': system.primary.id,
                    'secondary': system.secondary.id,
                    'avg_s': system.average_separation.m,
                    'ecc_p': system.ecc_p.m,
                    "ecc_s": system.ecc_s.m,
                    "name": system.name,
                    "position": dict(zip(['x', 'y', 'z'], system.cartesian)),
                    "neighbourhood_id": Universe.nei().id,
                    "flagged": system.flagged,
                }

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Binary Systems': data})

    def load_universe_data(self, nei=None):
        if nei is None:
            nei = Universe.nei()
        binary_systems = nei.quantities['Binary']
        self.quantity = binary_systems
        self.remaining.value = f'{self.quantity}'

    def hold_loaded_bodies(self, event):
        if 'Binary Systems' in event.data and len(event.data['Binary Systems']):
            self.held_data.update(event.data['Binary Systems'])

    def show_systems(self):
        for id in self.held_data:
            system_data = self.held_data[id]
            nei = Universe.current_galaxy.get_neighbourhood(system_data['neighbourhood_id'])
            self.load_universe_data(nei)

            prim = Universe.get_astrobody_by(system_data['primary'], 'id')
            scnd = Universe.get_astrobody_by(system_data['secondary'], 'id')

            if self.check_system(prim_scnd=[prim, scnd]):
                Universe.remove_loose_star(prim, nei.id)
                Universe.remove_loose_star(scnd, nei.id)
                avg_s = system_data['avg_s']
                ecc_p = system_data['ecc_p']
                ecc_s = system_data['ecc_s']

                name = system_data['name']
                system = system_type(avg_s)(prim, scnd, avg_s, ecc_p, ecc_s, id=id, name=name, nei_id=nei.id)
                Universe.add_astro_obj(system)

                button = self.create_button(system)
                if button is not None:
                    button.hide()

    def select_one(self, btn):
        for button in self.system_buttons.widgets():
            button.deselect()
        btn.select()

    def del_button(self, system):
        button = [i for i in self.system_buttons.widgets() if i.object_data == system][0]
        self.systems.remove(system)
        self.system_buttons.remove(button)
        self.sort_buttons(self.system_buttons.get_widgets_from_layer(self.last_id))
        self.dissolve_button.disable()
        Universe.nei().quantities['Binary'] += 1

        button.kill()
        EventHandler.trigger('DissolveSystem', self, {'system': system, 'nei': Universe.nei().id})

    @staticmethod
    def check_system(sstm=None, prim_scnd=None):
        """Se asegura de que los componentes del sistema sean dos estrellas individuales.
        Puede chequear un sistema ya creado o dos componentes estelares aternativamente."""
        if sstm is not None:
            if sstm.letter is not None:
                prim = sstm.primary
                scnd = sstm.secondary
            else:
                return False
        elif prim_scnd is not None:
            prim, scnd = prim_scnd
        else:
            return False
        if prim is not None and scnd is not None:
            return prim.celestial_type != 'system' and scnd.celestial_type != 'system'
        else:
            return False

    def show(self):
        self.parent.swap_neighbourhood_button.unlock()
        self.show_systems()
        if Universe.current_galaxy is not None:
            for system in Universe.nei().true_systems:
                if self.check_system(sstm=system):
                    self.create_button(system)
            self.load_universe_data()

        super().show()
        for prop in self.properties.widgets():
            prop.show()
        self.sort_buttons(self.system_buttons.get_widgets_from_layer(self.last_id))

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()
        for button in self.system_buttons.widgets():
            button.hide()

    def transfer_proto_system(self, discarded):
        proto = [sys for sys in self.discarded_protos if sys.location == discarded.cartesian]
        if len(proto):
            proto = proto.pop(0)
        else:
            raise ValueError(f'{discarded} has an invalid location.')
        Universe.nei().add_proto_system(proto)
        self.discarded_protos.remove(proto)

    def show_current_set(self, new_id):
        for button in self.system_buttons.widgets():
            button.hide()
        for button in self.system_buttons.get_widgets_from_layer(new_id):
            button.show()

        self.sort_buttons(self.system_buttons.get_widgets_from_layer(new_id))

    def update(self):
        current = Universe.nei()
        if current is not None:
            self.load_universe_data()
            if current.id != self.last_id:
                self.last_id = current.id
                self.stars_area.reset_offset()
                self.show_current_set(current.id)

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


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
        elif str(self.secondary.value) == '':
            self.secondary.value = obj
            self.has_values = True
        else:
            old_value = self.secondary.value
            self.replace_secondary(old_value, obj)
            self.secondary.value = obj
            self.has_values = True

        self.parent.undo_button.enable()

        Universe.remove_loose_star(obj, self.parent.last_id)

        if self.primary.value != '' and self.secondary.value != '':
            for obj in self.properties.get_widgets_from_layer(2):
                obj.enable()
            if not self.has_values:
                x, y = self.parent.auto_button.rect.center
                mouse.set_pos(x, y)

            if hasattr(self.parent, 'auto_button'):
                self.parent.auto_button.enable()

    def unset_stars(self):
        self.parent.stars_area.clear()
        if self.primary.value != '':
            Universe.add_loose_star(self.primary.value, self.parent.last_id)
        if self.secondary.value != '':
            Universe.add_loose_star(self.secondary.value, self.parent.last_id)
        stars = Universe.get_loose_stars(self.parent.last_id)
        self.parent.stars_area.populate(stars, layer=self.parent.last_id)
        self.erase()

    def replace_secondary(self, replaced_star, replacement):
        Universe.remove_loose_star(replacement, self.parent.last_id)
        Universe.add_loose_star(replaced_star, self.parent.last_id)

        stars = Universe.get_loose_stars(self.parent.last_id)
        self.parent.stars_area.clear()
        self.parent.stars_area.populate(stars, layer=self.parent.last_id)

    def get_determinants(self):
        names = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        dets = [self.primary.value, self.secondary.value]
        return dets + [float(getattr(self, name).value) for name in names if name not in ('primary', 'secondary')]

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                x = Universe.nei().id
                self.current = system_type(self.separation.value)(*self.get_determinants(), nei_id=x)
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
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            self.parent.remove_listed(self)
            self.parent.parent.current.set_bodies(self.object_data)
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
        if Universe.current_galaxy is not None:
            for nei in Universe.current_galaxy.stellar_neighbourhoods:
                stars = [star for star in Universe.get_loose_stars(nei.id)]
                self.populate(stars, layer=nei.id)
        super().show()

    def update(self):
        if Universe.current_galaxy is not None:
            if self.parent.quantity < 1:
                self.disable_by_type('star')
            else:
                self.enable_all()

            self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))

            if Universe.nei().id != self.last_id:
                self.last_idx = Universe.nei().id
            self.show_current(Universe.nei().id)


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            sistema = self.parent.current.current
            self.parent.create_button(sistema, new=True)
            self.parent.undo_button.disable()
            self.parent.current.erase()
            buttons = self.parent.system_buttons.get_widgets_from_layer(self.parent.last_id)
            self.parent.sort_buttons(buttons)
            self.disable()


class DissolveButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Dissolve System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            # system = self.parent.current.current
            # Systems.dissolve_system(system)
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
            self.parent.auto_button.disable()
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


class AutomaticSystemDataButton(TextButton):

    def __init__(self, parent, x, y, set_choice=None, factor=1):
        super().__init__(parent, '[Auto]', x, y)
        self.chosen = set_choice
        self.factor = factor

    def on_mousebuttondown(self, event):
        if self.enabled and event.data['button'] == 1 and event.origin == self:
            choices = ['S', 'P']
            if self.chosen is None:
                letter = choice(choices)
            else:
                letter = self.chosen
            if letter == 'P':
                min_a = 0.15 * self.factor
                max_a = 6 * self.factor
            else:
                min_a = 120 * self.factor
                max_a = 600 * self.factor
            a = round(roll(min_a, max_a), 3)
            e_1 = roll(0.4, 0.7)
            e_2 = roll(0.4, 0.7)

            a_widget = self.parent.current.properties.get_widget(2)
            e1_widget = self.parent.current.properties.get_widget(3)
            e2_widget = self.parent.current.properties.get_widget(4)

            a_widget.value = q(a, "EU")
            e1_widget.value = q(e_1)
            e2_widget.value = q(e_2)
            self.parent.current.fill()
            self.disable()
            x, y = self.parent.setup_button.rect.center
            mouse.set_pos(x, y)


AutoButton = AutomaticSystemDataButton

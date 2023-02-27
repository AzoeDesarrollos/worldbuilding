from .star_system_panel import SystemType, UndoButton, SetupButton, SystemButton, DissolveButton
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, Group
from engine.frontend.widgets.panels.common import ListedBody, ListedArea
from engine.backend import EventHandler, Systems
from engine.equations.binary import system_type
from engine.equations.space import Universe
from ..basewidget import BaseWidget
from ..values import ValueText
from pygame import Surface
from random import choice


class MultipleStarsPanel(BaseWidget):
    skippable = True
    skip = False

    curr_x = 0
    curr_y = 440

    show_swap_system_button = False

    _triple = 0
    _multiple = 0

    def __init__(self, parent):
        self.name = 'Multiple Stars'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()

        self.stars_area = AvailableSystems(self, ANCHO - 200, 32, 200, 340)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        f = self.crear_fuente(14, underline=True)
        self.write('Subsystems', f, COLOR_AREA, x=3, y=420)

        self.system_buttons = Group()

        self.systems = []
        self.current = SystemsType(self)
        self.undo_button = UndoButton(self, 234, 416)
        self.setup_button = SetupButton(self, 484, 416)
        self.dissolve_button = DissolveButton(self, 334, 416)
        self.properties.add(self.current, self.stars_area, self.undo_button, self.setup_button, self.dissolve_button)
        EventHandler.register(self.name_current, 'NameObject')

        t = " Systems remaining"
        self.triple_remaining = ValueText(self, 'Triple Star' + t, 3, self.area_buttons.top - 70, size=14)
        self.multiple_remaining = ValueText(self, 'Multiple Star' + t, 3, self.area_buttons.top - 50, size=14)
        self.properties.add(self.triple_remaining, self.multiple_remaining)

        self.discarded_protos = []

        EventHandler.register(self.save_systems, 'Save')
        EventHandler.register(self.load_systems, 'LoadData')
        EventHandler.register(self.name_current, 'NameObject')

    def load_universe_data(self):
        triple_systems = Universe.current_galaxy.current_neighbourhood.quantities['Triple']
        multiple_systems = Universe.current_galaxy.current_neighbourhood.quantities['Multiple']
        self.triple_remaining.value = str(triple_systems)
        self.multiple_remaining.value = str(multiple_systems)
        self._triple = triple_systems
        self._multiple = multiple_systems

    def name_current(self, event):
        if event.data['object'] in self.systems:
            system = event.data['object']
            system.set_name(event.data['name'])

    def create_button(self, system_data):
        self.parent.properties.widgets()[1].enable()
        triple_systems = [system for system in Universe.systems if system.composition == 'triple']
        multiple_systems = [system for system in Universe.systems if system.composition == 'multiple']
        primary = system_data.primary
        secondary = system_data.secondary
        chosen, kind = None, None
        if primary.celestial_type == 'system' and secondary.celestial_type == 'star':
            chosen = choice(triple_systems)
            kind = 'Triple'
        elif primary.celestial_type == 'system' and secondary.celestial_type == 'system':
            chosen = choice(multiple_systems)
            kind = 'Multiple'
        elif primary.celestial_type == 'star' and secondary.celestial_type == 'system':
            chosen = choice(triple_systems)
            kind = 'Triple'
        assert chosen is not None, "System is nonsensical"
        Universe.systems.remove(chosen)
        system_data.position = chosen.location
        Universe.current_galaxy.current_neighbourhood.quantities[kind] -= 1
        self.discarded_protos.append(chosen)
        if system_data not in self.systems:
            idx = len([s for s in self.systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, self.curr_x, self.curr_y)
            self.systems.append(system_data)
            self.system_buttons.add(button)
            self.properties.add(button)
            self.sort_buttons(self.system_buttons.widgets())
            Systems.set_system(system_data)
            Universe.current_galaxy.current_neighbourhood.add_true_system(system_data)
            self.current.enable()
            self.load_universe_data()
            return button

    def show_current(self, star):
        self.current.erase()
        self.current.current = star
        self.current.reset(star)

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
        super().show()
        for prop in self.properties.widgets():
            prop.show()
        self.parent.swap_neighbourhood_button.unlock()
        if Universe.current_galaxy is not None:
            self.load_universe_data()

    def create_systems(self):
        lock = False
        widgets = self.stars_area.listed_objects.widgets()
        singles = [system for system in Universe.systems if system.composition == 'single']
        stars = [s.object_data for s in widgets if s.object_data.celestial_type == 'star']
        binaries = [s.object_data for s in widgets if s.object_data.celestial_type != 'star']
        if len(singles):
            for star in stars:
                try:
                    chosen = choice(singles)
                    singles.remove(chosen)
                    Universe.remove_astro_obj(chosen)
                    star.position = chosen.location
                    Systems.set_system(star)
                    Universe.current_galaxy.current_neighbourhood.add_true_system(star)
                    lock = True

                except IndexError:
                    self.parent.properties.widgets()[1].disable()
                    self.parent.curr_idx -= 1
                    total = self._triple + self._multiple
                    verb = "s" if total == 1 else 're'
                    pl = '' if total == 1 else 's'
                    warning = f"Complete the systems before continuing.\n\nThere'{verb} {total} system{pl} left."
                    raise AssertionError(warning)

        for other in binaries:
            Systems.set_system(other)

        if lock:
            self.parent.swap_neighbourhood_button.lock()

    def hide(self):
        self.create_systems()
        super().hide()
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

    def save_systems(self, event):
        data = {}
        for system in self.systems:
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

        if len(data):
            # so it doesn't save an empty dictionary.
            EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Binary Systems': data})

    def load_systems(self, event):
        for id in event.data['Binary Systems']:
            system_data = event.data['Binary Systems'][id]

            prim = Universe.get_astrobody_by(system_data['primary'], 'id')
            scnd = Universe.get_astrobody_by(system_data['secondary'], 'id')
            go_on = prim.celestial_type == 'star' and scnd.celestial_type == 'system'
            go_on = go_on or prim.celestial_type == 'system' and scnd.celestial_type == 'system'
            go_on = go_on or prim.celestial_type == 'system' and scnd.celestial_type == 'star'

            if go_on:
                avg_s = system_data['avg_s']
                ecc_p = system_data['ecc_p']
                ecc_s = system_data['ecc_s']
                name = system_data['name']
                x = system_data['position']['x']
                y = system_data['position']['y']
                z = system_data['position']['z']

                system = system_type(avg_s)(prim, scnd, avg_s, ecc_p, ecc_s, id=id, name=name)
                system.position = x, y, z

                button = self.create_button(system)
                button.hide()


class SystemsType(SystemType):

    def __init__(self, parent):
        props = [
            'Primary System', 'Secondary System', 'Average Separation',
            'Eccentriciy (primary)', 'Eccentricty (secondary)', 'Barycenter',
            'Maximun Separation', 'Minimun Separation', 'System Name']
        super().__init__(parent, props)
        # avg_sep = 1200 and 60000 au
        # ecc = between 0.4 and 0.7

    def set_star(self, star):
        if str(self.primary.value) == '':
            self.primary.value = star
            self.has_values = True
        else:
            self.secondary.value = star
            self.parent.undo_button.enable()
            self.has_values = True

        if self.primary.value != '' and self.secondary.value != '':
            for obj in self.properties.get_widgets_from_layer(2):
                obj.enable()

    def unset_stars(self):
        self.parent.stars_area.repopulate()
        self.erase()

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                self.current = system_type(self.separation.value)(*self.get_determinants())
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep', 'min_sep', 'system_name']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            self.parent.setup_button.enable()


class ListedSystem(ListedBody):

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.parent.parent.current.set_star(self.object_data)
            self.parent.remove_listed(self)
            self.kill()
            self.parent.sort()


class AvailableSystems(ListedArea):
    name = 'Systems'
    listed_type = ListedSystem

    def show(self):
        self.repopulate()
        super().show()
        for listed in self.listed_objects.widgets():
            listed.show()

    def repopulate(self):
        population = []
        if Universe.current_galaxy is not None:
            for system in Universe.current_galaxy.current_neighbourhood.systems:
                if system not in population:
                    population.append(system)
        population.extend(Systems.loose_stars)

        if len(population):
            population.sort(key=lambda s: s.mass, reverse=True)
            self.populate(population, layer='two')

    def update(self):
        # this hook is necessary.
        # otherwise the content of the panel is deleted.
        pass

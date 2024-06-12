from .star_system_panel import SystemType, UndoButton, SetupButton, SystemButton, DissolveButton, AutoButton
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, Group
from engine.equations.system_single import SingleSystem
from engine.frontend.widgets.panels.common import ListedBody, ListedArea
from engine.equations.orbit import NeighbourhoodSystemOrbit
from engine.equations.system_binary import system_type
from engine.equations.space import Universe
from engine.backend import EventHandler
from ..basewidget import BaseWidget
from pygame import Surface, mouse
from ..values import ValueText


class MultipleStarsPanel(BaseWidget):
    skippable = True
    skip = False

    curr_x = 0
    curr_y = 440

    show_swap_system_button = False

    _t_quantity = None
    _m_quantity = None

    last_id = -1

    planetary_systems_added = False

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
        self.setup_button = CreateSystemButton(self, 484, 416)
        self.dissolve_button = DissolveButton(self, 334, 416)
        self.auto_button = AutoButton(self, ANCHO - 260, 133, set_choice='S', factor=10)
        self.properties.add(self.current, self.stars_area, self.undo_button,
                            self.setup_button, self.dissolve_button, self.auto_button)
        EventHandler.register(self.name_current, 'NameObject')

        t = " Systems remaining"
        self.triple_remaining = ValueText(self, 'Triple Star' + t, 3, self.area_buttons.top - 70, size=14)
        self.multiple_remaining = ValueText(self, 'Multiple Star' + t, 3, self.area_buttons.top - 50, size=14)
        self.properties.add(self.triple_remaining, self.multiple_remaining)

        self.discarded_protos = []

        EventHandler.register(self.save_systems, 'Save')
        EventHandler.register(self.hold_loaded_bodies, 'LoadBinary')
        EventHandler.register(self.name_current, 'NameObject')
        EventHandler.register(self.export_data, 'ExportData')

        self.held_data = {}

    @property
    def triple(self):
        nei = Universe.nei()
        return nei.quantities['Triple']

    @property
    def multiple(self):
        nei = Universe.nei()
        return nei.quantities['Multiple']

    def load_universe_data(self, nei=None):
        if nei is None:
            nei = Universe.nei()
        triple_systems = nei.quantities['Triple']
        multiple_systems = nei.quantities['Multiple']
        self._t_quantity = triple_systems
        self._m_quantity = multiple_systems
        self.triple_remaining.value = f'{self._t_quantity}'
        self.multiple_remaining.value = f'{self._m_quantity}'

    def name_current(self, event):
        if event.data['object'] in self.systems:
            system = event.data['object']
            system.set_name(event.data['name'])

    def create_button(self, system_data):
        self.parent.properties.widgets()[1].enable()
        nei = Universe.current_galaxy.get_neighbourhood(system_data.neighbourhood_id)
        triple_systems = [system for system in nei.proto_systems if system.composition == 'triple']
        multiple_systems = [system for system in nei.proto_systems if system.composition == 'multiple']

        prim = system_data.primary
        scnd = system_data.secondary
        go_on_1 = prim.celestial_type != 'system' and scnd.celestial_type == 'system'  # triple
        go_on_2 = prim.celestial_type == 'system' and scnd.celestial_type != 'system'  # triple
        go_on_3 = prim.celestial_type == 'system' and scnd.celestial_type == 'system'  # multiple
        chosen = None
        if go_on_1 or go_on_2:
            chosen = triple_systems.pop(0)
            nei.quantities['Triple'] -= 1
        elif go_on_3:
            chosen = multiple_systems.pop(0)
            nei.quantities['Multiple'] -= 1

        assert chosen is not None, "System is nonsensical"
        nei.remove_proto_system(chosen)
        system_data.cartesian = chosen.location
        # system_data.id = chosen.id
        offset = nei.location
        system_data.orbit = NeighbourhoodSystemOrbit(*system_data.cartesian, offset)
        self.discarded_protos.append(chosen)
        Universe.add_astro_obj(system_data)
        if system_data not in self.systems:
            all_systems = set(nei.true_systems + self.systems)
            idx = len([s for s in all_systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, self.curr_x, self.curr_y)
            self.systems.append(system_data)
            self.system_buttons.add(button, layer=nei.id)
            self.properties.add(button)
            self.sort_buttons(self.system_buttons.get_widgets_from_layer(nei.id))
            nei.add_true_system(system_data)
            self.current.enable()
            self.load_universe_data(nei)
            self.stars_area.enable_all()
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
        button.kill()

        prim = system.primary
        scnd = system.secondary
        go_on_1 = prim.celestial_type == 'star' and scnd.celestial_type == 'system'
        go_on_2 = prim.celestial_type == 'system' and scnd.celestial_type == 'star'
        go_on_3 = prim.celestial_type == 'system' and scnd.celestial_type == 'system'

        nei = Universe.nei()
        if go_on_1 or go_on_2:
            nei.quantities['Triple'] += 1
        if go_on_3:
            nei.quantities['Multiple'] += 1

        self.dissolve_button.disable()
        EventHandler.trigger('DissolveSystem', self, {'system': system, 'nei': Universe.nei().id})

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()
        self.parent.swap_neighbourhood_button.unlock()
        if Universe.current_galaxy is not None:
            self.load_universe_data()
            self.show_loaded_systems()

    def create_systems(self):
        for nei in Universe.current_galaxy.stellar_neighbourhoods:
            widgets = self.stars_area.listed_objects.get_widgets_from_layer(nei.id)
            singles = [system for system in nei.proto_systems if system.composition == 'single']
            stars = [s.object_data for s in widgets if s.object_data.celestial_type == 'star']
            if len(singles):
                for star in stars:
                    chosen = [proto for proto in singles if proto.id == star.id]
                    if len(chosen):
                        chosen = chosen[0]  # no more randomness
                        del singles[singles.index(chosen)]
                    else:
                        chosen = singles.pop(0)

                    nei.remove_proto_system(chosen)
                    system = SingleSystem(star, nei.id)
                    system.cartesian = chosen.location
                    offset = nei.location
                    system.set_orbit(offset)
                    nei.add_true_system(system)

            if len(singles):
                brown = [i for i in Universe.brown_dwarfs if i.parent is None and i.neighbourhood_id == nei.id]
                white = [i for i in Universe.white_dwarfs if i.parent is None and i.neighbourhood_id == nei.id]
                black = [i for i in Universe.black_holes if i.parent is None and i.neighbourhood_id == nei.id]
                neutron = [i for i in Universe.neutron_stars if i.parent is None and i.neighbourhood_id == nei.id]

                stellar_mass_objects = brown + white + black + neutron
                for it in stellar_mass_objects:
                    chosen = singles.pop()
                    nei.remove_proto_system(chosen)
                    system = SingleSystem(it, nei.id)
                    system.cartesian = chosen.location
                    offset = Universe.nei().location
                    system.set_orbit(offset)
                    nei.add_true_system(system)

        self.parent.swap_neighbourhood_button.disable()

    def hide(self):
        if (self.triple == 0 and self.multiple == 0) and self.planetary_systems_added is False:
            self.planetary_systems_added = True
            self.create_systems()
            Universe.nei().set_planetary_systems()
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def transfer_proto_system(self, discarded):
        proto = [sys for sys in self.discarded_protos if sys.location == discarded.cartesian]
        if len(proto):
            proto = proto.pop(0)
        else:
            raise ValueError(f'{discarded} has an invalid location.')
        Universe.systems.append(proto)
        self.discarded_protos.remove(proto)

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
                "neighbourhood_id": system.neighbourhood_id,
                "flagged": system.flagged
            }
            data[system.id] = d

        if len(data):
            # so it doesn't save an empty dictionary.
            EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Binary Systems': data})

    def hold_loaded_bodies(self, event):
        if 'Binary Systems' in event.data and len(event.data['Binary Systems']):
            self.held_data.update(event.data['Binary Systems'].copy())

    def show_loaded_systems(self):
        for id in self.held_data:
            system_data = self.held_data[id]
            nei = Universe.current_galaxy.get_neighbourhood(system_data['neighbourhood_id'])
            self.load_universe_data(nei)

            prim = Universe.get_astrobody_by(system_data['primary'], 'id', silenty=True)
            scnd = Universe.get_astrobody_by(system_data['secondary'], 'id', silenty=True)
            if prim is not False and scnd is not False:
                go_on_1 = prim.celestial_type != 'system' and scnd.celestial_type == 'system'  # triple
                go_on_2 = prim.celestial_type == 'system' and scnd.celestial_type != 'system'  # triple
                go_on_3 = prim.celestial_type == 'system' and scnd.celestial_type == 'system'  # multiple

                if any([go_on_1, go_on_2, go_on_3]):
                    avg_s = system_data['avg_s']
                    ecc_p = system_data['ecc_p']
                    ecc_s = system_data['ecc_s']
                    name = system_data['name']

                    system = system_type(avg_s)(prim, scnd, avg_s, ecc_p, ecc_s, id=id, name=name, nei_id=nei.id)

                    button = self.create_button(system)
                    button.hide()

        self.stars_area.disable()

    def show_current_set(self, new_id):
        for button in self.system_buttons.widgets():
            button.hide()
        for button in self.system_buttons.get_widgets_from_layer(new_id):
            button.show()

        self.sort_buttons(self.system_buttons.get_widgets_from_layer(new_id))

    def update(self):
        self.load_universe_data()
        current = Universe.nei()
        if current.id != self.last_id:
            self.last_id = current.id
            self.stars_area.reset_offset()
            self.show_current_set(current.id)

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


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

            for listed in self.parent.stars_area.listed_objects.widgets():
                if listed.object_data is not star:
                    self.check_contruction(listed.object_data)
        elif str(self.secondary.value) == '':
            self.secondary.value = star
            self.parent.undo_button.enable()

        else:
            return False

        if self.primary.value != '' and self.secondary.value != '':
            for obj in self.properties.get_widgets_from_layer(2):
                obj.enable()
            if not self.has_values:
                x, y = self.parent.auto_button.rect.center
                mouse.set_pos(x, y)
                self.parent.auto_button.enable()
        return True

    def check_contruction(self, system_2):
        # you may be buiding a multiple system.
        # Are there slots for it?
        # if not, disable all other systems.
        # you can only add a star as a secondary system
        # to form a triple system.
        # again, if there are slots for it.
        if self.primary.value != '':
            system_1 = self.primary.value
            if system_1.celestial_type == 'system':
                triple = self.parent.triple
                multiple = self.parent.multiple
                if system_2.celestial_type == 'system':
                    if multiple >= 1:
                        self.parent.stars_area.disable_by_type('star')
                elif system_2.celestial_type == 'star':
                    if triple >= 1:
                        self.parent.stars_area.disable_by_type('system')

    def unset_stars(self):
        self.parent.stars_area.repopulate()
        self.erase()

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                x = Universe.nei().id
                self.current = system_type(self.separation.value)(*self.get_determinants(), nei_id=x)
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep', 'min_sep', 'system_name']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            if self.parent.triple > 0 or self.parent.multiple > 0:
                self.parent.setup_button.enable()


class ListedSystem(ListedBody):

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            if self.parent.parent.current.set_star(self.object_data):
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

    def disable_all(self):
        enabled_objects = [i for i in self.listed_objects.get_widgets_from_layer(Universe.nei().id)]
        if len(enabled_objects):
            for listed in enabled_objects:
                listed.disable()

    def repopulate(self):
        self.clear()

        for nei in Universe.current_galaxy.stellar_neighbourhoods:
            stars = [star for star in Universe.get_loose_stars(nei.id)]
            systems = [system for system in nei.true_systems]
            population = stars + systems

            if len(population):
                population.sort(key=lambda s: s.mass, reverse=True)
                self.populate(population, layer=nei.id)

    def update(self):
        if self.parent.triple < 1 and self.parent.multiple < 1:
            self.disable_all()
        if Universe.nei().id != self.last_idx:
            self.last_idx = Universe.nei().id
        self.show_current(Universe.nei().id)


class CreateSystemButton(SetupButton):

    def on_mousebuttondown(self, event):
        if event.origin == self:
            clause = self.parent.triple > 0 or self.parent.multiple > 0
            assert clause, "There are no more binary systems available to create."
            super().on_mousebuttondown(event)

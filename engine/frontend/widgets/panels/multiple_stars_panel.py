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
        self.triple_remaining = ValueText(self, 'Triple Star'+t, 3, self.area_buttons.top - 70, size=14)
        self.multiple_remaining = ValueText(self, 'Multiple Star'+t, 3, self.area_buttons.top - 50, size=14)
        self.properties.add(self.triple_remaining, self.multiple_remaining)

    def load_universe_data(self):
        triple_systems = Universe.current_galaxy.current_neighbourhood.quantities['Triple']
        multiple_systems = Universe.current_galaxy.current_neighbourhood.quantities['Multiple']
        self.triple_remaining.value = str(triple_systems)
        self.multiple_remaining.value = str(multiple_systems)

    def name_current(self, event):
        if event.data['object'] in self.systems:
            system = event.data['object']
            system.set_name(event.data['name'])

    def create_button(self, system_data):
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
        self.load_universe_data()
        if system_data not in self.systems:
            idx = len([s for s in self.systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, self.curr_x, self.curr_y)
            self.systems.append(system_data)
            self.system_buttons.add(button)
            self.properties.add(button)
            self.sort_buttons(self.system_buttons.widgets())
            Systems.set_system(system_data)
            self.current.enable()
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
        self.sort_buttons(self.system_buttons)
        self.properties.remove(button)
        self.dissolve_button.disable()
        if system in self.systems:
            Systems.dissolve_system(system)

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()
        self.parent.swap_neighbourhood_button.unlock()
        self.load_universe_data()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()
        self.parent.swap_neighbourhood_button.lock()


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
        for system_or_star in Systems.get_systems():
            if system_or_star.is_a_system:
                if system_or_star.star_system.system not in population:
                    population.append(system_or_star.star_system.system)

        if len(population):
            population.sort(key=lambda s: s.mass, reverse=True)
            self.populate(population, layer='two')

    def update(self):
        # this hook is necessary.
        # otherwise the content of the panel is deleted.
        pass

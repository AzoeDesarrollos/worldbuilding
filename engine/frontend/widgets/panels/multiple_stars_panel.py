from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, WidgetGroup
from engine.frontend.widgets.panels.common import ListedBody, ListedArea
from engine.equations.planetary_system import Systems
from .star_system_panel import SystemType, UndoButton
# from engine.backend.eventhandler import EventHandler
from engine.equations.binary import system_type
from engine.equations.star import Star
from ..basewidget import BaseWidget
from pygame import Surface


class MultipleStarsPanel(BaseWidget):
    skippable = True
    skip = False

    def __init__(self, parent):
        self.name = 'Multiple Stars'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)
        self.systems_area = AvailableSystems(self, ANCHO - 200, 32, 200, 340)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.f2 = self.crear_fuente(14, underline=True)
        self.write('Subsystems', self.f2, COLOR_AREA, x=3, y=420)

        self.current = SystemsType(self)
        self.restore_button = UndoButton(self, 234, 416)
        self.properties.add(self.current, self.systems_area, self.restore_button)

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()


class SystemsType(SystemType):
    virtual_primary = None
    virtual_secondary = None

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
            self.virtual_primary = Star({'mass': star.mass if hasattr(star, 'mass') else star.shared_mass})
        else:
            self.secondary.value = star
            self.parent.restore_button.enable()
            self.has_values = True
            self.virtual_secondary = Star({'mass': star.mass if hasattr(star, 'mass') else star.shared_mass})

    def unset_stars(self):
        pass

    def fill(self):
        super().fill()


class ListedSystem(ListedBody):

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.parent.current.set_star(self.object_data)
            self.kill()
            self.parent.sort()


class AvailableSystems(ListedArea):
    name = 'Systems'
    listed_type = ListedSystem

    def show(self):
        population = []
        for system_or_star in Systems.get_systems():
            if system_or_star.star_system.system not in population:
                population.append(system_or_star.star_system.system)
        population.sort(key=lambda s: s.mass, reverse=True)
        self.populate(population)
        super().show()

    # def update(self):
    # self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
    # idx = Systems.get_current_idx()
    # self.show_current(idx)

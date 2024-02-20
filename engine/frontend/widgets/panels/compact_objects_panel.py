from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, COLOR_AREA, COLOR_TEXTO
from engine.equations.compact import BlackHole, WhiteDwarf, BrownDwarf, NeutronStar
from engine.frontend.widgets import ValueText, BaseWidget, Meta
from engine.frontend.widgets.panels.common import TextButton
from engine.backend.eventhandler import EventHandler
from engine.equations.space import Universe
from engine.backend import Systems, q
from pygame import Surface, Rect


class CompactObjectsPanel(BaseWidget):
    skippable = False
    skip = False

    show_swap_system_button = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Compact Objects'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()

        self.white = WhiteDwarfType(self)
        self.neutron = NeutronStarType(self)
        self.black = BlackHoleType(self)
        self.brown = BrownDwarfType(self)
        self.current = self.white

        exp_font = self.crear_fuente(14)
        exp_white = 'White Dwarfs have masses between 0.17 and 1.4 solar masses.'
        exp_brown = 'Brown Dwarfs have masses between 13 and 80 Jupiter masses.'
        exp_black = 'Stellar Mass Black Holes have masses of 5 Solar masses or more.'
        exp_neutron = 'Neutron Stars have masses between 1.4 and 3 solar masses, and radii between 10 and 13 km.'

        rect = self.write2(exp_white, exp_font, 300, fg=COLOR_AREA, top=50, right=self.rect.right)
        rect = self.write2(exp_brown, exp_font, 300, fg=COLOR_AREA, top=rect.bottom + 20, right=self.rect.right)
        rect = self.write2(exp_black, exp_font, 300, fg=COLOR_AREA, top=rect.bottom + 50, right=self.rect.right)
        self.write2(exp_neutron, exp_font, 300, fg=COLOR_AREA, top=rect.bottom + 50, right=self.rect.right)

        area_font = self.crear_fuente(14, underline=True)
        self.area_buttons = Rect(0, 420, self.rect.w, 200)
        self.image.fill(COLOR_AREA, self.area_buttons)
        self.write('Compact Objects', area_font, COLOR_AREA, x=3, top=self.area_buttons.top)

        self.write('Remaining', exp_font, left=320, bottom=self.area_buttons.top - 20)
        self.remanent = ValueText(self, 'mass', 320, self.area_buttons.top - 20, size=14)
        self.remanent.enable()
        self.remanent.editable = False

        self.button_add = AddCompactObjectButton(self, ANCHO - 15, 416)

        self.properties.add(self.button_add, self.remanent, layer=1)

        t = " remaining"
        for i, text in enumerate(['Brown Dwarfs', 'White Dwarfs', 'Black Holes / Neutron Stars']):
            vt = ValueText(self, text + t, 3, 360 + i * 20, size=14)
            vt.enable()
            self.properties.add(vt, layer=7)

        EventHandler.register(self.clear, 'ClearData')

    def load_universe_data(self):
        value_brown = Universe.current_galaxy.current_neighbourhood.other['brown']
        value_white = Universe.current_galaxy.current_neighbourhood.other['white']
        value_black_or_neutron = Universe.current_galaxy.current_neighbourhood.other['black']

        widgets = self.properties.get_widgets_from_layer(7)
        text_brown, text_white, text_black = widgets

        brown_value = int(value_brown)
        white_value = int(value_white)
        other_value = int(value_black_or_neutron)

        if brown_value > 0:
            self.brown.enable()
        if white_value > 0:
            self.white.enable()
        if other_value > 0:
            self.neutron.enable()
            self.black.enable()

        text_brown.value = q(brown_value)
        text_white.value = q(white_value)
        text_black.value = q(other_value)

    def show(self):
        if Universe.current_galaxy is not None:
            self.load_universe_data()
            self.remanent.value = self.calculate_mass()

        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def review(self, object_data):
        if object_data.celestial_type == 'compact':
            if object_data.compact_subtype == 'black':
                text = self.black
            elif object_data.compact_subtype == 'neutron':
                text = self.neutron
            else:
                text = self.white
        else:
            text = self.brown

        text.fill(object_data)

    def clear(self, event=None):
        if event is None or event.data['panel'] is self:
            self.current.clear()

    @staticmethod
    def calculate_mass():
        current = Universe.current_galaxy.current_neighbourhood
        total_mass = sum([star.mass.to('sol_mass') for star in Systems.just_stars])
        main_sequence = len(Systems.just_stars)
        other = sum([*current.other.values()])

        total = main_sequence + other
        main_percentage = q(main_sequence / total, '%')
        other_percentage = q(other / total, '%')
        available_mass = total_mass / main_percentage
        return other_percentage * available_mass

    def create_button(self):
        object_data = self.current.current
        Universe.add_astro_obj(object_data)
        Systems.add_star(object_data)

        widgets = self.properties.get_widgets_from_layer(7)
        text_brown, text_white, text_black = widgets
        if object_data.compact_subtype in ('black', 'neutron'):
            text = text_black
        elif object_data.compact_subtype == 'white':
            text = text_white
        else:
            text = text_brown

        text.value = q(int(text.value) - 1)
        if text.value == 0:
            self.current.disable()

        mass = object_data.mass.to('sol_mass').m
        self.remanent.value = q(float(self.remanent.value) - mass, 'sol_mass')
        button = CompactObjectButton(self, object_data)
        self.properties.add(button, layer=6)
        self.sort_buttons(self.properties.get_widgets_from_layer(6))
        self.current.clear()


class NeutronStarType(BaseWidget):
    has_values = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.current = None

        texts = ['Mass', 'Radius']
        title_font = self.crear_fuente(16, underline=True)
        rect = self.parent.write('Neutron Star', title_font, x=3, y=30 * 9)
        for i, text in enumerate(texts):
            value = ValueText(self, text, 3, i * 20 + rect.bottom, size=16)
            self.parent.properties.add(value, layer=2)

    def fill(self, object_data=None):
        self.parent.current = self
        widgets = self.parent.properties.get_widgets_from_layer(2)
        mass, radius = widgets
        valid = False

        if object_data is None:
            if radius.value == '':
                NeutronStar.validate(float(mass.value), 'mass')
            else:
                NeutronStar.validate(float(radius.value), 'radius')
                self.current = NeutronStar(float(mass.value), float(radius.value))
                valid = True
        else:
            valid = True
            self.current = object_data

        if valid:
            mass.value = self.current.mass
            radius.value = self.current.radius

            self.parent.button_add.enable()

    def clear(self):
        for widget in self.parent.properties.get_widgets_from_layer(2):
            widget.value = ''
        self.current = None

    def disable(self):
        super().disable()
        self.clear()
        for widget in self.parent.properties.get_widgets_from_layer(2):
            widget.disable()

    def enable(self):
        super().enable()
        for widget in self.parent.properties.get_widgets_from_layer(2):
            widget.enable()
            widget.modifiable = True


class BlackHoleType(BaseWidget):
    has_values = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.current = None

        texts = ['Mass', 'Event Horizon', 'Photon Sphere']
        title_font = self.crear_fuente(16, underline=True)
        rect = self.parent.write('Black Hole', title_font, x=3, y=30 * 6 - 6)
        for i, text in enumerate(texts):
            value = ValueText(self, text, 3, i * 20 + rect.bottom, size=16)
            self.parent.properties.add(value, layer=3)

    def fill(self, object_data=None):
        self.parent.current = self
        widgets = self.parent.properties.get_widgets_from_layer(3)
        mass, radius, photon = widgets
        if object_data is None:
            self.current = BlackHole(float(mass.value))
        else:
            self.current = object_data

        mass.value = self.current.mass
        radius.value = self.current.event_horizon
        photon.value = self.current.photon_sphere

        self.parent.button_add.enable()

    def clear(self):
        for widget in self.parent.properties.get_widgets_from_layer(3):
            widget.value = ''
        self.current = None

    def disable(self):
        super().disable()
        self.clear()
        for widget in self.parent.properties.get_widgets_from_layer(3):
            widget.disable()

    def enable(self):
        super().enable()
        mass_widget = self.parent.properties.get_widgets_from_layer(3)[0]
        mass_widget.enable()
        mass_widget.modifiable = True


class WhiteDwarfType(BaseWidget):
    has_values = False
    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.current = None

        title_font = self.crear_fuente(16, underline=True)
        rect = self.parent.write('White Dwarf', title_font, x=3, y=30)
        texts = ['Mass', 'Radius']
        for i, text in enumerate(texts):
            value = ValueText(self, text, 3, i * 20 + rect.bottom, size=16)
            self.parent.properties.add(value, layer=4)

    def fill(self, object_data=None):
        self.parent.current = self
        widgets = self.parent.properties.get_widgets_from_layer(4)
        mass, radius = widgets
        if object_data is None:
            self.current = WhiteDwarf(float(mass.value))
        else:
            self.current = object_data

        mass.value = self.current.mass
        radius.value = self.current.radius

        self.parent.button_add.enable()

    def clear(self):
        for widget in self.parent.properties.get_widgets_from_layer(4):
            widget.clear()
        self.current = None

    def disable(self):
        super().disable()
        for widget in self.parent.properties.get_widgets_from_layer(4):
            widget.disable()
            widget.modifiable = False

    def enable(self):
        super().enable()
        mass_widget = self.parent.properties.get_widgets_from_layer(4)[0]
        mass_widget.enable()
        mass_widget.modifiable = True


class BrownDwarfType(BaseWidget):
    locked = False

    def __init__(self, parent):
        self.current = None
        super().__init__(parent)
        texts = ['Mass', 'Radius']
        title_font = self.crear_fuente(16, underline=True)
        rect = self.parent.write('Brown Dwarf', title_font, x=3, y=30 * 3 + 6)
        for i, text in enumerate(texts):
            value = ValueText(self, text, 3, i * 20 + rect.bottom, size=16)
            self.parent.properties.add(value, layer=5)

    def fill(self, object_data=None):
        self.parent.current = self
        widgets = self.parent.properties.get_widgets_from_layer(5)
        mass, radius = widgets
        if object_data is None:
            self.current = BrownDwarf(float(mass.value))
        else:
            self.current = object_data

        mass.value = self.current.mass
        radius.value = self.current.radius

        self.parent.button_add.enable()

    def clear(self):
        for widget in self.parent.properties.get_widgets_from_layer(5):
            widget.value = ''
        self.current = None

    def disable(self):
        super().disable()
        self.clear()
        for widget in self.parent.properties.get_widgets_from_layer(5):
            widget.disable()

    def enable(self):
        super().enable()
        mass_widget = self.parent.properties.get_widgets_from_layer(5)[0]
        mass_widget.enable()
        mass_widget.modifiable = True


class AddCompactObjectButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set Compact', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.create_button()
            self.disable()


class CompactObjectButton(Meta):
    enabled = True

    def __init__(self, parent, compact, size=16):
        super().__init__(parent)
        self.f1 = self.crear_fuente(size)
        self.f2 = self.crear_fuente(size, bold=True)
        self.object_data = compact
        self.img_uns = self.f1.render(str(compact) + ' #' + str(compact.idx), True, COLOR_TEXTO)
        self.img_sel = self.f2.render(str(compact) + ' #' + str(compact.idx), True, COLOR_TEXTO)

        self.image = self.img_uns
        self.rect = self.image.get_rect()
        self.max_w = self.img_sel.get_width()

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.review(self.object_data)
            self.parent.button_add.disable()

    def move(self, x, y):
        self.rect.topleft = x, y

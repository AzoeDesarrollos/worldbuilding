from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, COLOR_AREA, COLOR_TEXTO, Renderer
from engine.equations.compact import BlackHole, WhiteDwarf, BrownDwarf, NeutronStar
from engine.frontend.widgets import ValueText, BaseWidget, Meta
from engine.frontend.widgets.panels.common import TextButton
from engine.backend.eventhandler import EventHandler
from engine.equations.space import Universe
from engine.backend import q, roll, Config
from random import expovariate, choice
from pygame import Surface, Rect
from time import sleep


class CompactObjectsPanel(BaseWidget):
    skippable = True
    skip = False

    show_swap_system_button = False
    locked = False

    last_id = -1

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Compact Objects'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()
        self.buttons = Group()

        self.white = WhiteDwarfType(self)
        self.neutron = NeutronStarType(self)
        self.black = BlackHoleType(self)
        self.brown = BrownDwarfType(self)
        self.current = self.white

        self.compact_objects = Group()

        font = self.crear_fuente(14)
        exp_white = 'White Dwarfs have masses between 0.17 and 1.4 solar masses.'
        exp_brown = ('Brown Dwarfs have masses between 13 and 80 Jupiter masses. '
                     'Their radius is equal to Jupiter, plus or minus a few decimals.')
        exp_black = 'Stellar Mass Black Holes have masses of 5 Solar masses or more.'
        exp_neutron = 'Neutron Stars have masses between 1.4 and 3 solar masses, and radii between 10 and 13 km.'

        r, c = self.rect.right, COLOR_AREA
        self.white_rect = self.write2(exp_white, font, 300, fg=c, top=50, right=self.rect.right)
        self.brown_rect = self.write2(exp_brown, font, 300, fg=c, top=self.white_rect.bottom + 20, right=r)
        self.black_rect = self.write2(exp_black, font, 300, fg=c, top=self.brown_rect.bottom + 50, right=r)
        self.neutron_rect = self.write2(exp_neutron, font, 300, fg=c, top=self.black_rect.bottom + 50, right=r)

        area_font = self.crear_fuente(14, underline=True)
        self.area_buttons = Rect(0, 420, self.rect.w, 200)
        self.image.fill(COLOR_AREA, self.area_buttons)
        self.write('Compact Objects', area_font, COLOR_AREA, x=3, top=self.area_buttons.top)

        self.write('Remaining', font, left=320, bottom=self.area_buttons.top - 20)
        self.remanent = ValueText(self, 'mass', 320, self.area_buttons.top - 20, size=14)
        self.remanent.enable()
        self.remanent.editable = False

        self.button_add = AddCompactObjectButton(self, ANCHO - 15, 416)
        self.auto_button = AutoButton(self, ANCHO - 100, self.button_add.rect.top)

        self.properties.add(self.button_add, self.remanent, self.auto_button, layer=1)

        t = " remaining"
        for i, text in enumerate(['Brown Dwarfs', 'White Dwarfs', 'Black Holes / Neutron Stars']):
            vt = ValueText(self, text + t, 3, 360 + i * 20, size=14)
            vt.enable()
            self.properties.add(vt, layer=7)

        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.save_objects, 'Save')
        EventHandler.register(self.load_objects, 'LoadCompact')
        EventHandler.register(self.export_data, 'ExportData')
        EventHandler.register(self.name_current, 'NameObject')

    def load_universe_data(self):
        current_nei = Universe.current_galaxy.current_neighbourhood

        no_black_holes = "This stellar neighbourhood does not have room for more black holes."
        no_neutron_stars = "This stellar neighbourhood does not have room for more neutron stars."
        no_brown_dwarfs = "This stellar neighbourhood does not have room for more brown dwarfs."
        no_white_dwarfs = "This stellar neighbourhood does not have room for more white dwarfs."

        widgets = self.compact_objects.get_widgets_from_layer
        count_brown = sum([1 for w in widgets(current_nei.id) if w.compact_subtype is None])
        count_white = sum([1 for w in widgets(current_nei.id) if w.compact_subtype == 'white'])
        count_other = sum([1 for w in widgets(current_nei.id) if w.compact_subtype == 'neutron'])
        count_other += sum([1 for w in widgets(current_nei.id) if w.compact_subtype == 'black'])

        value_brown = int(current_nei.other['brown'] - count_brown)
        value_white = int(current_nei.other['white'] - count_white)
        value_black_or_neutron = int(current_nei.other['black'] - count_other)

        widgets = self.properties.get_widgets_from_layer(7)
        text_brown, text_white, text_black = widgets

        exp_font = self.crear_fuente(14)
        if value_brown > 0:
            self.brown.enable()
        else:
            self.brown.disable()
            self.image.fill(COLOR_BOX, self.brown_rect)
            self.write2(no_brown_dwarfs, exp_font, 300, fg=COLOR_AREA, topleft=self.brown_rect.topleft)

        if value_white > 0:
            self.white.enable()
        else:
            self.white.disable()
            self.write2(no_white_dwarfs, exp_font, 300, fg=COLOR_AREA, topleft=self.white_rect.topleft)

        if value_black_or_neutron > 0:
            self.neutron.enable()
            self.black.enable()
        else:
            self.neutron.disable()
            self.black.disable()
            self.image.fill(COLOR_BOX, self.black_rect.union(self.neutron_rect))  # Eraser
            self.write2(no_black_holes, exp_font, 300, fg=COLOR_AREA, topleft=self.black_rect.topleft)
            self.write2(no_neutron_stars, exp_font, 300, fg=COLOR_AREA, topleft=self.neutron_rect.topleft)

        text_brown.value = q(value_brown)
        text_white.value = q(value_white)
        text_black.value = q(value_black_or_neutron)

    def show(self):
        if Universe.current_galaxy is not None:
            self.load_universe_data()
            self.remanent.value = self.calculate_mass()
            self.sort_buttons(self.properties.get_widgets_from_layer(6))
            self.auto_button.enable()

        elif Config.get('mode') == 1:
            self.brown.enable()
            self.white.enable()
            self.neutron.enable()
            self.black.enable()

        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()
        for button in self.buttons.widgets():
            button.hide()

    def review(self, object_data):
        for button in self.properties.get_widgets_from_layer(6):
            button.deselect()

        if object_data.compact_subtype == 'black':
            text = self.black
        elif object_data.compact_subtype == 'neutron':
            text = self.neutron
        elif object_data.compact_subtype == 'white':
            text = self.white
        else:
            text = self.brown

        text.fill(object_data)

    def clear(self, event=None):
        if event is None or event.data['panel'] is self:
            self.brown.clear()
            self.black.clear()
            self.white.clear()
            self.neutron.clear()
            self.load_universe_data()

    @staticmethod
    def calculate_mass():
        stars = Universe.get_loose_stars(Universe.nei().id)
        total_mass = sum([star.mass.to('sol_mass') for star in stars])
        main_sequence = len(stars)
        other = sum([*Universe.nei().other.values()])

        total = main_sequence + other
        main_percentage = q(main_sequence / total, '%')
        other_percentage = q(other / total, '%')
        available_mass = total_mass / main_percentage
        return other_percentage * available_mass

    def create_button(self, object_data=None):
        if object_data is None:
            object_data = self.current.current
        Universe.add_astro_obj(object_data)
        Universe.add_loose_star(object_data, object_data.neighbourhood_id)
        self.compact_objects.add(object_data, layer=object_data.neighbourhood_id)

        widgets = self.properties.get_widgets_from_layer(7)
        text_brown, text_white, text_black = widgets
        if object_data.compact_subtype in ('black', 'neutron'):
            text = text_black
        elif object_data.compact_subtype == 'white':
            text = text_white
        else:
            text = text_brown

        if text.value != '':
            text.value = q(int(text.value) - 1)
            if text.value == 0:
                self.current.disable()

        mass = object_data.mass.to('sol_mass').m
        if self.remanent.value != '':
            self.remanent.value = q(float(self.remanent.value) - mass, 'sol_mass')
        button = CompactObjectButton(self, object_data, size=13)
        self.buttons.add(button, layer=object_data.neighbourhood_id)
        if self.is_visible:
            buttons = self.buttons.get_widgets_from_layer(object_data.neighbourhood_id)
            self.sort_buttons(buttons)
            self.current.clear()

    def save_objects(self, event):
        macro_data = {}
        for compact in self.compact_objects.widgets():
            data = {
                'mass': compact.mass.m,
                "neighbourhood_id": compact.neighbourhood_id,
                'subtype': compact.compact_subtype,
                'age': compact.age.m,
                'flagged': compact.flagged
            }
            if compact.compact_subtype in ('neutron', None):
                data.update({'radius': compact.radius.m})

            if hasattr(compact, 'sub_cls'):  # neutron stars and white dwarfs otherwise assing random numbers.
                data.update({'sub': compact.sub_cls})

            if compact.has_name:
                data.update({'name': compact.name})

            macro_data[compact.id] = data

        EventHandler.trigger(event.tipo + 'Data', 'Compact', {"Compact Objects": macro_data})

    def load_objects(self, event):
        self.load_universe_data()
        for key in event.data['Compact Objects']:
            data = event.data['Compact Objects'][key]
            data['id'] = key
            subtype = data['subtype']
            if subtype == 'black':
                compact = BlackHole(data)
            elif subtype == 'neutron':
                compact = NeutronStar(data)
            elif subtype == 'white':
                compact = WhiteDwarf(data)
            else:
                compact = BrownDwarf(data)

            self.create_button(compact)

    def name_current(self, event):
        if event.data['object'] in self.compact_objects:
            moon = event.data['object']
            moon.set_name(event.data['name'])

    def export_data(self, event):
        if event.data['panel'] is self:
            pass

    def show_current(self, new_id):
        self.load_universe_data()
        for button in self.buttons.widgets():
            button.hide()
        for button in self.buttons.get_widgets_from_layer(new_id):
            button.show()

        self.sort_buttons(self.buttons.get_widgets_from_layer(new_id))
        self.auto_button.enable()

    def update(self):
        current = Universe.nei()
        if current.id != self.last_id:
            self.last_id = current.id
            self.show_current(current.id)


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
                idx = Universe.nei().id
                NeutronStar.validate(float(radius.value), 'radius')
                data = {'mass': float(mass.value), 'radius': float(radius.value), 'neighbourhood_id': idx}
                self.current = NeutronStar(data)
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
            idx = Universe.nei().id
            self.current = BlackHole({'mass': float(mass.value), 'neighbourhood_id': idx})
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
            idx = Universe.nei().id
            self.current = WhiteDwarf({'mass': float(mass.value), 'neighbourhood_id': idx})
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
            idx = Universe.nei().id
            self.current = BrownDwarf({'mass': float(mass.value),
                                       'radius': float(radius.value),
                                       'neighbourhood_id': idx})
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
        for widget in self.parent.properties.get_widgets_from_layer(5):
            widget.enable()
            widget.modifiable = True


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
        self.crear(str(compact))

        self.image = self.img_uns
        self.rect = self.image.get_rect()
        self.max_w = self.img_sel.get_width() + 3

    def crear(self, text):
        self.img_uns = self.f1.render(text, True, COLOR_TEXTO)
        self.img_sel = self.f2.render(text, True, COLOR_TEXTO)
        self.image = self.img_uns

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.clear()
            self.parent.review(self.object_data)
            self.select()
            self.parent.button_add.disable()
            self.parent.auto_button.disable()

    def move(self, x, y):
        self.rect.topleft = x, y

    def update(self):
        super().update()
        if self.object_data.has_name:
            self.crear(str(self.object_data))


class AutoButton(TextButton):

    def __init__(self, parent, x, y):
        super().__init__(parent, '[Auto]', x, y)

    def on_mousebuttondown(self, event):
        if self.enabled and event.data['button'] == 1 and event.origin == self:
            neighbourhood_id = Universe.nei().id
            generated_objects = []
            if self.parent.brown.enabled:
                total = Universe.nei().other['brown']
                for _ in range(total):
                    a = roll(13, 80)
                    b = 1 + roll(0.0, 0.1)
                    compact = BrownDwarf({'mass': a, 'radius': b, 'neighbourhood_id': neighbourhood_id})
                    generated_objects.append(compact)
            if self.parent.white.enabled:
                total = Universe.nei().other['white']
                for _ in range(total):
                    a = roll(0.17, 1.4)
                    compact = WhiteDwarf({'mass': a, 'neighbourhood_id': neighbourhood_id})
                    generated_objects.append(compact)
            total = Universe.nei().other['black']
            while total:
                chosen = choice(['black', 'neutron'])
                compact = None
                if self.parent.black.enabled and chosen == 'black':
                    a = expovariate(5)
                    compact = BlackHole({'mass': a, 'neighbourhood_id': neighbourhood_id})
                elif self.parent.neutron.enabled and chosen == 'neutron':
                    a = roll(1.4, 3.0)
                    b = roll(10, 13)
                    compact = NeutronStar({'mass': a, 'radius': b, 'neighbourhood_id': neighbourhood_id})

                if compact is not None:
                    total -= 1
                    generated_objects.append(compact)

            for compact in generated_objects:
                sleep(0.01)
                self.parent.create_button(compact)
                Renderer.update()
            self.parent.load_universe_data()
            self.disable()

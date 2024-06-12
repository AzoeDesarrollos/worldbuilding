from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, COLOR_AREA, COLOR_TEXTO, NUEVA_LINEA
from engine.frontend.widgets import ValueText, BaseWidget, Meta
from engine.frontend.widgets.panels.common import TextButton
from engine.equations.system_binary import analyze_binaries
from engine.equations.stellar_neighbourhood import *
from engine.backend.eventhandler import EventHandler
from engine.equations.space import Universe
from engine.equations.galaxy import Galaxy
from math import pi, acos, sin, cos, floor
from pygame import Surface, draw, Rect
from random import uniform


class NeighbourhoodPanel(BaseWidget):
    skippable = True
    skip = False

    locked = False

    show_swap_system_button = False

    current = None
    current_nei = None

    current_galaxy_id = None
    last_id = None
    analized = None

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Neighbourhood'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()
        self.neighbourhood_buttons = Group()
        title_font = self.crear_fuente(16, underline=True)
        subtitle_font = self.crear_fuente(14, underline=True)

        self.galaxy = GalaxyType(self)
        self.neighbourhood = NeighbourhoodType(self)

        self.area_buttons = Rect(0, 420, self.rect.w, 200)
        self.image.fill(COLOR_AREA, self.area_buttons)
        self.write('Systems', subtitle_font, COLOR_AREA, x=3, top=self.area_buttons.top)

        self.current = None
        self.current_nei = None

        rect = self.write('Galactic Characteristics', title_font, x=3, y=30)
        texts = ['Radius', 'Habitable Zone inner limit', 'Habitable Zone outer limit']
        for i, text in enumerate(texts):
            value = ValueText(self.galaxy, text, 3, i * 20 + rect.bottom, size=16)
            if i == 0:
                value.enable()
                value.modifiable = True
            self.properties.add(value, layer=1)

        rect = draw.aaline(self.image, (0, 0, 0), [3, len(texts) * 20 + 55], [self.rect.w - 3, len(texts) * 20 + 55])

        texts = ['Distance from galactic core', 'Radius']
        rect = self.write('Neighbourhood Characteristics', title_font, x=3, y=rect.bottom + 5)
        for i, text in enumerate(texts):
            value = ValueText(self.neighbourhood, text, 3, i * 20 + rect.bottom, size=16)
            value.modifiable = True
            self.properties.add(value, layer=2)

        value = ValueText(self.neighbourhood, 'Density x1K', 400, rect.bottom, size=16)
        value.do_round = True
        self.properties.add(value, layer=2)

        self.button_add = AddNeighbourhoodButton(self, ANCHO - 15, 416)
        self.properties.add(self.button_add, layer=3)

        EventHandler.register(self.clear, 'ClearData')
        EventHandler.register(self.switch_current, 'SwitchGalaxy')
        EventHandler.register(self.export_data, 'ExportData')
        self.neighbourhoods = []

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if event.data['button'] in (4, 5):
                buttons = self.properties.get_widgets_from_layer(5)
                if self.area_buttons.collidepoint(event.data['pos']) and len(buttons):
                    last_is_hidden = not buttons[-1].is_visible
                    first_is_hidden = not buttons[0].is_visible
                    if event.data['button'] == 4 and first_is_hidden:
                        self.curr_y += NUEVA_LINEA
                    elif event.data['button'] == 5 and last_is_hidden:
                        self.curr_y -= NUEVA_LINEA
                    self.sort_buttons(buttons, overriden=True)

    def select_one(self, selected):
        for button in self.properties.get_widgets_from_layer(5):
            button.deselect()
        selected.select()
        self.current = selected
        self.current_nei = selected.object_data

    def create_button(self, data=None):
        widgets = self.properties.get_widgets_from_layer(2)
        location = widgets[0].value
        radius = widgets[1].value
        density = widgets[2].value / 1000 if type(widgets[2].value) is not str else widgets[2].value
        if data is None:
            data = {'location': location, 'radius': radius, 'density': density}
        else:
            density = data['density']
            radius = data['radius']

        self.neighbourhood.characteristics.recalculate(density, radius)
        brown = self.neighbourhood.characteristics.stars('bd')
        white = self.neighbourhood.characteristics.stars('wd')
        black = self.neighbourhood.characteristics.stars('black hole')
        other = {'brown': brown, 'white': white, 'black': black}
        data.update({'other': other})

        object_data = DefinedNeighbourhood(len(self.neighbourhoods) + 1, data)
        self.neighbourhoods.append(object_data)
        self.current_nei = object_data
        button = NeighbourhoodButton(self, object_data)
        self.neighbourhood_buttons.add(button, layer=self.current_galaxy_id)
        self.properties.add(button, layer=5)
        if self.is_visible:
            self.sort_buttons(self.properties.get_widgets_from_layer(5))

        self.neighbourhood.characteristics.set_location(data['location'], known_density=data['density'])
        self.neighbourhood.characteristics.set_radius(data['radius'])

        stars = self.neighbourhood.characteristics.individual_stars
        self.current_nei.add_proto_stars(stars)

        comps = ['single', 'binary', 'triple', 'multiple']
        positions = self.neighbourhood.characteristics.system_positions(object_data)
        singles = [x['pos'] for x in positions if x['configuration'] == 'Single']
        binaries = [x['pos'] for x in positions if x['configuration'] == 'Binary']
        triples = [x['pos'] for x in positions if x['configuration'] == 'Triple']
        multiples = [x['pos'] for x in positions if x['configuration'] == 'Multiple']
        d = {'single': singles, 'binary': binaries, 'triple': triples, 'multiple': multiples}
        for i, comp in enumerate(comps):
            quantity = self.neighbourhood.characteristics.systems(comp)
            object_data.set_quantity(comp.title(), quantity)
            for each in range(quantity):
                system_position = d[comp][each]
                system_data = {'composition': comp, 'location': system_position, 'idx': i,
                               'neighbourhood_id': object_data.id}
                if self.analized is not None and each < len(self.analized[comp.title()]):
                    system_id = self.analized[comp.title()][each]
                    system_data.update({'id': system_id})

                system_object = ProtoSystem(system_data)
                object_data.add_proto_system(system_object)

        return button

    def set_analyzed(self, pairs):
        self.analized = pairs

    def get_values(self, location, radius):
        density = self.galaxy.current.get_density_at_location(location)
        loc_text, rad_text, den_text = self.properties.get_widgets_from_layer(2)
        loc_text.value = str(location)
        rad_text.value = str(radius)
        den_text.value = str(round(density, 3))
        self.neighbourhood.fill()

    def create_neighbourhood(self, data=None):
        button = self.create_button(data)
        self.galaxy.current.add_neighbourhood(button.object_data)
        return button

    def clear(self, event=None):
        if event is None or event.data['panel'] is self:
            self.neighbourhood.clear()
            for value_text in self.properties.get_widgets_from_layer(2):
                value_text.clear()

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()
        self.neighbourhood.populate()
        self.sort_buttons(self.properties.get_widgets_from_layer(5))
        if Universe.current_galaxy is not None:
            self.parent.swap_galaxy_button.enable()
            self.parent.swap_neighbourhood_button.disable()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()
        self.parent.swap_galaxy_button.disable()
        self.parent.swap_neighbourhood_button.enable()
        self.parent.swap_neighbourhood_button.set_current()

    def switch_current(self, event):
        self.current_galaxy_id = event.data['current'].id
        if self.parent.current is self:
            self.neighbourhood.clear()
            self.galaxy.current = event.data['current']
            self.neighbourhood.characteristics.set_galaxy()
            for widget in self.properties.get_widgets_from_layer(2):
                widget.clear()
            for button in self.properties.get_widgets_from_layer(5):
                button.deselect()
                button.hide()
            for button in self.neighbourhood_buttons.get_widgets_from_layer(self.current_galaxy_id):
                button.show()

    def update(self):
        if self.current_galaxy_id != self.last_id:
            self.last_id = self.current_galaxy_id

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class GalaxyType(BaseWidget):
    locked = False

    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.current = None
        EventHandler.register(self.save_galaxy, 'Save')
        EventHandler.register(self.load_galaxies, 'LoadGalaxies')
        EventHandler.register(self.switch_current, 'SwitchGalaxy')

    def fill(self, data=None):
        galaxy = Galaxy()
        galaxy.initialize(data)
        Universe.add_astro_obj(galaxy)
        if not self.has_values:
            self.current = galaxy
            self.parent.current_galaxy_id = galaxy.id
            widgets = self.parent.properties.get_widgets_from_layer(1)
            if data is None:
                radius_text = widgets[0]
                self.current.set_radius(float(radius_text.value))
            widgets[0].value = galaxy.radius
            widgets[1].value = galaxy.inner
            widgets[2].value = galaxy.outer

            widgets = self.parent.properties.get_widgets_from_layer(2)
            widgets[0].set_min_and_max(galaxy.inner.m, galaxy.outer.m)
            widgets[2].value = 'Unknown'
            for widget in widgets:
                widget.enable()
            self.has_values = True

            swap_galaxy_button = self.parent.parent.swap_galaxy_button
            swap_galaxy_button.enable()
            swap_galaxy_button.current = self.current

    def save_galaxy(self, event):
        widget = self.parent.properties.get_widgets_from_layer(1)[0]
        if widget.value != '':
            data = {"radius": widget.value, 'flagged': self.current.flagged}

            EventHandler.trigger(event.tipo + 'Data', 'Galaxy', {'Galaxies': {self.current.id: data}})

    def load_galaxies(self, event):
        for key in event.data['Galaxies']:
            data = {'radius': event.data['Galaxies'][key]['radius'], 'id': key}
            self.fill(data)

    def switch_current(self, event):
        self.current = event.data['current']
        self.has_values = False
        self.fill(self.current)


class NeighbourhoodType(BaseWidget):
    locked = False
    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.characteristics = StellarNeighbourhood(self)
        self.title_font = self.crear_fuente(16, underline=True)
        EventHandler.register(self.save_neighbourhoods, 'Save')
        EventHandler.register(self.load_neighbourhoods, 'LoadNeighbourhoods')
        self.values = {}

        f = self.crear_fuente(16, bold=True)
        self.habitable = f.render('Habitable', True, (0, 255, 0), COLOR_BOX)
        self.uninhabitable = f.render('Uninhabitable', True, (255, 0, 0), COLOR_BOX)
        self.hab_rect = self.habitable.get_rect(centerx=460, y=self.parent.rect.y + 160)
        self.unhab_rect = self.uninhabitable.get_rect(centerx=470, y=self.parent.rect.y + 160)
        self.eraser = Rect(390, self.parent.rect.y + 160, 150, 24)

    def fill(self):
        self.characteristics.set_galaxy()
        widgets = self.parent.properties.get_widgets_from_layer(2)
        location_text, radius_text, density_text = widgets
        location_valid, radius_valid, valid = False, False, False

        if type(location_text.value) in (str, float) and location_text.value != '':
            valid = self.characteristics.galaxy.validate_position(float(location_text.value))
            density = self.characteristics.set_location(float(location_text.value))
            location_text.value = q(location_text.value, 'ly')
            location_valid = True
            location_text.editable = False
            density_text.value = q(density * 1000)

        if type(radius_text.value) in (str, float) and radius_text.value != '':
            self.characteristics.set_radius(float(radius_text.value))
            radius_text.value = self.characteristics.radius
            radius_valid = True

        if location_valid and radius_valid:
            self.clear()
            self.populate()
            self.has_values = True
            self.parent.button_add.enable()

            if valid:
                self.parent.image.blit(self.habitable, self.hab_rect)
            else:
                self.parent.image.blit(self.uninhabitable, self.unhab_rect)

    def save_neighbourhoods(self, event):
        macro_data = {}
        for neighbourhood in self.parent.neighbourhoods:
            data = {
                'location': neighbourhood.location,
                'radius': neighbourhood.radius,
                'density': neighbourhood.density,
                'galaxy_id': self.parent.galaxy.current.id,
                'seed': neighbourhood.nei_seed
            }
            macro_data[neighbourhood.id] = data

        EventHandler.trigger(event.tipo + 'Data', 'Neighbourhood', {"Neighbourhoods": macro_data})

    def load_neighbourhoods(self, event):
        self.parent.set_analyzed(analyze_binaries(event.data))
        self.characteristics.set_galaxy()
        if len(event.data['Neighbourhoods']):
            for key in event.data['Neighbourhoods']:
                neighbourhood_data = event.data['Neighbourhoods'][key]
                location = neighbourhood_data['location']
                density = neighbourhood_data['density']
                neighbourhood_data['id'] = key
                self.parent.galaxy.current.record_density_at_location(location, density)
                nei = self.parent.create_neighbourhood(neighbourhood_data)
                nei.object_data.process_data(event.data)

    def clear(self):
        for name in self.values:
            value = self.values[name]
            value.clear()
        self.parent.image.fill(COLOR_BOX, self.eraser)

    def populate(self):
        rect_stars = self.parent.write('Stars in vicinity', self.title_font, x=3, y=185)
        rect_systems = self.parent.write('Stars Systems in vicinity', self.title_font, x=230, y=185)

        types = 'o,b,a,f,g,k,m,wd,bd,black hole'.split(',')

        for i, cls in enumerate(types):
            if len(cls) == 1:
                clase = f'{cls.upper()} Stars'

            elif cls == 'wd':
                clase = 'White Dwarfs'

            elif cls == 'bd':
                clase = 'Brown Dwarfs'
            else:
                clase = cls.title() + 's'

            quantity = self.characteristics.stars(cls)
            if clase not in self.values:
                value_text = ValueText(self, clase, 3, i * 20 + rect_stars.bottom, size=15)
                self.values[clase] = value_text
                value_text.value = ''
            else:
                value_text = self.values[clase]
                value_text.value = str(quantity)
            self.parent.properties.add(value_text, layer=4)
            value_text.show()

        total_stars = self.characteristics.totals('stars')
        main_seq = self.characteristics.totals('main sequence')
        for i, title in enumerate(['Total Stars', 'Main Sequence Stars'], start=7):
            if title not in self.values:
                value_text = ValueText(self, title, 230, i * 20 + rect_stars.bottom, size=15)
                self.values[title] = value_text
                value_text.value = ''
                write = False
            else:
                write = True
                value_text = self.values[title]

            if i == 7 and write:
                value_text.value = str(int(total_stars))
            elif i == 8 and write:
                value_text.value = str(int(main_seq))

            self.parent.properties.add(value_text, layer=4)
            value_text.show()

        comps = ['single', 'binary', 'triple', 'multiple']
        for i, comp in enumerate(comps):
            name = f'{comp.title()} Star Systems'
            quantity = self.characteristics.systems(comp)
            if name not in self.values:
                value_text = ValueText(self, name, 230, i * 35 + rect_systems.bottom, size=14)
                self.values[name] = value_text
                value_text.value = ''
            else:
                value_text = self.values[name]
                value_text.value = str(quantity)
            self.parent.properties.add(value_text, layer=4)
            value_text.show()

        total_systems = 0 if self.characteristics is None else self.characteristics.totals('systems')
        if 'Total Systems' not in self.values:
            value_text = ValueText(self, 'Total Systems', 230, 9 * 20 + rect_stars.bottom, size=14)
            self.values['Total Systems'] = value_text
            value_text.value = ''
        else:
            value_text = self.values['Total Systems']
            value_text.value = str(int(total_systems))
        self.parent.properties.add(value_text, layer=4)
        value_text.show()

    def elevate_changes(self, value_text, new_value):
        widgets = self.parent.properties.get_widgets_from_layer(2)
        location_text, radius_text, density_text = widgets

        if location_text is value_text:
            if location_text.value != new_value:
                self.fill()


class StellarNeighbourhood:
    _o_stars = 0
    _b_stars = 0
    _a_stars = 0
    _f_stars = 0
    _g_stars = 0
    _k_stars = 0
    _m_stars = 0
    _w_dwarfs = 0
    _b_dwarfs = 0
    _other = 0

    _total_stars = 0
    _total_systems = 0

    _single = 0
    _binary = 0
    _triple = 0
    _multiple = 0

    radius = None

    location = None
    density = None

    celestial_type = 'stellar bubble'

    main_sequence_stars = 0

    galaxy = None

    def __init__(self, parent):
        self.parent = parent

    def set_galaxy(self):
        self.galaxy = self.parent.parent.galaxy.current

    def set_location(self, location, known_density=None):
        self.location = location
        if known_density is not None:
            self.galaxy.record_density_at_location(location, known_density)
            density = known_density
        else:
            density = self.galaxy.get_density_at_location(location)
        if density is None:
            self.density = uniform(0.003, 0.012)
            self.galaxy.record_density_at_location(location, self.density)
        else:
            self.density = density
        return self.density

    def set_radius(self, radius):
        assert radius < 500, 'Stellar Neighbourhood will pop out of the galatic disk'
        self.radius = q(radius, 'ly')
        self._calculate(self.density, self.radius.m)

    def recalculate(self, density, radius):
        self._calculate(float(density), float(radius))

    def _calculate(self, density, radius):
        stellar_factor = density * ((4 / 3) * pi * radius ** 3)

        self._o_stars = round(stellar_factor * 0.9 * 0.0000003, 0)
        self._b_stars = round(stellar_factor * 0.9 * 0.0013, 0)
        self._a_stars = round(stellar_factor * 0.9 * 0.006, 0)
        self._f_stars = round(stellar_factor * 0.9 * 0.03, 0)
        self._g_stars = round(stellar_factor * 0.9 * 0.076, 0)
        self._k_stars = round(stellar_factor * 0.9 * 0.121, 0)
        self._m_stars = round(stellar_factor * 0.9 * 0.7645, 0)
        self._w_dwarfs = round(stellar_factor * 0.09, 0)
        self._b_dwarfs = round(stellar_factor / 2.5, 0)
        self._other = floor(stellar_factor * 0.01)

        self._total_stars = sum([self._o_stars, self._b_stars, self._a_stars, self._f_stars, self._g_stars,
                                 self._k_stars, self._m_stars, self._w_dwarfs, self._b_dwarfs, self._other])

        self.main_sequence_stars = sum([self._o_stars, self._b_stars, self._a_stars, self._f_stars, self._g_stars,
                                        self._k_stars, self._m_stars])

        # The distribution of individual stars into systems only takes into account main sequence stars because
        # the program doesn't allow for neither the creation of brown or white dwarves or black holes yet.
        # this might change in future revisions.
        self._binary = int(round(((self.main_sequence_stars / 1.58) * 0.33), 0))
        self._triple = int(round(((self.main_sequence_stars / 1.58) * 0.08), 0))
        self._multiple = int(round(((self.main_sequence_stars / 1.58) * 0.03), 0))
        self._single = int(self.main_sequence_stars - ((self._binary * 2) + (self._triple * 3) + (self._multiple * 4)))
        # se agregan los cuerpos compactos porque por definición son sistemas simples.
        self._single += int(self._w_dwarfs + self._b_dwarfs + self._other)

        self._total_systems = int(sum([self._single, self._binary, self._triple, self._multiple]))

        # this is because some of the binary pairs are part
        self._binary += self._triple + (self._multiple * 2)
        # of triple and cuadruple systems.

        self.individual_stars = [{'class': 'O', 'idx': i} for i in range(int(self._o_stars))]
        self.individual_stars += [{'class': 'B', 'idx': i} for i in range(int(self._b_stars))]
        self.individual_stars += [{'class': 'A', 'idx': i} for i in range(int(self._a_stars))]
        self.individual_stars += [{'class': 'F', 'idx': i} for i in range(int(self._f_stars))]
        self.individual_stars += [{'class': 'G', 'idx': i} for i in range(int(self._g_stars))]
        self.individual_stars += [{'class': 'K', 'idx': i} for i in range(int(self._k_stars))]
        self.individual_stars += [{'class': 'M', 'idx': i} for i in range(int(self._m_stars))]

    def stars(self, spectral_type: str = 'g') -> int:

        types = 'o,b,a,f,g,k,m,wd,white,brown,bd,black,black hole'.split(',')
        assert spectral_type in types, f'spectral_type "{spectral_type}" is unrecognizable.'

        if spectral_type == 'o':
            returned = self._o_stars
        elif spectral_type == 'b':
            returned = self._b_stars
        elif spectral_type == 'a':
            returned = self._a_stars
        elif spectral_type == 'f':
            returned = self._f_stars
        elif spectral_type == 'g':
            returned = self._g_stars
        elif spectral_type == 'k':
            returned = self._k_stars
        elif spectral_type == 'm':
            returned = self._m_stars
        elif spectral_type in ('wd', 'white'):
            returned = self._w_dwarfs
        elif spectral_type in ('bd', 'brown'):
            returned = self._b_dwarfs
        else:
            returned = self._other

        return int(returned)

    def systems(self, configuration: str = 'single') -> int:
        if configuration == 'single':
            return self._single
        elif configuration == 'binary':
            return self._binary
        elif configuration == 'triple':
            return self._triple
        elif configuration == 'multiple':
            return self._multiple
        else:
            raise ValueError('Configuration is invalid.')

    def totals(self, kind: str = 'stars'):
        if kind == 'stars':
            return self._total_stars
        elif kind == 'systems':
            return self._total_systems
        elif kind == 'main sequence':
            return self.main_sequence_stars
        else:
            raise ValueError(f'Kind "{kind}" is unrecognizable.')

    def system_positions(self, current_neighbourhood):
        if current_neighbourhood.nei_seed is None:
            seed = 1
        else:
            seed = current_neighbourhood.nei_seed

        systems = ['Single'] * (self.systems('single')) + ['Binary'] * self.systems('binary')
        systems += ['Triple'] * self.systems('triple') + ['Multiple'] * self.systems('multiple')

        divisor = 2 ** 31 - 1
        constant = 48271

        initial_value = (constant * seed) % divisor
        r_raw = initial_value
        distances = []
        for i, system in enumerate(systems):
            if len(current_neighbourhood.pre_processed_system_positions[system]):
                x, y, z = current_neighbourhood.pre_processed_system_positions[system].pop()
            else:
                p_raw = constant * r_raw % divisor
                w_raw = constant * p_raw % divisor
                r_raw = constant * w_raw % divisor

                p_normal = p_raw / divisor
                w_normal = w_raw / divisor
                r_normal = r_raw / divisor

                p = p_normal ** (1 / 3) * self.radius.m
                w = w_normal * 2 * pi
                r = acos(2 * r_normal - 1)

                x = round(p * sin(r) * cos(w), 2)
                y = round(p * sin(r) * sin(w), 2)
                z = round(p * cos(r), 2)

            distances.append({'configuration': systems[i], 'pos': [x, y, z]})

        return distances


class NeighbourhoodButton(Meta):
    enabled = True

    def __init__(self, parent, nei_object):
        super().__init__(parent)
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.object_data = nei_object
        text = f"{str(nei_object)}@{nei_object.location}"
        self.img_uns = self.f1.render(text, True, COLOR_TEXTO)
        self.img_sel = self.f2.render(text, True, COLOR_TEXTO)

        self.image = self.img_uns
        self.rect = self.image.get_rect()
        self.max_w = self.img_sel.get_width()

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            location = self.object_data.location
            radius = self.object_data.radius
            self.parent.get_values(location, radius)
            self.parent.select_one(self)
            self.parent.button_add.disable()
            # esto está un poco sucio porque se está está poniendo por afuera.
            self.parent.parent.swap_neighbourhood_button.current = self.object_data
            Universe.current_galaxy.current_neighbourhood = self.object_data

    def move(self, x, y):
        self.rect.topleft = x, y


class AddNeighbourhoodButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set Neighbourhood', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.create_neighbourhood()
            self.parent.clear()
            self.disable()

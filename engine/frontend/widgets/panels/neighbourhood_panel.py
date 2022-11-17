from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, COLOR_AREA, COLOR_TEXTO, NUEVA_LINEA
from engine.frontend.widgets import ValueText, BaseWidget, Meta
from engine.frontend.widgets.panels.common import TextButton
from engine.equations.stellar_neighbourhood import *
from engine.backend.eventhandler import EventHandler
from engine.equations.galaxy import Galaxy
from pygame import Surface, draw, Rect


class NeighbourhoodPanel(BaseWidget):
    skippable = True
    skip = False

    locked = False

    show_swawp_system_button = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Neighbourhood'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()
        title_font = self.crear_fuente(16, underline=True)
        subtitle_font = self.crear_fuente(14, underline=True)
        self.write(self.name + ' Panel', title_font, centerx=(ANCHO // 4) * 1.5, y=0)
        self.galaxy = GalaxyType(self)
        self.neighbourhood = NeighbourhoodType(self)

        self.area_buttons = Rect(0, 420, self.rect.w, 200)
        self.image.fill(COLOR_AREA, self.area_buttons)
        self.write('Systems', subtitle_font, COLOR_AREA, x=3, top=self.area_buttons.top)

        self.current = None

        self.text_size = 16

        rect = self.write('Galactic Characteristics', title_font, x=3, y=30)
        texts = ['Radius', 'Habitable Zone inner limit', 'Habitable Zone outer limit']
        for i, text in enumerate(texts):
            value = ValueText(self.galaxy, text, 3, i * 20 + rect.bottom, size=self.text_size)
            if i == 0:
                value.enable()
                value.modifiable = True
            self.properties.add(value, layer=1)

        rect = draw.aaline(self.image, (0, 0, 0), [3, len(texts) * 20 + 55], [self.rect.w - 3, len(texts) * 20 + 55])

        texts = ['Distance from galactic core', 'Radius']
        rect = self.write('Neighbourhood Characteristics', title_font, x=3, y=rect.bottom + 5)
        for i, text in enumerate(texts):
            value = ValueText(self.neighbourhood, text, 3, i * 20 + rect.bottom, size=self.text_size)
            value.modifiable = True
            self.properties.add(value, layer=2)

        value = ValueText(self.neighbourhood, 'Density', 400, rect.bottom, size=self.text_size)
        self.properties.add(value, layer=2)

        self.button_add = AddNeighbourhoodButton(self, ANCHO - 15, 416)
        self.properties.add(self.button_add, layer=6)

        EventHandler.register(self.clear, 'ClearData')

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

    def create_button(self):
        widgets = self.properties.get_widgets_from_layer(2)
        location = widgets[0].value
        radius = widgets[1].value
        data = {'location': location, 'radius': radius}
        object_data = DefinedNeighbourhood(data)
        button = NeighbourhoodButton(self, object_data)
        self.properties.add(button, layer=5)
        self.sort_buttons(self.properties.get_widgets_from_layer(5))

    def get_values(self, location, radius):
        denstiy = self.galaxy.characteristics.get_density_at_location(location)
        loc_text, rad_text, den_text = self.properties.get_widgets_from_layer(2)
        loc_text.value = str(location)
        rad_text.value = str(radius)
        den_text.value = str(round(denstiy, 3))
        self.neighbourhood.fill()

    def create_neighbourhood(self):
        buttons = self.neighbourhood.characteristics.individual_stars
        galaxy = self.galaxy.characteristics
        galaxy.add_proto_stars(buttons)
        self.create_button()

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

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()


class GalaxyType(BaseWidget):
    locked = False

    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.characteristics = Galaxy()

    def fill(self):
        widgets = self.parent.properties.get_widgets_from_layer(1)
        radius_text = widgets[0]
        self.characteristics.set_radius(float(radius_text.value))
        widgets[0].value = self.characteristics.radius
        widgets[1].value = self.characteristics.inner
        widgets[2].value = self.characteristics.outer

        widgets = self.parent.properties.get_widgets_from_layer(2)
        widgets[0].set_min_and_max(self.characteristics.inner.m, self.characteristics.outer.m)
        widgets[2].value = 'Unknown'
        for widget in widgets:
            widget.enable()


class NeighbourhoodType(BaseWidget):
    locked = False
    location_valid, radius_valid = False, False

    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.characteristics = StellarNeighbourhood(self)
        self.title_font = self.crear_fuente(16, underline=True)
        self.values = {}

    def fill(self):
        widgets = self.parent.properties.get_widgets_from_layer(2)
        location_text, radius_text, density_text = widgets

        if type(location_text.value) in (str, float) and location_text.value != '':
            self.parent.galaxy.characteristics.validate_position(float(location_text.value))
            density = self.characteristics.set_location(float(location_text.value))
            location_text.value = q(location_text.value, 'ly')
            self.location_valid = True
            location_text.editable = False
            density_text.value = str(round(density, 3))

        if type(radius_text.value) in (str, float) and radius_text.value != '':
            self.characteristics.set_radius(float(radius_text.value))
            radius_text.value = self.characteristics.radius
            self.radius_valid = True

        if self.location_valid and self.radius_valid:
            self.clear()
            self.populate()
            self.has_values = True
            self.parent.button_add.enable()

    def clear(self):
        for name in self.values:
            value = self.values[name]
            value.clear()

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
        if 'Total Stars' not in self.values:
            value_text = ValueText(self, 'Total Stars', 230, 8 * 20 + rect_stars.bottom, size=15)
            self.values['Total Stars'] = value_text
            value_text.value = ''
        else:
            value_text = self.values['Total Stars']
            value_text.value = str(int(total_stars))
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

        total_systems = self.characteristics.totals('systems')
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


class NeighbourhoodButton(Meta):
    enabled = True

    def __init__(self, parent, nei_object, size=16):
        super().__init__(parent)
        self.f1 = self.crear_fuente(size)
        self.f2 = self.crear_fuente(size, bold=True)
        self.object_data = nei_object
        text = f"Neighbourhood @{nei_object.location}"
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

    def move(self, x, y):
        self.rect.topleft = x, y
    #
    # def __repr__(self):
    #     return f'{self.name} Button @ {self.position}'
    #


class AddNeighbourhoodButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set Neighbourhood', x, y)
        self.rect.right = x

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.create_neighbourhood()
            self.parent.clear()

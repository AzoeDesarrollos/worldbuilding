from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, COLOR_AREA, COLOR_TEXTO, NUEVA_LINEA
from engine.frontend.widgets import ValueText, BaseWidget, Meta
from engine.equations.stellar_neighbourhood import *
from pygame import Surface, draw, Rect, SRCALPHA
from random import shuffle


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
        self.write(self.name + ' Panel', title_font, centerx=(ANCHO // 4) * 1.5, y=0)
        # self.dice = Dice(self, 3, 10)
        # self.properties.add(self.dice, layer=3)
        self.galaxy = GalaxyType(self)
        self.neighbourhood = NeighbourhoodType(self)

        self.area_buttons = Rect(0, 435, self.parent.rect.w, 163)
        self.image.fill(COLOR_AREA, self.area_buttons)

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
            value.enable()
            value.modifiable = True
            self.properties.add(value, layer=2)

        value = ValueText(self.neighbourhood, 'Density', 400, rect.bottom, size=self.text_size)
        value.enable()
        value.modifiable = True
        self.properties.add(value, layer=2)

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

    def kill_buttons(self):
        for button in self.properties.get_widgets_from_layer(5):
            button.kill()
        self.properties.clear_layer(5)

        self.current = None
        self.image.fill(COLOR_AREA, self.area_buttons)

    def clear(self):
        self.image.fill(COLOR_BOX, [3, 141, self.rect.w, 292])

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()


class GalaxyType(BaseWidget):
    locked = False

    has_values = False

    def __init__(self, parent):
        super().__init__(parent)
        self.characteristics = GalacticCharacteristics(self)

    def fill(self):
        widgets = self.parent.properties.get_widgets_from_layer(1)
        radius_text = widgets[0]
        self.characteristics.set_radius(float(radius_text.value))
        widgets[0].value = self.characteristics.radius
        widgets[1].value = self.characteristics.inner
        widgets[2].value = self.characteristics.outer

        widget = self.parent.properties.get_widgets_from_layer(2)[0]
        widget.set_min_and_max(self.characteristics.inner.m, self.characteristics.outer.m)


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

    def clear(self):
        self.parent.clear()
        for name in self.values:
            value = self.values[name]
            value.clear()

    def populate(self):
        rect_stars = self.parent.write('Stars in vicinity', self.title_font, x=3, y=185)
        rect_systems = self.parent.write('Stars Systems in vicinity', self.title_font, x=230, y=185)

        positions = self.characteristics.system_positions(self.parent.dice.seed)
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
            else:
                value_text = self.values[clase]
            value_text.value = str(quantity) if quantity > 0 else 'None'
            self.parent.properties.add(value_text, layer=4)
            value_text.show()

        total_stars = self.characteristics.totals('stars')
        if 'Total Stars' not in self.values:
            value_text = ValueText(self, 'Total Stars', 3, len(types) * 20 + 210, size=15)
            self.values['Total Stars'] = value_text
        else:
            value_text = self.values['Total Stars']
        value_text.value = str(int(total_stars)) if total_stars > 0 else 'None'
        self.parent.properties.add(value_text, layer=4)
        value_text.show()

        comps = ['single', 'binary', 'triple', 'multiple']
        singles = [x['pos'] for x in positions if x['configuration'] == 'Single']
        binaries = [x['pos'] for x in positions if x['configuration'] == 'Binary']
        triples = [x['pos'] for x in positions if x['configuration'] == 'Triple']
        multiples = [x['pos'] for x in positions if x['configuration'] == 'Multiple']
        d = {'single': singles, 'binary': binaries, 'triple': triples, 'multiple': multiples}
        for i, comp in enumerate(comps):
            name = f'{comp.title()} Star Systems'
            quantity = self.characteristics.systems(comp)
            if name not in self.values:
                value_text = ValueText(self, name, 230, i * 50 + rect_systems.bottom, size=14)
                self.values[name] = value_text
            else:
                value_text = self.values[name]
            value_text.value = str(quantity) if quantity > 0 else 'None'
            self.parent.properties.add(value_text, layer=4)
            value_text.show()
            for each in range(quantity):
                system_position = d[comp][each]
                system = SystemButton(self.parent, comp.title(), system_position, size=15)
                self.parent.properties.add(system, layer=5)
                system.show()

        systems = self.parent.properties.get_widgets_from_layer(5)
        for _ in range(5):
            shuffle(systems)
        self.parent.sort_buttons(systems)

        total_systems = self.characteristics.totals('systems')
        if 'Total Systems' not in self.values:
            value_text = ValueText(self, 'Total Systems', 230, len(types) * 20 + 210, size=14)
            self.values['Total Systems'] = value_text
        else:
            value_text = self.values['Total Systems']
        value_text.value = str(int(total_systems)) if total_systems > 0 else 'None'
        self.parent.properties.add(value_text, layer=4)
        value_text.show()


class Dice(Meta):
    enabled = True
    seed = 1

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.img_uns = self.crear((100, 100, 100), (0, 0, 0))
        self.img_sel = self.crear((255, 255, 255), (0, 0, 0))
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    @staticmethod
    def crear(fondo, lineas):
        canvas = Surface((33, 33), SRCALPHA)
        alto = 13

        a = 16, 1
        b = 24, alto // 2
        c = 8, alto // 2
        d = 16, a[1] + alto - 3
        e = 8, b[1] + alto
        f = 24, b[1] + alto
        g = 16, d[1] + alto

        draw.polygon(canvas, fondo, [a, b, d, c])
        draw.polygon(canvas, fondo, [b, f, g, d])
        draw.polygon(canvas, fondo, [c, d, g, e])

        draw.aaline(canvas, lineas, a, b)
        draw.aaline(canvas, lineas, a, c)
        draw.aaline(canvas, lineas, b, d)
        draw.aaline(canvas, lineas, c, d)
        draw.aaline(canvas, lineas, d, g)
        draw.aaline(canvas, lineas, b, f)
        draw.aaline(canvas, lineas, c, e)
        draw.aaline(canvas, lineas, e, g)
        draw.aaline(canvas, lineas, f, g)

        return canvas

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.seed += 1
            if self.parent.neighbourhood.has_values:
                self.parent.kill_buttons()
                self.parent.neighbourhood.fill()


class SystemButton(Meta):
    enabled = True

    def __init__(self, parent, name, pos, size=16):
        super().__init__(parent)
        self.f1 = self.crear_fuente(size)
        self.f2 = self.crear_fuente(size, bold=True)
        self.img_dis = self.f1.render(name, True, COLOR_TEXTO)
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO)

        self.image = self.img_dis
        self.rect = self.image.get_rect()
        self.max_w = self.img_sel.get_width()

        self.position = pos
        self.name = name

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            x, y, z = self.position
            if x == 0 and y == 0 and z == 0:
                sub = 'Home'
            else:
                sub = self.name
            raise AssertionError(f'{sub} Star System @\n ({x}, {y}, {z})')

    def move(self, x, y):
        self.rect.topleft = x, y

    def __repr__(self):
        return f'{self.name} Button @ {self.position}'

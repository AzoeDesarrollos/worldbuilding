from engine.frontend.widgets import BaseWidget, Meta
from engine.equations.stellar_neighbourhood import *
from pygame import Surface, draw, Rect
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, COLOR_AREA
from engine.frontend.widgets import ValueText


class NeighbourhoodPanel(BaseWidget):
    skippable = True
    skip = False

    locked = False

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Neighbourhood'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()

        self.properties.add(Dice(self, 3, 10), layer=3)
        self.galaxy = GalaxyType(self)
        self.neighbourhood = NeighbourhoodType(self)

        texts = ['Galactic Radius', 'Galactic Habitable Zone inner limit', 'Galactic Habitable Zone inner outer']
        for i, text in enumerate(texts):
            value = ValueText(self.galaxy, text, 3, i * 20 + 60)
            if i == 0:
                value.enable()
                value.modifiable = True
            self.properties.add(value, layer=1)

        draw.aaline(self.image, (0, 0, 0), [3, len(texts) * 20 + 80], [self.rect.w - 3, len(texts) * 20 + 80])

        texts = ['Location', 'Radius']
        for i, text in enumerate(texts):
            value = ValueText(self.neighbourhood, text, 3, i * 20 + 150)
            value.enable()
            value.modifiable = True
            self.properties.add(value, layer=2)

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


class NeighbourhoodType(BaseWidget):
    locked = False
    location_valid, radius_valid = False, False

    def __init__(self, parent):
        super().__init__(parent)
        self.characteristics = StellarNeighbourhood(self)
        self.systems_area = Rect(0, 435, self.parent.rect.w, 163)
        self.parent.image.fill(COLOR_AREA, self.systems_area)

    def fill(self):
        widgets = self.parent.properties.get_widgets_from_layer(2)
        location_text, radius_text = widgets

        if type(location_text.value) is str and location_text.value != '':
            self.parent.galaxy.characteristics.validate_position(float(location_text.value))
            location_text.value = q(location_text.value, 'ly')
            self.location_valid = True

        if type(radius_text.value) is str and radius_text.value != '':
            self.characteristics.set_radius(float(radius_text.value))
            radius_text.value = self.characteristics.radius
            self.radius_valid = True

        if self.location_valid and self.radius_valid:
            self.populate()

    def populate(self):
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
            value_text = ValueText(self, clase, 3, i * 20 + 200)
            value_text.value = str(quantity) if quantity > 0 else 'None'
            self.parent.properties.add(value_text, layer=4)
            value_text.show()

        total_stars = self.characteristics.totals('stars')
        value_text = ValueText(self, 'Total Stars', 3, len(types) * 20 + 210)
        value_text.value = str(int(total_stars)) if total_stars > 0 else 'None'
        self.parent.properties.add(value_text, layer=4)
        value_text.show()

        total_systems = self.characteristics.totals('systems')
        value_text = ValueText(self, 'Total Systems', 230, len(types) * 20 + 210)
        value_text.value = str(int(total_systems)) if total_systems > 0 else 'None'
        self.parent.properties.add(value_text, layer=4)
        value_text.show()


class Dice(Meta):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.img_uns = self.crear((100, 100, 100), (0, 0, 0))
        self.img_sel = self.crear((255, 255, 255), (0, 0, 0))
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    @staticmethod
    def crear(fondo, lineas):
        canvas = Surface((33, 33))
        canvas.fill(COLOR_BOX)
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

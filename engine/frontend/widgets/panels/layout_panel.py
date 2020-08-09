from engine.equations.planetary_system import PlanetarySystem
from engine.frontend.globales import Renderer, WidgetHandler
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, draw, transform, SRCALPHA, font
from engine.frontend.globales import ALTO, ANCHO, WidgetGroup, COLOR_TEXTO, COLOR_BOX
from engine.frontend.widgets import panels
from .planet_panel import Meta


class LayoutPanel(BaseWidget):
    system = None
    curr_idx = 0

    def __init__(self):
        super().__init__()
        self.image = Surface((ANCHO, ALTO))
        self.image.fill((125, 125, 125))
        self.rect = self.image.get_rect()
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

        self.panels = []
        self.properties = WidgetGroup()
        for panel in panels:
            self.panels.append(panel(self))

        self.current = self.panels[self.curr_idx]
        self.current.show()

        a = Arrow(self, 'backward', 180, self.rect.left + 16, self.rect.bottom)
        b = Arrow(self, 'forward', 0, self.rect.right - 16, self.rect.bottom)
        c = SaveButton(self, self.rect.centerx, self.rect.bottom-26)
        # noinspection PyTypeChecker
        self.properties.add(a, b, layer=3)
        Renderer.add_widget(a)
        Renderer.add_widget(b)
        Renderer.add_widget(c)
        WidgetHandler.add_widget(c)

    def cycle(self, delta):
        self.current.hide()
        if 0 <= self.curr_idx+delta < len(self.panels):
            self.curr_idx += delta
            self.current = self.panels[self.curr_idx]
        self.current.show()

    def set_system(self, star):
        for arrow in self.properties.get_widgets_from_layer(3):
            arrow.enable()
        self.system = PlanetarySystem(star)


class Arrow(Meta, BaseWidget):
    def __init__(self, parent, direccion, angulo, centerx, y):
        super().__init__(parent)
        WidgetHandler.add_widget(self)
        self.direccion = direccion

        self.img_uns = self.create((255, 0, 0, 255), angulo)
        self.img_sel = self.create((0, 0, 255, 255), angulo)
        self.img_dis = self.create((200, 200, 200, 222), angulo)

        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=centerx, bottom=y)

    @staticmethod
    def create(color, angulo):
        img = Surface((32, 32), SRCALPHA)
        draw.polygon(img, color, [[1, 13], [20, 13], [20, 5], [30, 14], [20, 26], [20, 18], [1, 17]])
        image = transform.rotate(img, angulo)
        return image

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.enabled:
                    if self.direccion == 'forward':
                        self.parent.cycle(+1)
                    elif self.direccion == 'backward':
                        self.parent.cycle(-1)


class SaveButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        f1 = font.SysFont('Verdana', 16)
        f2 = font.SysFont('Verdana', 16, bold=1)
        self.img_uns = f1.render('Guardar', True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = f2.render('Guardar', True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=x, y=y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            pass

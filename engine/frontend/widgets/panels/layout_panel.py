from engine.frontend.globales import ALTO, ANCHO, WidgetGroup, COLOR_TEXTO, COLOR_BOX
from engine.frontend.globales import Renderer, WidgetHandler
from pygame import Surface, draw, transform, SRCALPHA, font
from engine.frontend.widgets.basewidget import BaseWidget
from engine.backend.util import guardar_json, abrir_json
from engine.equations.planetary_system import system
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets import panels
from .planet_panel import Meta


class LayoutPanel(BaseWidget):
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

        c = SaveButton(self, 450, self.rect.bottom - 26)
        d = LoadButton(self, 300, self.rect.bottom - 26)
        e = NewButton(self, 150, self.rect.bottom - 26)

        # noinspection PyTypeChecker
        self.properties.add(a, b, layer=3)
        Renderer.add_widget(a)
        Renderer.add_widget(b)

        # noinspection PyTypeChecker
        self.properties.add(e, layer=4)
        Renderer.add_widget(c)
        Renderer.add_widget(d)
        Renderer.add_widget(e)

        WidgetHandler.add_widget(c)
        WidgetHandler.add_widget(d)
        WidgetHandler.add_widget(e)

    def cycle(self, delta):
        self.current.hide()
        if 0 <= self.curr_idx + delta < len(self.panels):
            self.curr_idx += delta
            self.current = self.panels[self.curr_idx]
        self.current.show()

    def set_system(self, star):
        for arrow in self.properties.get_widgets_from_layer(3):
            arrow.enable()
        self.properties.get_widgets_from_layer(4)[0].enable()
        system.set_star(star)


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


class BaseButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, x, y, text):
        super().__init__(parent)
        f1 = font.SysFont('Verdana', 16)
        f2 = font.SysFont('Verdana', 16, bold=1)
        self.img_uns = f1.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = f2.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=x, y=y)


class SaveButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Guardar')

    def on_mousebuttondown(self, event):
        if event.button == 1:
            data = system.return_data()
            guardar_json('D:/Python/worldbuilding/data/savedata.json', data)


class LoadButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Cargar')

    def on_mousebuttondown(self, event):
        if event.button == 1:
            data = abrir_json('D:/Python/worldbuilding/data/savedata.json')
            EventHandler.trigger('LoadData', 'LoadButton', data)


class NewButton(BaseButton):
    enabled = False

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Nuevo')

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            EventHandler.trigger('ClearData', 'NewButton', {'panel': self.parent.current})

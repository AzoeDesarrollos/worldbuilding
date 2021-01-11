from engine.frontend.globales import ALTO, ANCHO, WidgetGroup, COLOR_TEXTO, COLOR_BOX
from engine.frontend.globales import Renderer, WidgetHandler
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, draw, transform, SRCALPHA
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.backend.util import abrir_json
from engine.frontend.widgets import panels
from os.path import exists, join
from .planet_panel import Meta
from os import getcwd


class LayoutPanel(BaseWidget):
    curr_idx = 0

    def __init__(self):
        super().__init__()
        self.image = Surface((ANCHO, ALTO))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.show()

        Systems.init()

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

        f = SwapSystem(self, ANCHO-200, 2)

        self.properties.add(a, b, layer=3)
        Renderer.add_widget(a)
        Renderer.add_widget(b)

        self.properties.add(e, layer=4)
        Renderer.add_widget(c)
        Renderer.add_widget(d)
        Renderer.add_widget(e)

        self.properties.add(f, layer=4)

        WidgetHandler.add_widget(c)
        WidgetHandler.add_widget(d)
        WidgetHandler.add_widget(e)

    def cycle(self, delta):
        self.current.hide()
        if 0 <= self.curr_idx + delta < len(self.panels):
            self.curr_idx += delta
            self.current = self.panels[self.curr_idx]
            if self.current.skippable is True and self.current.skip is True:
                self.cycle(delta)
                return  # si se saltea un panel, no hay que mostrar el panel siguiente 2 veces.
        self.current.show()

    def set_skippable(self, name, value):
        panel = [i for i in self.panels if i.name == name][0]
        panel.skip = value

    def __repr__(self):
        return 'Layout Panel'


class Arrow(Meta, BaseWidget):
    enabled = True

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

    def __repr__(self):
        return 'Arrow ({})'.format(self.direccion)


class BaseButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, x, y, text):
        super().__init__(parent)
        f1 = self.crear_fuente(16)
        f2 = self.crear_fuente(16, bold=True)
        self.img_uns = f1.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = f2.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=x, y=y)


class SaveButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Guardar')

    def on_mousebuttondown(self, event):
        if event.button == 1:
            EventHandler.trigger('Save', 'SaveButton', {})


class LoadButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Cargar')

    def on_mousebuttondown(self, event):
        ruta = join(getcwd(), 'data', 'savedata.json')
        if event.button == 1 and exists(ruta):
            data = abrir_json(ruta)
            if len(data):
                EventHandler.trigger('LoadData', 'LoadButton', data)


class NewButton(BaseButton):

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Nuevo')

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            EventHandler.trigger('ClearData', 'NewButton', {'panel': self.parent.current})


class SwapSystem(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.layer = 7
        self.f1 = self.crear_fuente(13, bold=True)
        self.f2 = self.crear_fuente(13)
        self.img_sel = self.f1.render('System: ', True, COLOR_TEXTO, COLOR_BOX)
        self.img_uns = self.f2.render('System: ', True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        self.system_image = SystemName(self, left=self.rect.right+6, y=2)
        self.show()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            Systems.cycle_systems()


class SystemName(BaseWidget):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.f = self.crear_fuente(13)
        self.image = self.f.render(str(Systems.get_current_star()), True, COLOR_TEXTO, COLOR_BOX)
        self._rect = self.image.get_rect(**kwargs)
        self.rect = self._rect.copy()
        self.show()

    def update(self):
        self.image = self.f.render(str(Systems.get_current_star()), True, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=self._rect.topleft)

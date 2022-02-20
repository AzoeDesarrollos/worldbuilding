from engine.frontend.globales import ALTO, ANCHO, COLOR_TEXTO, COLOR_SELECTED, COLOR_BOX, COLOR_DISABLED
from engine.frontend.globales import Renderer, WidgetHandler
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, draw, transform, SRCALPHA
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets.meta import Meta
from engine.backend.util import abrir_json
from os.path import exists, join
from os import getcwd
from . import panels


class LayoutPanel(BaseWidget):
    curr_idx = 0

    def __init__(self):
        super().__init__()
        self.image = Surface((ANCHO, ALTO))
        self.image.fill(COLOR_SELECTED)
        self.rect = self.image.get_rect()
        self.show()
        self.name = 'Layout'

        Systems.init()

        self.panels = []
        for panel in panels:
            self.panels.append(panel(self))

        self.current = self.panels[self.curr_idx]
        self.current.show()

        a = Arrow(self, 'backward', 180, self.rect.left + 16, self.rect.bottom)
        b = Arrow(self, 'forward', 0, self.rect.right - 16, self.rect.bottom)

        e = NewButton(self, (self.rect.w//6)*1+32, self.rect.bottom - 26)
        d = LoadButton(self, (self.rect.w//6)*3, self.rect.bottom - 26)
        c = SaveButton(self, (self.rect.w//6)*5-32, self.rect.bottom - 26)

        SwapSystem(self, ANCHO-200, 2)

        Renderer.add_widget(a)
        Renderer.add_widget(b)
        Renderer.add_widget(c)
        Renderer.add_widget(d)
        Renderer.add_widget(e)

        WidgetHandler.add_widget(c)
        WidgetHandler.add_widget(d)
        WidgetHandler.add_widget(e)

        self.load_button = d

        EventHandler.register(self.show_current, 'SwitchMode')

    def show_current(self, event):
        if event.data['mode'] == 1:
            self.current.show()

    def cycle(self, delta):
        if self.curr_idx + delta < 0:
            self.curr_idx = len(self.panels)-1
        elif self.curr_idx + delta > len(self.panels)-1:
            self.curr_idx = 0
        else:
            self.curr_idx += delta

        self.current.hide()
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


class Arrow(Meta):
    enabled = True

    def __init__(self, parent, direccion, angulo, centerx, y):
        super().__init__(parent)
        WidgetHandler.add_widget(self)
        self.direccion = direccion

        self.img_uns = self.create(COLOR_BOX, angulo)
        self.img_sel = self.create(COLOR_TEXTO, angulo)
        self.img_dis = self.create(COLOR_DISABLED, angulo)

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


class BaseButton(Meta):
    enabled = True

    def __init__(self, parent, x, y, text):
        super().__init__(parent)
        f1 = self.crear_fuente(16)
        f2 = self.crear_fuente(16, bold=True)
        self.img_uns = f1.render(text, True, COLOR_TEXTO, COLOR_SELECTED)
        self.img_sel = f2.render(text, True, COLOR_TEXTO, COLOR_SELECTED)
        self.img_dis = f1.render(text, True, COLOR_DISABLED, COLOR_SELECTED)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=x, y=y)


class SaveButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Save')

    def on_mousebuttondown(self, event):
        if event.button == 1:
            EventHandler.trigger('Save', 'SaveButton', {})
            self.parent.load_button.enable()


class LoadButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Load')

    def on_mousebuttondown(self, event):
        ruta = join(getcwd(), 'data', 'savedata.json')
        if event.button == 1 and exists(ruta):
            data = abrir_json(ruta)
            if len(data):
                EventHandler.trigger('LoadData', 'LoadButton', data)


class NewButton(BaseButton):

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'New')

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            EventHandler.trigger('ClearData', 'NewButton', {'panel': self.parent.current})


class SwapSystem(Meta):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.layer = 7
        self.f1 = self.crear_fuente(13, bold=True)
        self.f2 = self.crear_fuente(13)
        self.img_sel = self.f1.render('System: ', True, COLOR_TEXTO, COLOR_BOX)
        self.img_uns = self.f2.render('System: ', True, COLOR_TEXTO, COLOR_BOX)
        self.img_dis = self.f1.render('System: ', True, COLOR_DISABLED, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        self.system_image = SystemName(self, left=self.rect.right+6, y=2)
        self.show()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            Systems.cycle_systems()

    def update(self):
        super().update()
        if not len(Systems.get_systems()):
            self.disable()
        elif not self.enabled and 'Star' not in self.parent.current.name:
            self.enable()


class SystemName(BaseWidget):
    color = COLOR_DISABLED

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.f = self.crear_fuente(13)

        self.image = self.f.render(self.get_name(), True, COLOR_TEXTO, COLOR_BOX)
        self._rect = self.image.get_rect(**kwargs)
        self.rect = self._rect.copy()
        self.show()

    def get_name(self):
        if 'Star' in self.parent.parent.current.name:
            name = None
        else:
            star = Systems.get_current_star()
            if star is not None and star.has_name:
                name = star.name
            else:
                name = str(star)

        if name is None:
            self.color = COLOR_DISABLED
            name = '-'
        elif name == 'None':
            self.color = COLOR_DISABLED
        else:
            self.color = COLOR_TEXTO
        return name

    def update(self):
        self.image = self.f.render(self.get_name(), True, self.color, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=self._rect.topleft)

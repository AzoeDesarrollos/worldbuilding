from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group
from engine.frontend.widgets import BaseWidget
from engine.backend.config import Config
from pygame import Surface, Rect
from .common import RadioButton


class StartPanel(BaseWidget):
    skippable = True
    skip = True

    show_swap_system_button = False

    def __init__(self, parent):
        self.name = 'Start'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.properties = Group()
        rect_a = Rect(0, 0, self.rect.w // 2, ALTO)
        rect_b = Rect(self.rect.centerx, 0, self.rect.w // 2, ALTO)
        self.button_a = RadioButton(self, rect_a.centerx, rect_a.centery - 50)
        self.button_b = RadioButton(self, rect_b.centerx, rect_b.centery - 50)

        self.properties.add(self.button_a, self.button_b, layer=1)

        text_intro = 'Welcome to WorldBuilding, an app for worldbuilders.'
        text_intro += '\n\nPlease select the mode you wish to use:'

        text_a = 'This mode will limit the mass available to create celestial bodies within a system.'
        text_a += ' The more stars a system have, the less mass is available to create planets for that system.'

        text_b = 'This mode allows for the creation of celestial bodies without taking into consideration the mass they'
        text_b += ' need to be created.'

        f = self.crear_fuente(16, bold=True, underline=True)
        f0 = self.crear_fuente(11)
        f2 = self.crear_fuente(14)
        f3 = self.crear_fuente(14, bold=True)
        self.f = f2

        r = self.write2('W O R L D B U I L D I N G', f, self.rect.w, centerx=self.rect.centerx, y=50, j=True)
        self.write2('v2022', f0, self.rect.w, centerx=self.rect.centerx, top=r.bottom, j=True)

        self.write2(text_intro, f2, self.rect.w, centerx=self.rect.centerx, y=self.rect.centery - 200, j=True)

        self.write('Restricted Mode', f3, centerx=self.button_a.rect.centerx, bottom=self.button_a.rect.top - 10)
        self.write('Unrestricted Mode', f3, centerx=self.button_b.rect.centerx, bottom=self.button_b.rect.top - 10)

        self.write2(text_a, f2, rect_a.w - 10, x=3, y=self.button_a.rect.bottom + 5, j=True)
        self.write2(text_b, f2, rect_a.w - 10, x=rect_b.x + 10, y=self.button_b.rect.bottom + 5, j=True)

        mode = Config.get('mode')
        selected = None
        if mode == 0:
            selected = self.button_a
        elif mode == 1:
            selected = self.button_b

        if selected is not None:
            self.select_one(selected)

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if any([self.button_a.on, self.button_b.on]):
                if self.button_a.on:
                    Config.set('mode', 0)
                elif self.button_b.on:
                    Config.set('mode', 1)
                self.hide()
                self.parent.cycle(+1)

    def hide(self):
        super().hide()
        for widget in self.properties.get_widgets_from_layer(1):
            widget.hide()
        self.parent.show()

    def show(self):
        super().show()
        for widget in self.properties.get_widgets_from_layer(1):
            widget.show()

    def select_one(self, selected):
        for each in self.properties.get_widgets_from_layer(1):
            each.deselect()
        selected.select()

        if selected is self.button_a:
            Config.set('mode', 0)
        else:
            Config.set('mode', 1)

        self.write2('Click anywhere to continue.', self.f, self.rect.w, centerx=self.rect.centerx, y=400, j=True)

from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group
from engine.frontend.widgets import BaseWidget
from pygame import Surface


class StartPanel(BaseWidget):
    skippable = True
    _skip = True

    show_swap_system_button = False

    def __init__(self, parent):
        self.name = 'Start'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.properties = Group()
        text_intro = 'Welcome to WorldBuilding, an app for worldbuilders.'

        f = self.crear_fuente(16, bold=True, underline=True)
        f0 = self.crear_fuente(11)
        f2 = self.crear_fuente(14)
        self.f = f2

        r = self.write2('W O R L D B U I L D I N G', f, self.rect.w, centerx=self.rect.centerx, y=50, j=True)
        self.write2('v2024', f0, self.rect.w, centerx=self.rect.centerx, top=r.bottom, j=True)

        self.write2(text_intro, f2, self.rect.w, centerx=self.rect.centerx, y=self.rect.centery - 200, j=True)

        self.write2('Click anywhere to continue.', self.f, self.rect.w, centerx=self.rect.centerx, y=400, j=True)

    @property
    def skip(self):
        return self._skip

    @skip.setter
    def skip(self, value):
        self._skip = value

    def on_mousebuttondown(self, event):
        if event.origin == self:
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



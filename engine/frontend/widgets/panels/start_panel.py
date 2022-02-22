from engine.frontend.widgets import BaseWidget
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX
from pygame import Surface


class StartPanel(BaseWidget):
    skippable = True
    skip = True

    def __init__(self, parent):
        self.name = 'Naming'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

    def on_mousebuttondown(self, event):
        self.hide()
        self.parent.cycle(+1)

    def hide(self):
        super().hide()
        self.parent.show()

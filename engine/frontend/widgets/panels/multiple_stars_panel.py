from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX
from ..basewidget import BaseWidget
from pygame import Surface


class MultipleStarsPanel(BaseWidget):
    skippable = True
    skip = False

    def __init__(self, parent):
        self.name = 'Multiple Stars'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)

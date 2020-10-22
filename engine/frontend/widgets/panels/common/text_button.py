from engine.frontend.globales import COLOR_BOX, COLOR_TEXTO
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import font
from .meta import Meta


class TextButton(Meta, BaseWidget):
    def __init__(self, parent, text, x, y):
        super().__init__(parent)
        self.f1 = font.SysFont('Verdana', 16)
        self.f2 = font.SysFont('Verdana', 16, bold=True)
        self.img_dis = self.f1.render(text, True, (200, 200, 200), COLOR_BOX)
        self.img_uns = self.f1.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(text, True, COLOR_TEXTO, COLOR_BOX)

        self.image = self.img_dis
        self.rect = self.image.get_rect(bottomleft=(x, y))

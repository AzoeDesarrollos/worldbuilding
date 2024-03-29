from engine.frontend.globales import COLOR_BOX, COLOR_TEXTO
from engine.frontend.widgets.meta import Meta


class TextButton(Meta):
    def __init__(self, parent, text, x, y, font_size=16):
        super().__init__(parent)
        self.f1 = self.crear_fuente(font_size)
        self.f2 = self.crear_fuente(font_size, bold=True)
        self.img_dis = self.f1.render(text, True, (200, 200, 200), COLOR_BOX)
        self.img_uns = self.f1.render(text, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = self.f2.render(text, True, COLOR_TEXTO, COLOR_BOX)

        self.image = self.img_dis
        self.rect = self.image.get_rect(bottomleft=(x, y))

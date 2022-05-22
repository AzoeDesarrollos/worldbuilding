from engine.frontend.globales import COLOR_AREA, COLOR_DISABLED, COLOR_TEXTO
from engine.frontend.widgets.meta import Meta


class ToggleableButton(Meta):
    enabled = True

    def __init__(self, parent, text, method, x, y):
        super().__init__(parent)
        f1 = self.crear_fuente(14)
        f2 = self.crear_fuente(14, bold=True)
        self.img_uns = f1.render(text, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = f2.render(text, True, COLOR_TEXTO, COLOR_AREA)
        self.img_dis = f1.render(text, True, COLOR_DISABLED, COLOR_AREA)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        self.method = method

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.method()

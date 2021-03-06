from engine.frontend.globales import COLOR_TEXTO, COLOR_AREA
from engine.frontend.widgets.basewidget import BaseWidget
from .meta import Meta


class ListedBody(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, body, name, x, y, fg_color=None):
        super().__init__(parent)
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.object_data = body
        if fg_color is None:
            self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
            self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        else:
            self.img_uns = self.f1.render(name, True, fg_color, COLOR_AREA)
            self.img_sel = self.f2.render(name, True, fg_color, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        raise NotImplementedError()

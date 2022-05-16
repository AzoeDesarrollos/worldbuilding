from engine.frontend.globales import COLOR_TEXTO, COLOR_AREA
from engine.frontend.widgets.meta import Meta


class ListedBody(Meta):
    enabled = True
    _color = None

    def __init__(self, parent, body, name, x, y, fg_color=None):
        super().__init__(parent)
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.object_data = body

        if self._color is None and fg_color is None:
            self._color = COLOR_TEXTO
        elif fg_color is not None:
            self._color = fg_color

        self.crear(name)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_w = self.img_sel.get_width()

    def crear(self, name):
        self.img_uns = self.f1.render(name, True, self._color, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, self._color, COLOR_AREA)

    def on_mousebuttondown(self, event):
        raise NotImplementedError()

from engine.frontend.globales import ANCHO, ALTO, COLOR_TEXTO, COLOR_BOX
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, transform
from itertools import cycle


class BasePanel(BaseWidget):
    current = None
    mode = None
    name = None
    skip = False
    skippable = False

    def __init__(self, name, parent, modes=2):
        super().__init__(parent)
        self.name = name
        self.image = Surface((ANCHO, ALTO-32))
        self.rect = self.image.get_rect()

        self.f = self.crear_fuente(16, underline=True)

        f2 = self.crear_fuente(16)
        self.rt1_uns = transform.rotate(f2.render('Relative Values', True, COLOR_TEXTO, COLOR_BOX), 90)
        self.rt1_sel = transform.rotate(f2.render('Absolute Values', True, COLOR_TEXTO, COLOR_BOX), 90)
        rt1_rect = self.rt1_uns.get_rect(x=12, y=70)
        self.relative_text = self.rt1_uns
        self.relative_text_area = rt1_rect.inflate(10, 10)
        self.modes = cycle(list(range(modes)))
        self.mode = next(self.modes)

        rt2 = transform.rotate(f2.render('Absolute Values', True, COLOR_TEXTO, COLOR_BOX), 90)
        rt2_rect = rt2.get_rect(x=6, y=220)

        render = self.f.render(name+' Panel', True, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(centerx=(ANCHO//4)*1.5, y=0)

        self.image.fill(COLOR_BOX)
        self.image.blit(render, render_rect)
        self.image.blit(self.relative_text, self.relative_text_area)
        self.image.blit(rt2, rt2_rect)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            if self.relative_text_area.collidepoint(event.pos):
                self.image.fill(COLOR_BOX, self.relative_text_area)
                self.mode = next(self.modes)
                if self.mode == 1:
                    self.relative_text = self.rt1_sel
                else:
                    self.relative_text = self.rt1_uns

                if self.current.has_values:
                    self.current.fill()
                self.image.blit(self.relative_text, self.relative_text_area)

    def show(self):
        super().show()
        self.current.show()

    def hide(self):
        super().hide()
        self.current.hide()

    def __repr__(self):
        return self.name + ' Panel'

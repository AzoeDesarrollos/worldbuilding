from engine.frontend.globales import ANCHO, ALTO, COLOR_TEXTO, COLOR_AREA
from engine.backend.textrect import render_textrect
from .basewidget import BaseWidget
from pygame import Surface, Rect


class PopUpMessage(BaseWidget):
    def __init__(self, text):
        super().__init__()
        self.layer = 50
        self.image = Surface([200, 200])
        self.rect = self.image.get_rect(center=(ANCHO // 2, (ALTO // 2)-100))
        self.image.fill(COLOR_AREA, [1, 1, self.rect.w - 2, self.rect.h - 2])
        f = self.crear_fuente(14)
        f2 = self.crear_fuente(20)
        message = render_textrect(text, f, self.rect.inflate(-5, -3), COLOR_TEXTO, COLOR_AREA, 1)
        msg_rect = message.get_rect(x=3, centery=self.rect.centery - self.rect.y)
        self.image.blit(message, msg_rect)

        self.image.fill((100, 100, 100), [1, 1, self.rect.w - 2, 25])
        self.write(' X ', f2, (200, 0, 0), right=self.rect.w - 2, y=1)
        self.close_area = Rect(367, self.rect.y, 32, 30)

        self.show()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.close_area.collidepoint(event.pos):
                self.hide()

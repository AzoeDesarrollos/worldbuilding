from engine.frontend.globales import ANCHO, ALTO, COLOR_TEXTO, COLOR_AREA, WidgetHandler
from engine.backend.textrect import render_textrect
from .basewidget import BaseWidget
from pygame import Surface, Rect


class PopUpMessage(BaseWidget):
    blinking = False
    ticks = 0

    def __init__(self, text):
        super().__init__()
        self.layer = 50
        self.image = Surface([200, 200])
        self.rect = self.image.get_rect(center=(ANCHO // 2, (ALTO // 2) - 100))
        self.image.fill(COLOR_AREA, [1, 1, self.rect.w - 2, self.rect.h - 2])
        f = self.crear_fuente(14)
        f2 = self.crear_fuente(20)
        message = render_textrect(text, f, self.rect.inflate(-5, -3), COLOR_TEXTO, COLOR_AREA, 1)
        msg_rect = message.get_rect(x=3, centery=self.rect.centery - self.rect.y)
        self.image.blit(message, msg_rect)

        self.blink_area = self.image.fill((100, 100, 100), [1, 1, self.rect.w - 31, 25])
        self.write(' X ', f2, (200, 0, 0), right=self.rect.w - 2, y=1)
        self.close_area = Rect(367, self.rect.y, 32, 30)

        self.show()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.close_area.collidepoint(event.pos):
                self.hide()
                WidgetHandler.unlock()

    def blink(self):
        self.blinking = True

    def update(self):
        j = 8
        if self.blinking:
            self.ticks += 1
            t = self.ticks
            if (0 < t <= j) or (j*2+1 <= t <= j*3) or (j*4+1 <= t <= j*5) or (j*6+1 <= t <= j*7):
                self.image.fill((200, 50, 0), self.blink_area)
            elif (j+1 <= t <= j*2) or (j*3+1 <= t <= j*4) or (j*5+1 <= t <= j*6) or (j*7+1 <= t <= j*8):
                self.image.fill((255, 255, 0), self.blink_area)
            else:
                self.image.fill((100, 100, 100), self.blink_area)
                self.blinking = False
                self.ticks = 0

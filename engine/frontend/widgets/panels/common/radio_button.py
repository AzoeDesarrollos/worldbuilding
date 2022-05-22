from engine.frontend.globales import COLOR_BOX, COLOR_AREA
from engine.frontend.widgets import BaseWidget
from pygame import Surface, draw


class RadioButton(BaseWidget):
    on = False
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.img_off = self.create()
        self.img_on = self.create(fill=True)
        self.image = self.img_off
        self.rect = self.image.get_rect(center=(x, y))

    @staticmethod
    def create(fill=False):
        radio = 6
        img = Surface((radio * 2, radio * 2))
        img.fill(COLOR_BOX)
        draw.circle(img, 'black', (radio, radio), radio)
        draw.circle(img, COLOR_AREA, (radio, radio), radio - 1)
        if fill:
            draw.circle(img, 'black', (radio, radio), radio-3)
        return img

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.select_one(self)

    def select(self):
        super().select()
        self.image = self.img_on
        self.on = True

    def deselect(self):
        super().deselect()
        self.image = self.img_off
        self.on = False

from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, COLOR_SELECTED, WidgetHandler
from engine.frontend.widgets.meta import Meta
from pygame import Surface, mouse, draw
from engine.backend import EventHandler


class BaseSlider(Meta):
    cursor = None

    def __init__(self, parent, x, y, w):
        super().__init__(parent)

        self.image = Surface((w, 7))
        self.rect = self.image.get_rect(topleft=[x, y])
        self.image.fill(COLOR_BOX, [0, 0, w - 1, 7])
        draw.aaline(self.image, COLOR_TEXTO, [0, 3], [self.rect.w, 3])
        draw.aaline(self.image, COLOR_TEXTO, [0, 0], [0, 7])

    def on_mousebuttonup(self, event):
        if self.cursor is not None and event.origin == self:
            self.cursor.pressed = False

    def enable(self):
        self.cursor.show()

    def hide(self):
        super().hide()
        self.cursor.hide()


class BaseCursor(Meta):
    pressed = False
    enabled = True

    def __init__(self, parent, y):
        super().__init__(parent)
        self.img_uns = self.crear(1, COLOR_TEXTO)
        self.img_sel = self.crear(3, COLOR_SELECTED)
        self.img_dis = self.crear(5, COLOR_TEXTO)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centery=y)
        self.rect.centerx = self.parent.rect.left
        self.centerx = self.rect.centerx

    @staticmethod
    def crear(w, color):
        image = Surface((w, 13))
        image.fill(color)
        return image

    def select(self):
        super().select()
        self.rect = self.image.get_rect(centerx=self.centerx)

    def deselect(self):
        super().deselect()
        self.rect = self.image.get_rect(centerx=self.centerx)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            EventHandler.trigger('DeselectOthers', self, {})
            WidgetHandler.set_active(self)
            self.pressed = True

    def on_mousebuttonup(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.pressed = False

    def update(self):
        super().update()
        x = mouse.get_pos()[0]
        min_x = self.parent.rect.x
        max_x = self.parent.rect.right
        if self.pressed:
            self.has_mouseover = True
            self.rect.centerx = x if min_x <= x <= max_x else self.rect.x

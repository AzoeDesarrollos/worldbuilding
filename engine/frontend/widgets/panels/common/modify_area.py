from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, mouse


class ModifyArea(BaseWidget):
    marker = None
    ready = False

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((32, 20))
        self.unlink()
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button in (4, 5) and self.ready:
            mouse.set_pos(self.rect.center)
        delta = 0
        if event.button == 4:
            delta = -1
        elif event.button == 5:
            delta = +1

        if self.marker is not None and self.parent.visible_markers:
            self.marker.tune_value(delta)

    def link(self, marker):
        self.marker = marker
        self.color_ready()
        self.ready = True
        mouse.set_pos(self.rect.center)

    def unlink(self):
        self.marker = None
        self.color_standby()
        self.ready = False

    def color_ready(self):
        self.image.fill((0, 255, 0), (1, 1, 30, 18))

    def color_standby(self):
        if self.marker is None:
            self.image.fill((255, 255, 0), (1, 1, 30, 18))
        else:
            self.color_ready()

    def color_alert(self):
        self.image.fill((255, 0, 0), (1, 1, 30, 18))

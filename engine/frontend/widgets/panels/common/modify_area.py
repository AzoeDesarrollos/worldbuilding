from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface


class ModifyArea(BaseWidget):
    marker = None
    visible_markers = False

    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = Surface((32, 20))
        self.unlink()
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        delta = 0
        if event.button == 4:
            delta = -1
        elif event.button == 5:
            delta = +1

        if self.marker is not None and self.visible_markers:
            self.marker.tune_value(delta)

    def link(self, marker):
        self.marker = marker
        self.color_ready()

    def unlink(self):
        self.marker = None
        self.color_standby()

    def color_ready(self):
        self.image.fill((0, 255, 0), (1, 1, 30, 18))

    def color_standby(self):
        if self.marker is None:
            self.image.fill((255, 255, 0), (1, 1, 30, 18))
        else:
            self.color_ready()

    def color_alert(self):
        self.image.fill((255, 0, 0), (1, 1, 30, 18))

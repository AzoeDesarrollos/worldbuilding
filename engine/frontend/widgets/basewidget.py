from pygame.sprite import Sprite


class BaseWidget(Sprite):
    active = False
    enabled = False
    selected = False

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def on_keydown(self, key):
        pass

    def on_keyup(self, key):
        pass

    def on_mousebuttondown(self, event):
        pass

    def on_mousebuttonup(self, event):
        pass

    def on_mousemotion(self, rel):
        pass

    def on_mouseover(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def select(self):
        pass

    def deselect(self):
        pass

    def update(self):
        pass

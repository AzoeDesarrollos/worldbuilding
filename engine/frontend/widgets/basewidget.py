from pygame.sprite import Sprite


class BaseWidget(Sprite):
    active = False

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def on_keydown(self, key):
        pass

    def on_keyup(self, key):
        pass

    def on_mousebuttondown(self, button):
        pass

    def on_mousebuttonup(self, button):
        pass

    def on_mousemotion(self, rel):
        pass

    def on_mouseover(self):
        pass

    def update(self):
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

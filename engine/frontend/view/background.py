from engine.frontend import WIDTH, HEIGHT, WidgetHandler, Renderer
from engine.frontend.widgets import BaseWidget
from pygame.sprite import LayeredUpdates
from random import choice
from pygame import image
from os.path import join
from os import getcwd


class Background(BaseWidget):
    layer = 0
    chunk_x = 0
    chunk_y = 0

    def __init__(self, parent=None):
        self.image_base = image.load(join(getcwd(), 'data', 'estrellas.png'))
        self.rect = self.image_base.get_rect()
        self.chunks = LayeredUpdates(Chunk(self, image.load(join(getcwd(), 'data', 'estrellas.png'))))

        super().__init__(parent)
        WidgetHandler.add_widget(self)

    def __repr__(self):
        return 'Star Bg'

    def move(self, dx=0, dy=0):
        self.purge()
        if dx < 0:
            chunk_image = self.select_chunk(width=dx)
            self.chunks.add(Chunk(self, chunk_image, right=WIDTH))
        if dx > 0:
            chunk_image = self.select_chunk(width=dx)
            self.chunks.add(Chunk(self, chunk_image, left=0))
        if dy < 0:
            chunk_image = self.select_chunk(height=dy)
            self.chunks.add(Chunk(self, chunk_image, bottom=HEIGHT))
        if dy > 0:
            chunk_image = self.select_chunk(height=dy)
            self.chunks.add(Chunk(self, chunk_image, top=0))

    def purge(self):
        for chunk in self.chunks.sprites():
            if not Renderer.contains(chunk):
                chunk.kill()

    def select_chunk(self, width=WIDTH, height=HEIGHT):

        w, h = round(abs(width)), round(abs(height))
        choices_v, choices_h = [], []
        for i in range(0, WIDTH, w):
            try:
                choices_h.append(self.image_base.subsurface(i, 0, w, h))
            except ValueError:
                pass

        for i in range(0, HEIGHT, h):
            try:
                choices_v.append(self.image_base.subsurface(0, i, w, h))
            except ValueError:
                pass

        chosen = None
        if width != WIDTH:
            chosen = choice(choices_h)
        elif height != HEIGHT:
            chosen = choice(choices_v)

        return chosen


class Chunk(BaseWidget):
    def __init__(self, parent, img, **kwargs):
        super().__init__(parent)
        self.image = img
        self.rect = self.image.get_rect(**kwargs)
        self.show()

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

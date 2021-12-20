from pygame import Surface, SRCALPHA
from pygame.sprite import Sprite


class BodyMarker(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self.crear('black')
        self.rect = self.image.get_rect(center=(x, y))

    @staticmethod
    def crear(color):
        graph = [
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ]
        image = Surface([len(graph)]*2, SRCALPHA)
        for y, line in enumerate(graph):
            for x, j in enumerate(line):
                if j:
                    image.set_at((x, y), color)

        return image

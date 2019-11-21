from pygame.sprite import Sprite
from pygame import Surface, Rect, SRCALPHA, Color, draw

# noinspection PyArgumentList
cian = Color(0, 125, 255, 255)
# noinspection PyArgumentList
rojo = Color(255, 0, 0, 255)


class Linea(Sprite):
    def __init__(self, x, y, w, h, grupo):
        super().__init__(grupo)
        self.image = Surface((w, h))
        self.image.fill(cian)

        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = Rect(x, y, w, h)

    def move_x(self, x):
        if 59 < x < 589:
            self.rect.centerx = x

    def move_y(self, y):
        if 2 < y < 480:
            self.rect.centery = y


class Punto(Sprite):
    def __init__(self, x, y, grupo):
        super().__init__(grupo)
        self.image_des = Surface((10, 10), SRCALPHA)
        self.image_sel = Surface((10, 10), SRCALPHA)
        draw.circle(self.image_des, cian, [5, 5], 5)

        draw.circle(self.image_sel, rojo, [5, 5], 5)

        self.image = self.image_des
        self.rect = self.image.get_rect(center=[x, y])

    def select(self):
        self.image = self.image_sel

    def deselect(self):
        self.image = self.image_des

    def move_x(self, x):
        if 59 < x < 589:
            self.rect.centerx = x

    def move_y(self, y):
        if 2 < y < 480:
            self.rect.centery = y

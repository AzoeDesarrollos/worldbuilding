from pygame.sprite import Sprite
from pygame import Surface, Rect, SRCALPHA, Color, draw

cian = Color(0, 125, 255, 255)
rojo = Color(255, 0, 0, 255)
gris = Color(125, 125, 125, 255)


class Linea(Sprite):
    def __init__(self, area, x, y, w, h, grupo):
        super().__init__(grupo)
        self.image = Surface((w, h))
        self.image.fill(cian)

        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = Rect(x, y, w, h)
        self.area_rect = area.copy()

    def move_x(self, x):
        y = self.y
        if self.area_rect.collidepoint((x, y)):
            self.rect.centerx = x

    def move_y(self, y):
        x = self.x
        if self.area_rect.collidepoint((x, y)):
            self.rect.centery = y


class Punto(Sprite):
    disabled = False
    selected = False

    def __init__(self, area, x, y, grupo):
        super().__init__(grupo)
        self.image_des = Surface((10, 10), SRCALPHA)
        self.image_sel = Surface((10, 10), SRCALPHA)
        self.image_dis = Surface((10, 10), SRCALPHA)
        draw.circle(self.image_des, cian, [5, 5], 5)
        draw.circle(self.image_sel, rojo, [5, 5], 5)
        draw.circle(self.image_dis, gris, [5, 5], 5)

        self.image = self.image_des
        self.rect = self.image.get_rect(center=[x, y])
        self.area_rect = area.copy()

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def enable(self):
        self.disabled = False

    def disable(self):
        self.disabled = True

    def move_x(self, x):
        y = self.rect.centery
        if self.area_rect.collidepoint((x, y)):
            self.rect.centerx = x

    def move_y(self, y):
        x = self.rect.centerx
        if self.area_rect.collidepoint((x, y)):
            self.rect.centery = y

    def update(self):
        if not self.disabled:
            if self.selected:
                self.image = self.image_sel
            else:
                self.image = self.image_des
        else:
            self.image = self.image_dis

from pygame import draw, Surface, SRCALPHA
from math import sin, cos, radians
from .basewidget import BaseWidget
from engine.frontend.globales import Renderer, WidgetHandler


class StarSprite(BaseWidget):
    centerx = 0
    centery = 0
    ticks = 0
    has_mouseover = False
    clicked = False

    def __init__(self, star, x, y):
        super().__init__()
        self.radius = round(star.radius.m * 10)

        if self.radius % 2 == 0:
            self.radius += 1
        self.color = star.color
        self.image = self.create()
        self.rect = self.image.get_rect(center=(x, y))
        self.centerx, self.centery = [self.radius - 1] * 2
        self.draw_rays()
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)
        star.sprite = self

    def create(self):
        image = Surface((2 * self.radius, 2 * self.radius), SRCALPHA)
        rect = image.get_rect()
        draw.circle(image, self.color, rect.center, self.radius // 4 * 3)
        return image

    def draw_rays(self, start=0):
        for angulo in range(start, 181, 10):
            contra = (angulo - 180) + 360
            x1, y1 = self.set_xy(angulo)
            x2, y2 = self.set_xy(contra)
            draw.aaline(self.image, self.color, (x1, y1), (x2, y2))

    def set_xy(self, angle: int):
        x = round(self.centerx + self.radius * cos(radians(angle)))
        y = round(self.centery + self.radius * sin(radians(angle)))
        return x, y

    def animate(self):
        self.ticks += 1
        self.image.fill((0, 0, 0, 255))
        self.image = self.create()
        if self.ticks <= 30:
            self.draw_rays(start=0)
        elif self.ticks <= 60:
            self.draw_rays(start=15)
        else:
            self.ticks = 0

    def on_mouseover(self):
        self.animate()

from pygame import draw, Surface, SRCALPHA, transform
from engine.backend.eventhandler import EventHandler
from ..basewidget import BaseWidget
from math import sin, cos, pi


# adapted from https://stackoverflow.com/questions/23246185/python-draw-pie-shapes-with-colour-filled


class Arc(BaseWidget):
    handle_a = None
    handle_b = None
    handle_pos = None
    arc_lenght = 0
    _finished = False

    _set = False

    selected_color = None
    default_value = None

    def __init__(self, parent, name, color_a, color_b, a, b, radius):
        super().__init__(parent)
        self.radius = radius
        self.color = color_a
        self.color_dis = color_b
        self.name = name
        self.selected_color = self.color_dis
        self.a, self.b = a, b
        self.image = self.create()
        self.rect = self.image.get_rect()

    def show(self):
        self.parent.show()
        super().show()

    def hide(self):
        self.parent.hide()
        super().hide()

    def disable(self):
        super().disable()
        self.selected_color = self.color_dis

    def enable(self):
        super().enable()
        self.selected_color = self.color
        self.image = self.create()

    def point(self, n, rect):
        x = rect.w // 2 + int(self.radius * cos(n * pi / 180))
        y = rect.h // 2 + int(self.radius * sin(n * pi / 180))
        return x, y

    def get_value(self):
        value = self.arc_lenght - 1
        return round(value * 100 / 360)

    def post_value(self):
        EventHandler.trigger('SetValue', self.name, {'value': self.get_value()})

    def create(self):
        """Crea la imagen del sector"""
        a, b = self.a, self.b

        image = Surface((self.radius * 2, self.radius * 2), SRCALPHA)
        rect = image.get_rect()
        point_sequence = [(rect.centerx, rect.centery)]
        x, y = a, b
        rotation = False
        # these are because 360 and 0 represent the same point
        if a == 0 and b == 360:
            y = 0
        elif a == 360 and b == 0:
            x = 0

        # these are to avoid a glitch when the arc begins before 0°/360° and ends after 0° but before 360°
        if a < 0:
            x = 0
            y = b + abs(a)
            rotation = abs(a)

        elif 360 >= a > b:
            y = 360 - a + b
            x = 0
            rotation = abs(360 - a)
        elif x == 0 and y == 0:
            self.arc_lenght = -1
        elif x == y == 360:
            self.hide()

        for n in range(x, y + 1):
            # we add 1 here to y for the initial point in the center.
            point_sequence.append(self.point(n, rect))

        if self.handle_pos is None:
            # the initial handle position is only set once.
            self.handle_pos = point_sequence[-2]
        try:
            # El try/catch acá es porque si la point_sequence es demasiado corta para hacer un poligono, esto puede ser
            # porque el arco se extiguió, con lo que es eliminado, o porque el arco ocupa 360°, a lo que se dibuja
            # como un círculo y no como un polígono.
            if self.arc_lenght != -1 and len(point_sequence) > 1:
                self.arc_lenght = len(point_sequence) - 1
            if 1 < self.arc_lenght < 360:
                draw.polygon(image, self.selected_color, point_sequence)
            else:
                rotation = False
                self._finished = True
                draw.circle(image, self.selected_color, [self.radius, self.radius], self.radius)

        except ValueError:
            if self.arc_lenght < 1:
                self.hide()
            # if self.handle_a.pressed:
            #     self.handle_a.merge()
            # elif self.handle_b.pressed:
            #     self.handle_b.merge()

        if rotation:
            image = transform.rotate(image, rotation)

        if not self._set:
            self.post_value()
        return image

    def displace(self, cx, cy):
        """Ajusta la posición del arco según el centro dado"""
        dx = cx - self.rect.centerx
        dy = cy - self.rect.centery
        self.rect.move_ip(dx, dy)
        # self.handle_a.rect.move_ip(dx // 2, dy // 2)
        # self.handle_b.rect.move_ip(dx // 2, dy // 2)

    # def adjust(self, handle):
    #     if handle is self.handle_a:
    #         self.a = handle.angle
    #     if handle is self.handle_b:
    #         self.b = handle.angle
    #
    #     if not self._finished:
    #         pos = self.rect.center
    #         self.image = self.create()
    #         self.rect = self.image.get_rect(center=pos)
    #     else:
    #         # there's no point of having a handle if the "arc" is a circle,
    #         # so the handle commits suicide.
    #         handle.kill()

    def __repr__(self):
        return 'Arc ' + self.name

    def links(self, handle_a, handle_b):
        self.handle_a = handle_a
        self.handle_b = handle_b

        self.handle_a.link(self)
        self.handle_b.link(self)

    def is_handle(self, handle):
        a = handle == self.handle_a
        b = handle == self.handle_b
        return a or b

    def set_ab(self, a, b):
        self.a = a
        self.b = b
        self._set = True
        pos = self.rect.center
        self.image = self.create()
        self.rect = self.image.get_rect(center=pos)

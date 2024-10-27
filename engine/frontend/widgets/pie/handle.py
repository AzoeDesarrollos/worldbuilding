from pygame import Surface, transform, SRCALPHA, Color, mouse
from engine.backend.eventhandler import EventHandler
from math import sin, cos, radians, sqrt
from ..meta import Meta


class Handle(Meta):
    pressed = False

    def __init__(self, parent, angle, name, pos):
        super().__init__(parent)
        self.layer += 10
        self.angle = angle
        self.name = name
        self.linked = []
        color3 = self.parent.get_disabled_color('black')
        self.img_uns = self.create(6, 'black')
        self.img_sel = self.create(8, 'white')
        self.img_dis = self.create(6, color3)
        self.image = self.img_dis
        self.rect = self.image.get_rect(center=pos)

    @staticmethod
    def create(size, fg):
        image = Surface((size + 2, size + 2), SRCALPHA)
        image.fill('gold')
        image.fill(Color(fg), rect=[1, 1, size, size])
        return transform.rotate(image, 45.0)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.pressed = True
            mouse.set_pos(self.rect.center)
            self.parent.set_active(self)
            EventHandler.trigger('SetOrigin', self, {'origin': self})

    def on_mousebuttonup(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.pressed = False
            self.parent.set_active()

    def on_mouseover(self):
        if self.enabled:
            # mouse.set_pos(self.rect.center)
            self.selected = True

    def on_mousemotion(self, rel):
        dx, dy = rel
        delta = 0
        if self.pressed and self.enabled:
            if 0 <= self.angle <= 90:  # bottomright
                if dx < 0 or dy > 0:
                    delta = +1
                else:
                    delta = -1
            elif 90 <= self.angle <= 180:  # bottomleft
                if dx < 0 or dy < 0:
                    delta = +1
                else:
                    delta = -1
            elif 180 <= self.angle <= 270:  # topleft
                if dx > 0 or dy < 0:
                    delta = +1
                else:
                    delta = -1
            elif 270 <= self.angle <= 360:  # topright
                if dx > 0 or dy > 0:
                    delta = +1
                else:
                    delta = -1

            if self.angle + delta >= 360:
                self.angle = 0
            elif self.angle + delta <= 0:
                self.angle = 360
            else:
                self.angle += delta

            self.rect.center = self.set_xy()
            for widget in self.linked:
                widget.adjust(self)

    def restore(self, angle):
        self.angle = angle
        self.rect.center = self.set_xy()

    def link(self, arc):
        if arc not in self.linked:
            self.linked.append(arc)

    def unlink(self, arc):
        if arc in self.linked:
            self.linked.remove(arc)

    def set_xy(self):
        x = round(self.parent.rect.centerx + self.parent.radius * cos(radians(self.angle)))
        y = round(self.parent.rect.centery + self.parent.radius * sin(radians(self.angle)))
        return x, y

    def euclidean_distance(self, other) -> float:
        """Devuelve la distancia de Euclides que hay entre dos handles."""
        x1, y1 = self.rect.center
        x2, y2 = other.rect.center
        d = sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
        return d

    def get_direction(self, x2, y2):
        x1, y1 = self.rect.center
        dx = x2 - x1
        dy = y2 - y1
        if dx > dy:
            if dy < 0:
                return 0, +1
            else:
                return 0, -1
        else:
            if dx < 0:
                return +1, 0
            else:
                return -1, 0

    def update(self, *args, **kwargs) -> None:
        """Controla la imagen del handle según si está seleccionado o no."""

        if self.selected and self.enabled:
            self.image = self.img_sel
        elif self.enabled:
            self.image = self.img_uns
        else:
            self.image = self.img_dis

        self.rect = self.image.get_rect(center=self.rect.center)
        if not self.pressed:
            self.selected = False

    def merge(self):
        """
        Al unirse dos Handles, estos se mezclan porque el arco que había entre ellos desapareció.
        """

        for arc in self.linked:
            if self is not arc.handle_a and self.euclidean_distance(arc.handle_a) < 3:
                arc.handle_a.kill()
                self.unlink(arc)
                linked = [a for a in arc.handle_a.linked if a is not arc][0]
                self.link(linked)
                linked.handle_b = self

            elif self is not arc.handle_b and self.euclidean_distance(arc.handle_b) < 3:
                arc.handle_b.kill()
                self.unlink(arc)
                linked = [a for a in arc.handle_b.linked if a is not arc][0]
                self.link(linked)
                linked.handle_a = self

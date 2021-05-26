from math import pi, sqrt, asin, pow
from pygame import Rect
from engine import d

pi = d(pi)


class BodyInHydrostaticEquilibrium:
    circumference = 0
    surface = 0
    volume = 0
    density = 0

    celestial_type = ''

    @staticmethod
    def calculate_circumference(r):
        return d('2') * pi * r

    @staticmethod
    def calculate_surface_area(r):
        return d('4') * pi * r ** d('2')

    @staticmethod
    def calculate_volume(r):
        return (d('4') / d('3')) * pi * r ** d('3')

    @classmethod
    def calculate_density(cls, m, r):
        v = cls.calculate_volume(r)
        return m / v

    def update_everything(self):
        return NotImplemented

    def set_value(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
            self.update_everything()


class Ellipse:
    _a = 0  # semi major axis
    _b = 0  # semi minor axis
    _e = 0  # eccentricity

    focus = None

    def __init__(self, a, e):
        assert 0 <= e < 1, 'eccentricity has to be greater than 0\nbut less than 1.'
        self._a = d(a.m)
        self._e = d(e.m)
        self._b = self._a * sqrt(1 - pow(self._e, d(2)))
        self.focus = sqrt(pow(self._a, d(2)) - pow(self._b, d(2)))

    def get_rect(self, x, y):
        """returns the rect of the ellipse for the use of pygame.draw.ellipse().
        x and y form the center of the ellipse, not its topleft point."""

        w = self._a * d(2)
        h = self._b * d(2)
        return Rect(int(d(x) // d(2)), int(d(y) // d(2)), w, h)


class OblateSpheroid(Ellipse, BodyInHydrostaticEquilibrium):
    def calculate_circumference(self, r):
        return d(2) * d(pi) * sqrt((self._a + self._b) / d(2))

    def calculate_surface_area(self, r):
        return d(2) * d(pi) * self._a * (self._a + (self._b / self._e) * asin(self._e))

    def calculate_volume(self, r):
        return d('4/3') * d(pi) * (self._a ** d(2)) * self._b


class Ring:
    def __init__(self, planet,  inner, outer, w, h):
        self.inner = inner
        self.outer = outer
        self.wideness = w
        self.thickness = h
        self.parent = planet

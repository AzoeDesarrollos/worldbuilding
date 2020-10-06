from math import pi, sqrt, asin
from pygame import Rect


class BodyInHydrostaticEquilibrium:
    circumference = 0
    surface = 0
    volume = 0
    density = 0

    celestial_type = ''

    @staticmethod
    def calculate_circumference(r):
        return 2 * pi * r

    @staticmethod
    def calculate_surface_area(r):
        return 4 * pi * r ** 2

    @staticmethod
    def calculate_volume(r):
        return (4 / 3) * pi * r ** 3

    @classmethod
    def calculate_density(cls, m, r):
        v = cls.calculate_volume(r)
        return m / v


class Ellipse:
    a = 0  # semi major axis
    b = 0  # semi minor axis
    e = 0  # eccentricity

    def __init__(self, a, e):
        self.b = a * sqrt(1 - (e ** 2))
        self.a = a
        self.e = e

    def draw(self, x, y):
        """returns the rect of the ellipse for the use of pygame.draw.ellipse().
        x and y form the center of the ellipse, not its topleft point."""

        w = self.a * 2
        h = self.b * 2
        return Rect(x // 2, y // 2, w, h)


class OblateSpheroid(Ellipse, BodyInHydrostaticEquilibrium):
    def calculate_circumference(self, r):
        return 2 * pi * sqrt((self.a + self.b) / 2)

    def calculate_surface_area(self, r):
        return 2*pi*self.a*(self.a+(self.b/self.e)*asin(self.e))

    def calculate_volume(self, r):
        return 4/3*pi*(self.a**2)*self.b

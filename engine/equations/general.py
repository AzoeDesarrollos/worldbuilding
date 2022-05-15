from engine.backend.util import roll, q
from math import pi, sqrt, asin
from pygame import Rect
from .day_lenght import aprox_day_leght


class Flagable:
    flagged = False
    _position = None

    def flag(self):
        self.flagged = True

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, values):
        x, y, z = values
        self._position = x, y, z


class StarSystemBody(Flagable):
    parent = None
    celestial_type = ''
    name = None
    has_name = False

    _age = -1
    _rotation = -1

    formation = 0
    reference_rotation = q(24, 'hours/day')
    unit = ''

    def set_parent(self, parent):
        self.parent = parent
        self.age = parent.age.to('years')
        self.formation = parent.age.to('billion years')

    def is_orbiting_a_star(self):
        if hasattr(self.parent, 'parent'):
            return self.parent.parent is None
        return False

    def set_name(self, name):
        self.name = name
        self.has_name = True

    @staticmethod
    def find_topmost_parent(this):
        if this.is_orbiting_a_star():
            return this.parent
        else:
            return this.find_topmost_parent(this.parent)

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new):
        self._age = new

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, new: q):
        if type(self._rotation) in (int, q):
            self._rotation = new.to(self.unit + '_rotation')
            self.reference_rotation = round(new.to('hours/day').m, 3)
        else:
            self.reset_rotation()

    def reset_rotation(self):
        now = -self.formation.to('years').m - self.age.to('years').m
        self._rotation = q(aprox_day_leght(self, now), self.unit + '_rotation')

    def update_everything(self, age=None):
        if age is not None:
            self.age = age
            self.reset_rotation()


class BodyInHydrostaticEquilibrium(StarSystemBody):
    circumference = 0
    surface = 0
    volume = 0
    density = 0

    satellites = None

    rogue = False  # Bodies created outside a system are rogue planets by definition.

    def set_rogue(self):
        self.rogue = True
        self._position = roll(-100, 100), roll(-100, 100), roll(-100, 100)

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
        self._a = float(a.m)
        self._e = float(e.m)
        self._b = self._a * sqrt(1 - (self._e ** 2))
        self._c = sqrt(self._a ** 2 - self._b ** 2)
        self.f1 = Point(self._c, 0)
        self.f2 = Point(-self._c, 0)
        self.focus = self.f1

    def get_rect(self, x, y):
        """returns the rect of the ellipse for the use of pygame.draw.ellipse().
        x and y form the center of the ellipse, not its topleft point."""

        w = self._a * 2
        h = self._b * 2
        return Rect(x // 2, y // 2, w, h)


class OblateSpheroid(Ellipse, BodyInHydrostaticEquilibrium):
    def calculate_circumference(self, r):
        return 2 * pi * sqrt((self._a + self._b) / 2)

    def calculate_surface_area(self, r):
        return 2 * pi * self._a * (self._a + (self._b / self._e) * asin(self._e))

    def calculate_volume(self, r):
        return 4 / 3 * pi * (self._a ** 2) * self._b


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

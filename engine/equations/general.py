from engine.backend.util import roll, q, eucledian_distance
from math import pi, sqrt, asin, sin, cos
from .day_lenght import aprox_daylenght
from pygame import Rect


class Flagable:
    flagged = False
    _position = None

    parent = None
    system_number = None

    def flag(self):
        self.flagged = True

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, values):
        self._position = values

    def random_position(self):
        self.position = roll(-100, 100), roll(-100, 100), roll(-100, 100)

    def is_orbiting_a_star(self):
        if self.parent is not None:
            return self.parent
        else:
            return False

    def find_topmost_parent(self):
        if self.parent is not None:
            return self.parent.find_topmost_parent()
        else:
            return self


class StarSystemBody(Flagable):
    celestial_type = ''
    name = None
    has_name = False

    _age = -1
    _rotation = -1

    formation: q = None
    reference_rotation = None
    unit = ''

    hill_sphere = None
    roches_limit = None

    habitable = False

    def set_parent(self, parent):
        self.parent = parent
        self.age = parent.age.to('years')
        self.formation = parent.age.to('billion years')

    def set_name(self, name):
        self.name = name
        self.has_name = True

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
        if type(new) is q:
            if type(self._rotation) in (int, q):
                self._rotation = new.to(self.unit + '_rotation')
                self.reference_rotation = round(new.to('hours/day').m, 3)
        else:
            self._rotation = new

    def reset_rotation(self):
        formation = self.formation.to('years').m
        age = self.age.to('years').m
        if age > formation:
            'the future'
            'formation is possitive, age is possitve but more than formation'
            now = age
        elif age < formation:
            'the past'
            'formation is possitive'
            'age is also possitive, but less than formation'
            'then it is a point in the past, after formation but before now'
            now = -(formation - age)

        else:
            'age equals formation, so it is the present'
            now = 0
        self._rotation = q(aprox_daylenght(self, now), self.unit + '_rotation')

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

    _tilt = 'Not set'
    spin = 'N/A'

    def set_rogue(self):
        self.rogue = True
        self.random_position()

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

    def set_habitability(self, tilt):
        self.habitable = False
        return NotImplemented

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        if type(value) is not str:
            tilt = AxialTilt(self, value)
            self._tilt = tilt
            self.set_habitability(tilt)
        else:
            self._tilt = value

    def set_spin(self, spin):
        self.spin = spin


class Ellipse:
    _a = 0  # semi major axis
    _b = 0  # semi minor axis
    _e = 0  # eccentricity

    focus = None

    def __init__(self, a, e):
        assert 0 <= float(e.m) < 1, 'eccentricity has to be greater than 0\nbut less than 1.'
        self._a = float(a.m)
        self._e = float(e.m)
        self._b = self._a * sqrt(1 - (self._e ** 2))
        self._c = sqrt(self._a ** 2 - self._b ** 2)
        self.f1 = Point(self._c, name='right')
        self.f2 = Point(-self._c, name='left')

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

    def set_habitability(self, tilt):
        raise NotImplementedError


class Point:
    x, y, z = None, None, None  # None, porque 0 y -0 son también valores válidos.

    def __init__(self, x, y=None, z=None, name=''):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def how_close(self, other):
        if not hasattr(other, 'z'):
            return eucledian_distance([self.x, self.y], [other.x, other.y])
        else:
            return eucledian_distance(self, other)

    def __getitem__(self, item):
        if item == 0 and len(self) == 1:
            return self.x
        elif item == 1 and len(self) == 2:
            return self.y
        elif item == 2 and len(self) == 3:
            return self.z
        else:
            raise StopIteration

    def __len__(self):
        if self.y is None:
            return 1
        elif self.z is None:
            return 2
        else:
            return 3

    def __repr__(self):
        if self.name != '':
            return self.name
        else:
            return str(self)

    def __sub__(self, other):
        if len(self) == len(other):
            diffs = []
            for i, value in enumerate(self):
                result = self[i] - other[i]
                diffs.append(result)
            return sum(diffs)
        else:
            raise ValueError("Points must have equal lenghts")

    def __iter__(self):
        if len(self) == 1:
            return iter([self.x])
        elif len(self) == 2:
            return iter([self.x, self.y])
        else:
            return iter([self.x, self.y, self.z])


class AxialTilt:
    _value = 0
    _cycle = 0
    x, y = 0, 0

    def __init__(self, parent, inclination):
        self.parent = parent
        if type(inclination) is q:
            inclination = inclination.m
        if 0 <= inclination < 90:
            self.parent.set_spin('pograde')
        elif 90 <= inclination <= 180:
            self.parent.set_spin('retrograde')
        self._value = inclination
        self.x = inclination
        self._cycle = -7.095217823187172 * pow(self._value, 2) + 1277.139208333333 * self._value

    @property
    def a(self):
        # to be able to write tilt.a.m as with orbits
        return q(self._value, 'degree')

    @property
    def u(self):
        return 'degree'

    @property
    def m(self):
        return self._value

    @property
    def cycle_lenght(self):
        return q(round(self._cycle, 3), 'years')

    def precess(self, year):
        t = self._value  # "t" es el axial tilt del planeta.
        c = self._cycle  # "c" es el ciclo en años
        b = (2 * pi) / c  # "b" es la amplitud, un ciclo (2pi) cada "c" años
        self.x = round(t * cos(year * b), 3)  # inclinación en el eje x
        self.y = round(t * sin(year * b), 3)  # inclinación en el eje y

    def __int__(self):
        return self._value

    def update(self, year):
        self.precess(year)

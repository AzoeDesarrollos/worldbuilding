from math import sqrt, pow
from pygame import draw, Rect
from engine import q


class RawOrbit:
    unit = ''
    semi_major_axis = None
    temperature = ''

    def __init__(self, a, unit):
        self.semi_major_axis = q(float(a), unit)
        self.unit = unit
        self.a = self.semi_major_axis

    def set_temperature(self, t):
        self.temperature = t

    def __mul__(self, other):
        new_a = None
        if type(other) not in (float, Orbit):
            return NotImplemented()
        elif type(other) is float:
            new_a = q(self.semi_major_axis.m * other, self.unit)
        elif type(other) is Orbit:
            new_a = q(self.semi_major_axis.m * other.semi_major_axis.m, self.unit)

        return new_a.m

    def __truediv__(self, other):
        new_a = None
        if type(other) not in (float, Orbit):
            return NotImplemented()
        elif type(other) is float:
            new_a = q(self.semi_major_axis.m / other, self.unit)
        elif type(other) is Orbit:
            new_a = q(self.semi_major_axis.m / other.semi_major_axis.m, self.unit)

        return new_a.m

    def __float__(self):
        return float(self.semi_major_axis.m)

    def __lt__(self, other):
        return self.semi_major_axis.m < other

    def __gt__(self, other):
        return self.semi_major_axis.m > other

    def __eq__(self, other):
        return other.semi_major_axis.m == self.semi_major_axis.m

    def __repr__(self):
        # noinspection PyStringFormat
        return 'Orbit @' + '{:}'.format(round(float(self), 3))

    def complete(self, e, i):
        return Orbit(self.semi_major_axis.m, e, i, self.unit)


class Orbit:
    period = 0
    velocity = 0
    motion = ''

    _e = 0  # eccentricity
    _i = 0  # inclination
    _a = 0  # semi-major axis
    _b = 0  # semi-minor axis
    _q = 0  # periapsis
    _Q = 0  # apoapsis

    def __init__(self, a, e: float, i: float, unit='au'):
        self.unit = unit
        self._e = float(e)
        self._i = float(i)
        self._a = float(a.m)
        self._b = self._a * sqrt(1 - pow(self._e, 2))
        self._Q = self._a * (1 + self._e)
        self._q = self._a * (1 - self._e)

        self.unit = unit

        if self.inclination in (0, 180):
            self.motion = 'equatorial'
        elif self.inclination == 90:
            self.motion = 'polar'
        elif 0 <= self.inclination <= 90:
            self.motion = 'prograde'
        elif 90 < self.inclination <= 180:
            self.motion = 'retrograde'

        # abreviaturas
        self.a = self.semi_major_axis
        self.b = self.semi_minor_axis

    def draw(self, surface):
        rect = Rect(0, 0, 2 * self.semi_major_axis, 2 * self.semi_minor_axis)
        screen_rect = surface.get_rect()
        rect.center = screen_rect.center
        draw.ellipse(surface, (255, 255, 255), rect, width=1)

    def __repr__(self):
        return 'Orbit @' + str(round(self.semi_major_axis.m, 3))

    @property
    def semi_major_axis(self):
        return q(self._a, self.unit)

    @property
    def semi_minor_axis(self):
        return q(self._b, self.unit)

    @property
    def periapsis(self):
        return q(self._q, self.unit)

    @property
    def apoapsis(self):
        return q(self._Q, self.unit)

    @property
    def eccentricity(self):
        return q(self._e)

    @property
    def e(self):
        return self.eccentricity

    @eccentricity.setter
    def eccentricity(self, value):
        self._e = float(value)

    @property
    def inclination(self):
        return q(self._i, 'degree')

    @property
    def i(self):
        return self.inclination

    @inclination.setter
    def inclination(self, value):
        self._i = float(value)


class PlanetOrbit(Orbit):
    def __init__(self, star_mass, a, e, i):
        super().__init__(a, e, i, 'au')
        self.velocity = q(sqrt(star_mass / a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(sqrt((a ** 3) / star_mass), 'year')


class SatelliteOrbit(Orbit):
    def __init__(self, planet_mass, moon_mass, a, e, i):
        super().__init__(a, e, i, 'earth_radius')
        self.velocity = q(sqrt(planet_mass / a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(0.0588 * (a ** 3 / sqrt(planet_mass + moon_mass)), 'day')

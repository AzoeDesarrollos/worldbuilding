from math import sqrt
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
        return self.semi_major_axis.m

    def __lt__(self, other):
        return self.semi_major_axis.m < other

    def __gt__(self, other):
        return self.semi_major_axis.m > other

    def __eq__(self, other):
        return other.semi_major_axis.m == self.semi_major_axis.m

    def __repr__(self):
        return 'Orbit @' + str(round(self.semi_major_axis.m, 3))

    def complete(self, e, i):
        return Orbit(self.semi_major_axis.m, e, i, self.unit)


class Orbit:
    semi_major_axis = 0
    semi_minor_axis = 0
    periapsis = 0
    apoapsis = 0

    period = 0
    velocity = 0
    motion = ''

    _e = 0
    _i = 0

    def __init__(self, a: float, e: float, i: float, unit='au'):
        self.unit = unit
        self._e = float(e)
        self._i = float(i)
        self.semi_major_axis = q(float(a), unit)

        self.semi_minor_axis = q(a * sqrt(1 - e ** 2), unit)
        self.periapsis = q(a * (1 - e), unit)
        self.apoapsis = q(a * (1 + e), unit)

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

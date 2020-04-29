from math import sqrt
from pygame import draw, Rect
from engine import q


def put_in_star_orbit(body, star, a):
    body.orbit = PlanetOrbit(star.mass.magnitude, a)


def put_in_planet_orbit(body, planet, satellite, a):
    body.orbit = SatelliteOrbit(planet.mass.m, satellite.mass.m, a)


class RawOrbit:
    unit = ''
    semi_major_axis = None

    def __init__(self, a, unit):
        self.semi_major_axis = q(float(a), unit)
        self.unit = unit
        self.a = self.semi_major_axis

    def __mul__(self, other):
        new_a = None
        if type(other) not in (float, Orbit):
            return NotImplemented()
        elif type(other) is float:
            new_a = q(self.semi_major_axis.m * other, self.unit)
        elif type(other) is Orbit:
            new_a = q(self.semi_major_axis.m * other.semi_major_axis.m, self.unit)

        return RawOrbit(new_a.m, self.unit)

    def __truediv__(self, other):
        new_a = None
        if type(other) not in (float, Orbit):
            return NotImplemented()
        elif type(other) is float:
            new_a = q(self.semi_major_axis.m / other, self.unit)
        elif type(other) is Orbit:
            new_a = q(self.semi_major_axis.m / other.semi_major_axis.m, self.unit)

        return RawOrbit(new_a.m, self.unit)

    def __float__(self):
        return self.semi_major_axis.m

    def __lt__(self, other):
        return self.semi_major_axis.m < other

    def __gt__(self, other):
        return self.semi_major_axis.m > other

    def __repr__(self):
        return 'Orbit @'+str(round(self.semi_major_axis.m, 3))

    def complete(self, e, i):
        return Orbit(self.semi_major_axis.m, e, i, self.unit)


class Orbit:
    semi_major_axis = 0
    eccentricity = 0
    inclination = 0

    semi_minor_axis = 0
    periapsis = 0
    apoapsis = 0

    period = 0
    velocity = 0
    motion = ''

    def __init__(self, a: float, e: float, i: float, unit='au'):
        self.unit = unit
        self.eccentricity = q(float(e))
        self.inclination = q(float(i), "degree")
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
        self.e = self.eccentricity
        self.i = self.inclination

    def draw(self, surface):
        rect = Rect(0, 0, 2 * self.semi_major_axis, 2 * self.semi_minor_axis)
        screen_rect = surface.get_rect()
        rect.center = screen_rect.center
        draw.ellipse(surface, (255, 255, 255), rect, width=1)

    def __repr__(self):
        return 'Orbit @' + str(round(self.semi_major_axis.m, 3))


class PlanetOrbit:
    def __init__(self, star_mass, a):
        self.velocity = q(sqrt(star_mass / a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(sqrt((a ** 3) / star_mass), 'year')


class SatelliteOrbit:
    def __init__(self, planet_mass, moon_mass, a):
        self.velocity = q(sqrt(planet_mass / a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(0.0588 * (a ** 3 / sqrt(planet_mass + moon_mass)), 'day')

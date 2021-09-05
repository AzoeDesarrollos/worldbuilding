from engine.backend.util import collapse_factor_lists, prime_factors
from engine.frontend.graphs.orbital_properties import rotation_loop
from engine.frontend.globales import Renderer
from math import sqrt, pow, cos, sin, pi
from .planetary_system import Systems
from .general import Ellipse
from pygame import draw
from engine import q


class RawOrbit:
    _unit = ''
    temperature = ''

    def __init__(self, star, a):
        self._unit = a.u
        self.a = a
        self.star = star
        self.set_temperature()

    def set_temperature(self):
        if not self.a.u == 'earth_radius':
            if self.a.m > self.star.frost_line.m:
                self.temperature = 'cold'
            elif self.star.habitable_inner.m <= self.a.m <= self.star.habitable_outer.m:
                self.temperature = 'habitable'
            else:
                self.temperature = 'hot'
        else:
            self.temperature = 'N/A'

    @property
    def semi_major_axis(self):
        return q(self.a.m, self._unit)

    @semi_major_axis.setter
    def semi_major_axis(self, quantity):
        self.a = quantity
        self.set_temperature()

    def __mul__(self, other):
        new_a = None
        if type(other) not in (float, Orbit):
            return NotImplemented()
        elif type(other) is float:
            new_a = q(self.semi_major_axis.m * other, self._unit)
        elif type(other) is Orbit:
            new_a = q(self.semi_major_axis.m * other.semi_major_axis.m, self._unit)

        return new_a.m

    def __truediv__(self, other):
        new_a = None
        if type(other) not in (float, Orbit):
            return NotImplemented()
        elif type(other) is float:
            new_a = q(self.semi_major_axis.m / other, self._unit)
        elif type(other) is Orbit:
            new_a = q(self.semi_major_axis.m / other.semi_major_axis.m, self._unit)

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
        return 'Orbit @' + '{:}'.format(round(float(self), 3))

    def complete(self, e, i):
        return Orbit(self.semi_major_axis.m, e, i, self._unit)


class PseudoOrbit:
    eccentricity = ''
    inclination = ''
    semi_major_axis = 0
    temperature = 0

    def __init__(self, orbit):
        self.semi_major_axis = orbit.semi_major_axis
        self.temperature = orbit.temperature

    @property
    def a(self):
        return self.semi_major_axis


class Orbit(Ellipse):
    period = 0
    velocity = 0
    motion = ''

    _i = 0  # inclination
    _q = 0  # periapsis
    _Q = 0  # apoapsis

    astrobody = None
    _temperature = 0
    _star = None

    argument_of_periapsis = 'undefined'
    longitude_of_the_ascending_node = 0
    true_anomaly = q(0, 'degree')

    def __init__(self, a, e, i, unit='au'):
        super().__init__(a, e)
        self._unit = unit
        assert 0 <= float(i.m) <= 180, 'inclination values range from 0 to 180 degrees.'
        self._i = float(i.m)
        self._Q = self._a * (1 + self._e)
        self._q = -self._a * (1 - self._e)

        if self._i in (0, 180):
            self.motion = 'equatorial'
            self.direction = 'prograde' if self._i == 0 else 'retrograde'  # if self._i == 180
        elif self._i == 90:
            self.motion = 'polar'
            self.direction = 'perpendicular'

        if 0 <= self._i < 90:
            self.direction = 'prograde'
            self.motion = self.direction
        elif 90 < self._i < 180:
            self.direction = 'retrograde'
            self.motion = self.direction

    def draw(self, surface):
        screen_rect_center = surface.get_rect().center
        rect = self.get_rect(*screen_rect_center)
        draw.ellipse(surface, (255, 255, 255), rect, width=1)

    def __repr__(self):
        return 'Orbit @' + str(round(self.semi_major_axis.m, 3))

    def set_astrobody(self, main, astro_body):
        body_around_star = main.celestial_type == "star" or main.celestial_type == 'system'
        body_around_planet = main.celestial_type == "planet"

        if body_around_star:
            astro_body.orbit = PlanetOrbit(main.mass, self.semi_major_axis, self.eccentricity, self.inclination)
            astro_body.orbit.reset_astrobody(astro_body)

        elif body_around_planet:
            astro_body.orbit = SatelliteOrbit(self.semi_major_axis, self.eccentricity, self.inclination)
            astro_body.orbit.reset_astrobody(astro_body)
            astro_body.orbit.reset_period_and_speed(main.mass)

        astro_body.orbit._star = main
        astro_body.parent = main
        if astro_body.celestial_type == 'planet':
            self._temperature = astro_body.set_temperature(main.mass.m, self._a)

        if body_around_planet:
            main = astro_body.parent.orbit.star
        system = Systems.get_system_by_star(main)
        system.visibility_by_albedo()

    def get_planet_position(self):
        x = self._a * cos(self.true_anomaly.m)
        y = self._b * sin(self.true_anomaly.m)
        return x, y

    def get_measured_position(self, anomaly, unit):
        x = self.a.to(unit).m * cos(anomaly)
        y = self.b.to(unit).m * sin(anomaly)
        return x, y

    def set_true_anomaly(self, value: float):
        self.true_anomaly = q(round(value, 3), 'degree')

    @property
    def a(self):
        return self.semi_major_axis

    @property
    def b(self):
        return self.semi_minor_axis

    @property
    def semi_major_axis(self):
        return q(self._a, self._unit)

    @semi_major_axis.setter
    def semi_major_axis(self, quantity):
        self._a = float(quantity.m)
        self._b = self._a * sqrt(1 - pow(self._e, 2))
        self._Q = self._a * (1 + self._e)
        self._q = self._a * (1 - self._e)
        if self.temperature != 'N/A':
            self._temperature = self.astrobody.set_temperature(self._star.mass.m, self._a)
        self.reset_period_and_speed(self._star.mass.m)

    @property
    def semi_minor_axis(self):
        return q(self._b, self._unit)

    @property
    def periapsis(self):
        return q(self._q, self._unit)

    @property
    def apoapsis(self):
        return q(self._Q, self._unit)

    @property
    def eccentricity(self):
        return q(self._e)

    @property
    def e(self):
        return self.eccentricity

    @eccentricity.setter
    def eccentricity(self, value):
        assert 0 <= value < 1, 'eccentricity has to be greater than 0\nbut less than 1.'
        self._e = float(value)

    @property
    def inclination(self):
        return q(self._i, 'degree')

    @property
    def i(self):
        return self.inclination

    @inclination.setter
    def inclination(self, value):
        assert 0 <= float(value.m) <= 180, 'inclination values range from 0 to 180 degrees.'
        self._i = float(value)

    @property
    def temperature(self):
        if self._temperature == 'N/A':
            return 'N/A'
        else:
            return self.astrobody.temperature

    @property
    def star(self):
        return self._star

    def reset_period_and_speed(self, main_body_mass):
        raise NotImplementedError

    def reset_astrobody(self, astro_body):
        self.astrobody = astro_body
        self._temperature = astro_body.temperature


class PlanetOrbit(Orbit):
    primary = 'Star'

    def __init__(self, star_mass, a, e, i):
        super().__init__(a, e, i, 'au')
        self.reset_period_and_speed(star_mass.m)
        orbital_properties = set_orbital_properties(self._i)
        self.longitude_of_the_ascending_node = orbital_properties[0]
        self.argument_of_periapsis = orbital_properties[1]

    def reset_period_and_speed(self, main_body_mass):
        self.period = q(sqrt(pow(self._a, 3) / main_body_mass), 'year')
        self.velocity = q(sqrt(main_body_mass / self._a), 'earth_orbital_velocity').to('kilometer per second')


class SatelliteOrbit(Orbit):
    primary = 'Planet'

    def __init__(self, a, e, i):
        super().__init__(a, e, i, 'earth_radius')
        orbital_properties = set_orbital_properties(self._i)
        self.longitude_of_the_ascending_node = orbital_properties[0]
        self.argument_of_periapsis = orbital_properties[1]

    def reset_period_and_speed(self, main_body_mass):
        satellite_mass = round(self.astrobody.mass.m, 3)
        self.velocity = q(sqrt(main_body_mass.m / self._a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(sqrt(pow(self.a.to('au').m, 3) / (main_body_mass.m + satellite_mass)), 'year').to('day')


class BinaryStarOrbit(Orbit):
    def __init__(self, star, other, a, e):
        super().__init__(a, e, q(0, 'degrees'))
        self.reset_period_and_speed(star.mass.m+other.mass.m)

    def reset_period_and_speed(self, main_body_mass):
        self.period = q(sqrt(pow(self._a, 3) / main_body_mass), 'year')
        self.velocity = q(sqrt(main_body_mass / self._a), 'earth_orbital_velocity').to('kilometer per second')


class GalacticStellarOrbit(Orbit):
    def __init__(self, a, e):
        super().__init__(a, e, q(0, 'degrees'), unit='kpc')
        age = self.star.age.m
        self.star.z = q(49*cos((2*pi/72)*age), 'kpc')
        # z difined as the star's shift ("bobbing") with respect to the galactic plane
        # also, this fuction is completely made up, as the actual formula dependes on observational data.

    def reset_period_and_speed(self, main):
        raise NotImplementedError


def from_stellar_resonance(star, planet, resonance: str):
    """Return the semi-major axis in AU of the resonant orbit.

    The resonance argument is a string in the form of 'x:y'
    where both x and y are integers and x >= y.
    """
    x, y = [int(i) for i in resonance.split(':')]
    period = (x/y) * planet.orbit.period.to('year').m
    semi_major_axis = q(pow(pow(period, 2) * star.mass.to('sol_mass').m, (1 / 3)), 'au')
    return semi_major_axis


def from_planetary_resonance(planet, satellite, resonance: str):
    """Return the semi-major axis in Re of the resonant orbit.

    The resonance argument is a string in the form of 'x:y'
    where both x and y are integers and x >= y.
    """

    x, y = [int(i) for i in resonance.split(':')]
    period = (x/y) * satellite.orbit.period.to('year').m
    mass = planet.mass.m + satellite.mass.m  # earth masses
    semi_major_axis = q(pow(pow(period, 2) * mass, (1 / 3)), 'au')
    return semi_major_axis.to('earth_radius')


def to_resonance(period_primary, period_secondary):
    # resonances = ['1:1', '5:4', '4:3', '11:8', '3:2', '5:3', '7:4',
    #               '9:5', '11:6', '2:1', '19:9', '9:4', '7:3', '12:5',
    #               '5:2', '8:3', '3:1', '7:2', '11:3', '11:2']
    """It takes a pair of orbital periods and returns their mean motion
     resonance, if it exist. Otherwise, returns False."""
    a, b = prime_factors(period_primary), prime_factors(period_secondary)
    x, y = collapse_factor_lists(a, b)
    if x < period_primary and y < period_secondary:  # the MMR numbers should be small
        return x, y
    return False  # objects are not in mean motion resonance


def set_orbital_properties(inclination):
    if inclination in (0, 180):
        return q(0, 'degree'), 'undefined'
    else:
        values = rotation_loop()
        Renderer.reset()
        return values

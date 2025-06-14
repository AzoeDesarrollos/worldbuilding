from engine.frontend.graphs.orbital_properties import rotation_loop
from engine.frontend.globales import Renderer
from .general import Ellipse, Flagable, Point
from math import sqrt, pow, cos, sin, acos
from engine.backend import q
from decimal import Decimal
from .space import Universe


class RawOrbit:
    _unit = ''
    temperature = ''
    resonant = False
    id = None

    stable = False

    stability_overriten = False

    subtype = 'Raw'

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

    def __repr__(self):
        return 'Orbit @' + '{:}'.format(round(float(self), 3))

    def __eq__(self, other):
        return self.id == other.id

    def __int__(self):
        return round(self.a.m)

    def __index__(self):
        return round(self.a.m)

    def __float__(self):
        return float(self.semi_major_axis.m)

    def __lt__(self, other):
        return self.semi_major_axis.m < other

    def __gt__(self, other):
        return self.semi_major_axis.m > other


class PseudoOrbit:
    eccentricity = ''
    inclination = ''
    semi_major_axis = 0
    temperature = 0
    _star = None
    _period = 0
    resonant = False

    stable = False

    stability_overriten = False

    subtype = 'Incomplete'

    def __init__(self, orbit):
        self.semi_major_axis = orbit.semi_major_axis
        self.temperature = orbit.temperature
        self._star = orbit.star
        if not hasattr(self._star, 'letter') or self._star.letter is None:
            self._period = q(sqrt(pow(self.semi_major_axis.m, 3) / self._star.mass.m), 'year')
        elif self._star.letter == 'P':
            self._period = q(sqrt(pow(self.semi_major_axis.m, 3) / self._star.shared_mass.m), 'year')
        self.resonant = orbit.resonant

        if hasattr(orbit, 'e'):
            self.eccentricity = orbit.e

        if hasattr(orbit, 'i'):
            self.inclination = orbit.i

    @property
    def a(self):
        return self.semi_major_axis

    @property
    def star(self):
        return self._star

    def get_period(self):
        return self._period


class Orbit(Flagable, Ellipse):
    period: q = None
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

    id = None
    resonant = False
    resonance = None
    resonant_order = ''

    stable = False

    stability_overriten = False
    migrated = False

    subtype = 'Orbit'

    def __init__(self, id, a, e, i, unit):
        super().__init__(a, e)
        self._unit = unit
        assert 0 <= float(i.m) <= 180, 'inclination values range from 0 to 180 degrees.'
        self._i = float(i.m)
        self._Q = abs(self._a * (1 + self._e))
        self._q = abs(self._a * (1 - self._e))
        self.set_focus(self._q)
        self.id = id

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

    def __repr__(self):
        return 'Orbit @' + str(round(self.semi_major_axis.m, 3))

    def set_astrobody(self, main, astro_body):
        self.astrobody = astro_body
        self._temperature = astro_body.temperature
        self._star = main
        astro_body.set_parent(main)

        if main.celestial_type == "planet" or main.celestial_type == 'asteroid':
            self.reset_period_and_speed(main)

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

    def set_focus(self, periapsis):
        peri_point = Point(periapsis, name='Periapsis')
        foci = [self.f1, self.f2]
        closeness = [focus.how_close(peri_point) for focus in foci]
        self.focus = foci[closeness.index(min(closeness))]

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
        self._Q = abs(self._a * (1 + self._e))
        self._q = abs(self._a * (1 - self._e))
        if self.temperature != 'N/A':
            self._temperature = self.astrobody.set_temperature(self._star.mass.m, self._a)
        self.reset_period_and_speed(self._star)
        Universe.visibility_by_albedo()

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

    def reset_period_and_speed(self, main):
        raise NotImplementedError

    def __eq__(self, other):
        return self.id == other.id


class PlanetOrbit(Orbit):
    primary = 'Star'

    subtype = 'Planetary'

    def __init__(self, star, id, a, e, i, loan=None, aop=None):
        super().__init__(id, a, e, i, 'au')
        self.reset_period_and_speed(star)
        if loan is None and aop is None:
            orbital_properties = set_orbital_properties(self._i)
            self.longitude_of_the_ascending_node = orbital_properties[0]
            self.argument_of_periapsis = orbital_properties[1]
        else:
            if type(loan) is int or type(loan) is float:
                loan = q(loan, 'degree')
            self.longitude_of_the_ascending_node = loan
            self.argument_of_periapsis = aop if type(aop) is str else q(aop, 'degree')

    def reset_period_and_speed(self, main):
        if main.letter is None:
            main_body_mass = main.mass.m
        else:
            main_body_mass = main.shared_mass.m
        self.period = q(sqrt(pow(self._a, 3) / main_body_mass), 'year')
        self.velocity = q(sqrt(main_body_mass / self._a), 'earth_orbital_velocity').to('kilometer per second')


class SatelliteOrbit(Orbit):
    primary = 'Planet'

    subtype = 'Satellital'

    def __init__(self, id, a, e, i, loan=None, aop=None):
        super().__init__(id, a, e, i, 'earth_radius')
        if loan is None and aop is None:
            orbital_properties = set_orbital_properties(self._i)
            self.longitude_of_the_ascending_node = orbital_properties[0]
            self.argument_of_periapsis = orbital_properties[1]
        else:
            self.longitude_of_the_ascending_node = loan
            self.argument_of_periapsis = aop

    def reset_period_and_speed(self, main):
        main_body_mass = main.mass.m
        satellite_mass = round(self.astrobody.mass.m, 3)
        self.velocity = q(sqrt(main_body_mass / self._a), 'earth_orbital_velocity').to('kilometer per second')
        if main.habitable:
            self.period = q(round(0.0588 * sqrt(pow(self._a, 3) / (main_body_mass + satellite_mass)), 2), 'day')
        else:
            self.period = q(sqrt(pow(self.a.to('au').m, 3) / (main_body_mass + satellite_mass)), 'year').to('day')


class BinaryStarOrbit(Orbit):
    subtype = 'StellarBinary'

    def __init__(self, star, other, id, a, e):
        super().__init__(id, a, e, q(0, 'degrees'), 'au')
        self.reset_period_and_speed(star.mass.m + other.mass.m)

    def reset_period_and_speed(self, main_body_mass):
        self.period = q(sqrt(pow(self._a, 3) / main_body_mass), 'year')
        self.velocity = q(sqrt(main_body_mass / self._a), 'earth_orbital_velocity').to('kilometer per second')


class BinaryPlanetOrbit(Orbit):
    primary = 'Star'

    subtype = 'PlanetaryBinary'

    def __init__(self, planet, other, id, a, e):
        super().__init__(id, a, e, q(0, 'degrees'), 'earth_radius')
        self.reset_period_and_speed(planet.mass.m + other.mass.m)

    def reset_period_and_speed(self, main_body_mass):
        self.period = q(sqrt(pow(self._a, 3) / main_body_mass), 'year')
        self.velocity = q(sqrt(main_body_mass / self._a), 'earth_orbital_velocity').to('kilometer per second')


class GalacticNeighbourhoodOrbit(Orbit):
    subtype = 'Galatic'

    def __init__(self, a):
        super().__init__(q(a, 'light_years'), q(0), q(0, 'degrees'), unit='light_years')
        # age = self.star.age.m
        # self.star.z = q(49 * cos((2 * pi / 72) * age), 'kpc')
        # # z difined as the star's shift ("bobbing") with respect to the galactic plane
        # # also, this fuction is completely made up, as the actual formula dependes on observational data.

    def reset_period_and_speed(self, main):
        raise NotImplementedError


class NeighbourhoodSystemOrbit(Orbit):
    subtype = 'Neighbourhood'

    def __init__(self, id, x, y, z, offset):
        # spherical coordinates
        rho = sqrt(x ** 2 + y ** 2 + z ** 2)
        phi = acos(z / rho)
        super().__init__(id, q(rho + offset, 'light_years'), q(0), q(phi, 'degrees'), unit='light_years')


def from_stellar_resonance(star, planet, resonance: str):
    """Return the semi-major axis in AU of the resonant orbit.

    The resonance argument is a string in the form of 'x:y'
    where both x and y are integers and x >= y.
    """
    x, y = [int(i) for i in resonance.split(':')]
    period = (x / y) * planet.orbit.period.to('year').m
    semi_major_axis = q(pow(pow(period, 2) * star.mass.to('sol_mass').m, (1 / 3)), 'au')
    return semi_major_axis


def from_planetary_resonance(planet, satellite, resonance: str):
    """Return the semi-major axis in Re of the resonant orbit.

    The resonance argument is a string in the form of 'x:y'
    where both x and y are integers and x >= y.
    """

    x, y = [int(i) for i in resonance.split(':')]
    period = (x / y) * satellite.orbit.period.to('year').m
    mass = planet.mass.m + satellite.mass.m  # earth masses
    semi_major_axis = q(pow(pow(period, 2) * mass, (1 / 3)), 'au')
    return semi_major_axis.to('earth_radius')


def from_satellite_resonance(satellite, resonance: str):
    x, y = [int(i) for i in resonance.split(':')]
    period = (x / y) * satellite.orbit.period.to('year').m
    semi_major_axis = q(pow(pow(period, 2) * satellite.mass.m, (1 / 3)), 'au')
    return semi_major_axis.to('earth_radius')


def set_orbital_properties(inclination):
    if inclination in (0, 180):
        return q(0, 'degree'), 'undefined'
    else:
        values = rotation_loop()
        Renderer.reset()
        return values


def in_resonance(marker_a, marker_b):
    starred_markers = [m for m in [marker_a, marker_b] if hasattr(m, 'star')]
    if not len(starred_markers):
        raise ValueError("None of the markers are linked to a star to stablish their periods")
    else:
        star = starred_markers[0].star

    if type(marker_a) is float:
        period_a = sqrt(pow(marker_a, 3) / star.mass.m)
    elif hasattr(marker_a.orbit, 'period'):
        period_a = marker_a.orbit.period.to('years').m
    else:
        period_a = sqrt(pow(marker_a.orbit.a.m, 3) / star.mass.m)

    if type(marker_b) is float:
        period_b = sqrt(pow(marker_b, 3) / star.mass.m)
    elif hasattr(marker_b.orbit, 'period'):
        period_b = marker_b.orbit.period.to('years').m
    else:
        period_b = sqrt(pow(marker_b.orbit.a.m, 3) / star.mass.m)

    r = period_a / period_b if period_a < period_b else period_b / period_a
    ratio = Decimal(r)
    x, y = ratio.as_integer_ratio()
    if len(str(x)) <= 3 and len(str(y)) <= 3:
        return ':'.join([str(x), str(y)])
    else:
        return False

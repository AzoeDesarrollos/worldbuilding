from .orbit import BinaryPlanetOrbit, PlanetOrbit  # , BinaryStarOrbit
# from engine.backend.util import roll, generate_id, q
from engine.backend.util import generate_id, q
from .orbit import BinaryStarOrbit
from .general import Flagable
from .space import Universe
from .planet import Planet
from math import sqrt


class AbstractBinary(Flagable):
    primary = None
    secondary = None
    average_separation = 0
    barycenter = 0
    max_sep, min_sep = 0, 0
    inner_forbbiden_zone = 0
    outer_forbbiden_zone = 0
    ecc_p, ecc_s = 0, 0

    def __init__(self, primary, secondary, avgsep, ep=0, es=0, unit='au'):
        if secondary.mass <= primary.mass:
            self.primary = primary
            self.secondary = secondary
        else:
            self.primary = secondary
            self.secondary = primary

        self.ecc_p = q(ep)
        self.ecc_s = q(es)
        self.average_separation = q(avgsep, unit)
        self.barycenter = q(avgsep * (self.secondary.mass.m / (self.primary.mass.m + self.secondary.mass.m)), unit)
        self.primary_distance = round(self.barycenter, 2)
        self.secondary_distance = round(self.average_separation - self.primary_distance, 2)

        assert 0.4 <= ep <= 0.7, 'Primary eccentricity must be between 0.4 and 0.7'
        max_sep_p, min_sep_p = self.calculate_distances(ep, self.primary_distance.m, unit)

        assert 0.4 <= es <= 0.7, 'Secondary eccentricity must be between 0.4 and 0.7'
        max_sep_s, min_sep_s = self.calculate_distances(es, self.secondary_distance.m, unit)

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s

        self.primary_max_sep = max_sep_p
        self.secondary_max_sep = max_sep_s

    @staticmethod
    def calculate_distances(e, ref, unit):
        max_sep = q((1 + e) * round(ref, 2), unit)
        min_sep = q((1 - e) * round(ref, 2), unit)
        return max_sep, min_sep


class BinarySystem(AbstractBinary):
    celestial_type = 'system'

    letter = ''
    system_name = ''
    has_name = False
    name = None

    idx = None
    shared_mass = None

    parent = None

    _orbit_type = BinaryStarOrbit

    position = None

    def __init__(self, name, primary, secondary, avgsep, ep=0, es=0, unit='au', id=None):
        super().__init__(primary, secondary, avgsep, ep=ep, es=es, unit=unit)

        if name is None:
            self.has_name = False
        else:
            self.name = name
            self.has_name = True

        self.system_name = self.__repr__()

        # ID values make each system unique, even if they have the same stars and separation.
        self.id = id if id is not None else generate_id()

    def __str__(self):
        return self.letter + '-Type #{}'.format(self.idx)

    def __repr__(self):
        return self.letter + '-Type Binary System'

    def __eq__(self, other):
        return hasattr(other, 'primary') and all([
            self.primary == other.primary,
            self.secondary == other.secondary,
            self.average_separation == other.average_separation,  # distinguishes P-type from S-type systems
            self.id == other.id])

    def __hash__(self):
        return hash((hash(self.primary), hash(self.secondary), self.average_separation, self.id))

    def __getitem__(self, item):
        if type(item) is int:
            if item == 0:
                return self.primary
            elif item == 1:
                return self.secondary
            raise StopIteration()

    def composition(self):
        return [self.primary, self.secondary]

    @property
    def system(self):
        return self

    @property
    def mass(self):
        return self.shared_mass

    def compare(self, other):
        if hasattr(other, 'letter'):
            return self.letter == other.letter
        else:
            return False

    def set_parent(self, parent):
        self.parent = parent

    def set_name(self, name):
        self.name = name
        self.has_name = True


class PTypeSystem(BinarySystem):
    letter = 'P'

    habitable_inner = 0
    habitable_outer = 0
    inner_boundry = 0
    outer_boundry = 0
    frost_line = 0

    luminosity = 0
    radius = 0

    def __init__(self, primary, secondary, avgsep, ep=0, es=0, id=None, name=None):
        super().__init__(name, primary, secondary, avgsep, ep, es, id=id)
        self.primary.orbit = self._orbit_type(self.primary, self.secondary, self.primary_max_sep, self.ecc_p)
        self.secondary.orbit = self._orbit_type(self.secondary, self.primary, self.secondary_max_sep, self.ecc_s)

        assert self.min_sep.m > 0.1, "Stars will merge at {:~} minimum distance".format(self.min_sep)
        self.primary.set_parent(self)
        self.secondary.set_parent(self)
        self._mass = primary.mass + secondary.mass
        self._radius = max([primary.radius, secondary.radius]).m
        self._luminosity = primary.luminosity + secondary.luminosity
        self.temperature_mass = self._mass.m

        self._habitable_inner = round(sqrt(self._luminosity.m / 1.1), 3)
        self._habitable_outer = round(sqrt(self._luminosity.m / 0.53), 3)
        self._inner_boundry = round(self._mass.m * 0.01, 3)
        self._outer_boundry = round(self._mass.m * 40, 3)
        self._frost_line = round(4.85 * sqrt(self._luminosity.m), 3)
        self.set_qs()
        self.spin = self.primary.spin

        self.inner_forbbiden_zone = q(round(self.min_sep.m / 3, 3), 'au')
        self.outer_forbbiden_zone = q(round(self.max_sep.m * 3, 3), 'au')

        self.habitable_orbit = round(self.max_sep * 4, 3)
        age = max([self.primary.age, self.secondary.age])
        self.age = age
        self.evolution_id = self.id

    def set_qs(self):
        self.shared_mass = q(self._mass.m, 'sol_mass')
        self.radius = q(self._radius, 'sol_radius')
        self.luminosity = q(self._luminosity.m, 'sol_luminosity')
        self.habitable_inner = q(self._habitable_inner, 'au')
        self.habitable_outer = q(self._habitable_outer, 'au')
        self.inner_boundry = q(self._inner_boundry, 'au')
        self.outer_boundry = q(self._outer_boundry, 'au')
        self.frost_line = q(self._frost_line, 'au')

    def validate_orbit(self, orbit):
        return self._inner_boundry < orbit < self._outer_boundry


class STypeSystem(BinarySystem):
    letter = 'S'

    def __init__(self, primary, secondary, avgsep, ep=0, es=0, id=None, name=None):
        super().__init__(name, primary, secondary, avgsep, ep, es, id=id)
        self.primary.orbit = self._orbit_type(self.primary, self.secondary, self.primary_max_sep, self.ecc_p)
        self.secondary.orbit = self._orbit_type(self.secondary, self.primary, self.secondary_max_sep, self.ecc_s)
        self.primary.set_parent(self)
        self.secondary.set_parent(self)
        self.shared_mass = primary.mass + secondary.mass

        self.inner_forbbiden_zone = q(round(self.min_sep.m / 3, 3), 'au')
        self.outer_forbbiden_zone = q(round(self.max_sep.m * 3, 3), 'au')
        for star in self.composition():
            if star.letter is None:
                inner = self.inner_forbbiden_zone
                outer = self.outer_forbbiden_zone
                star.inherit(self, inner, outer, self.shared_mass)


class PlanetaryPTypeSystem(BinarySystem, Planet):
    celestial_type = 'binary planet'
    letter = 'P'
    _orbit_type = BinaryPlanetOrbit
    orbit = None
    relative_size = ''

    def __init__(self, star, primary, secondary, avg, ep=0, es=0):
        super().__init__('Not Set', primary, secondary, avg, ep, es, unit='earth_radius')

        # this is Planet.set_orbit(), not PlanetaryPTypeSystem.set_orbit()
        self.primary.set_orbit(star, [secondary, self.primary_max_sep, self.ecc_p], abnormal=True)
        self.secondary.set_orbit(star, [primary, self.secondary_max_sep, self.ecc_s], abnormal=True)

        self._mass = primary.mass + secondary.mass
        self.shared_mass = q(self._mass.m, 'earth_mass')
        if primary.relative_size == secondary.relative_size:
            self.relative_size = primary.relative_size

    def __repr__(self):
        return 'P-Type Planetary System'

    def set_orbit(self, star, orbital_parameters, abnormal=False):
        # the orbit of the whole system is a planetary orbit since it orbits a star, presumably
        self.orbit = PlanetOrbit(star, *orbital_parameters)
        self.temperature = 'undefined'
        self.orbit.set_astrobody(star, self)
        self.primary.parent = self
        self.secondary.parent = self
        self.parent = star
        Universe.visibility_by_albedo()
        return self.orbit


def system_type(separation):
    if 0.15 <= float(separation) <= 6:  # or 1.5 <= float(separation) <= 60?
        system = PTypeSystem
    elif (120 <= float(separation) <= 600) or (1200 <= float(separation) <= 60000):
        system = STypeSystem
    else:
        raise AssertionError('The Average Separation\nis incompatible with\n'
                             'S-Type (120 to 600 AU)\nor\n'
                             'P-Type (0.15 to 6 AU) systems')
    return system

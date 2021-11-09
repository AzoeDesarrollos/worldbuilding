from engine.backend.util import roll, generate_id
from .orbit import BinaryStarOrbit
from .general import Flagable
from math import sqrt
from engine import q


class BinarySystem(Flagable):
    celestial_type = 'system'

    primary = None
    secondary = None
    average_separation = 0
    barycenter = 0
    max_sep, min_sep = 0, 0
    inner_forbbiden_zone = 0
    outer_forbbiden_zone = 0
    ecc_p, ecc_s = 0, 0
    letter = ''
    system_name = ''
    has_name = False

    idx = None
    shared_mass = None

    def __init__(self, name, primary, secondary, avgsep, ep=0, es=0, id=None):
        if secondary.mass <= primary.mass:
            self.primary = primary
            self.secondary = secondary
        else:
            self.primary = secondary
            self.secondary = primary

        if name is None:
            self.has_name = False
            self.name = str(self)
        else:
            self.name = name
            self.has_name = True

        self.ecc_p = q(ep)
        self.ecc_s = q(es)
        self.average_separation = q(avgsep, 'au')
        self.barycenter = q(avgsep * (self.secondary.mass.m / (self.primary.mass.m + self.secondary.mass.m)), 'au')
        self.primary_distance = round(self.barycenter, 2)
        self.secondary_distance = round(self.average_separation - self.primary_distance, 2)

        self.primary.orbit = BinaryStarOrbit(self.primary, self.secondary, self.primary_distance, self.ecc_p)
        self.secondary.orbit = BinaryStarOrbit(self.secondary, self.primary, self.secondary_distance, self.ecc_s)

        self.system_name = self.__repr__()

        # ID values make each system unique, even if they have the same stars and separation.
        self.id = id if id is not None else generate_id()

    @staticmethod
    def calculate_distances(e, ref):
        max_sep = q((1 + e) * round(ref, 2), 'au')
        min_sep = q((1 - e) * round(ref, 2), 'au')
        return max_sep, min_sep

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


class PTypeSystem(BinarySystem):
    letter = 'P'

    habitable_inner = 0
    habitable_outer = 0
    inner_boundry = 0
    outer_boundry = 0
    frost_line = 0

    luminosity = 0

    def __init__(self, primary, secondary, avgsep, ep=0, es=0, pos=None, id=None, name=None):
        super().__init__(name, primary, secondary, avgsep, ep, es, id=id)

        assert 0.4 <= ep <= 0.7, 'Primary eccentricity must be between 0.4 and 0.7'
        max_sep_p, min_sep_p = self.calculate_distances(ep, self.primary_distance.m)

        assert 0.4 <= es <= 0.7, 'Secondary eccentricity must be between 0.4 and 0.7'
        max_sep_s, min_sep_s = self.calculate_distances(es, self.secondary_distance.m)

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s
        assert self.min_sep.m > 0.1, "Stars will merge at {:~} minimum distance".format(self.min_sep)

        self._mass = primary.mass + secondary.mass
        self._luminosity = primary.luminosity + secondary.luminosity

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
        self.position = [round(roll(0, 1000)) if pos is None else pos['x'],
                         round(roll(0, 1000)) if pos is None else pos['y'],
                         round(roll(0, 1000)) if pos is None else pos['z']]

    def set_qs(self):
        self.shared_mass = q(self._mass.m, 'sol_mass')
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

        assert 0.4 <= ep <= 0.7, 'Primary eccentricity must be between 0.4 and 0.7'
        max_sep_p, min_sep_p = self.calculate_distances(ep, self.average_separation.m)

        assert 0.4 <= es <= 0.7, 'Secondary eccentricity must be between 0.4 and 0.7'
        max_sep_s, min_sep_s = self.calculate_distances(es, self.average_separation.m)

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s
        self.shared_mass = primary.mass + secondary.mass

        self.inner_forbbiden_zone = q(round(self.min_sep.m / 3, 3), 'au')
        self.outer_forbbiden_zone = q(round(self.max_sep.m * 3, 3), 'au')
        for star in self.composition():
            inner = self.inner_forbbiden_zone
            outer = self.outer_forbbiden_zone
            star.inherit(self, inner, outer, self.shared_mass)


def system_type(separation):
    if 0.15 <= float(separation) < 6:
        system = PTypeSystem
    elif 120 <= float(separation) <= 600:
        system = STypeSystem
    else:
        raise AssertionError('The Average Separation is incompatible with\n'
                             'S-Type (120 to 600 AU) or\n'
                             'P-Type (0.15 to 6 AU) systems')
    return system

from engine import q
from math import sqrt
from datetime import datetime


class BinarySystem:
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

    def __init__(self, name, primary, secondary, avgsep, ep=0, es=0):
        if secondary.mass <= primary.mass:
            self.primary = primary
            self.secondary = secondary
        else:
            self.primary = secondary
            self.secondary = primary

        if name is None:
            self.has_name = False
            self.name = 'NoName'
        else:
            self.name = name

        self.ecc_p = q(ep)
        self.ecc_s = q(es)
        self.average_separation = q(avgsep, 'au')
        self.barycenter = q(avgsep * (self.secondary.mass.m / (self.primary.mass.m + self.secondary.mass.m)), 'au')
        self.primary_distance = round(self.barycenter, 2)
        self.secondary_distance = round(self.average_separation - self.primary_distance, 2)

        self.system_name = self.__repr__()

        # ID values make each system unique, even if they have the same stars and separation.
        self.id = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])

    @staticmethod
    def calculate_distances(e, ref):
        max_sep = q((1 + e) * round(ref, 2), 'au')
        min_sep = q((1 - e) * round(ref, 2), 'au')
        return max_sep, min_sep

    def __str__(self):
        return self.letter+'-Type'

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


class PTypeSystem(BinarySystem):
    letter = 'P'

    habitable_inner = 0
    habitable_outer = 0
    inner_boundry = 0
    outer_boundry = 0
    frost_line = 0

    mass = 0
    luminosity = 0

    def __init__(self, primary, secondary, avgsep, ep=0, es=0, name=None):
        super().__init__(name, primary, secondary, avgsep, ep, es)

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
        self._inner_boundry = self._mass.m * 0.01
        self._outer_boundry = self._mass.m * 40
        self._frost_line = round(4.85 * sqrt(self._luminosity.m), 3)
        self.set_qs()

        self.inner_forbbiden_zone = q(self.min_sep.m / 3, 'au')
        self.outer_forbbiden_zone = q(self.max_sep.m * 3, 'au')
        print('habitable world must orbit at {:~}'.format(self.max_sep * 4))

    def set_qs(self):
        self.mass = q(self._mass.m, 'sol_mass')
        self.luminosity = q(self._luminosity.m, 'sol_luminosity')
        self.habitable_inner = q(self._habitable_inner, 'au')
        self.habitable_outer = q(self._habitable_outer, 'au')
        self.inner_boundry = q(self._inner_boundry, 'au')
        self.outer_boundry = q(self._outer_boundry, 'au')
        self.frost_line = q(self._frost_line, 'au')


class STypeSystem(BinarySystem):
    letter = 'S'

    def __init__(self, primary, secondary, avgsep, ep=0, es=0, name=None):
        super().__init__(name, primary, secondary, avgsep, ep, es)

        assert 0.4 <= ep <= 0.7, 'Primary eccentricity must be between 0.4 and 0.7'
        max_sep_p, min_sep_p = self.calculate_distances(ep, self.average_separation.m)

        assert 0.4 <= es <= 0.7, 'Secondary eccentricity must be between 0.4 and 0.7'
        max_sep_s, min_sep_s = self.calculate_distances(es, self.average_separation.m)

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s

        self.inner_forbbiden_zone = q(self.min_sep.m / 3, 'au')
        self.outer_forbbiden_zone = q(self.max_sep.m * 3, 'au')


def system_type(separation):
    if 0.15 <= float(separation) < 6:
        system = PTypeSystem
    elif 120 <= float(separation) <= 600:
        system = STypeSystem
    else:
        raise AssertionError('the Average Separation is incompatible with S-Type or P-Type systems')
    return system

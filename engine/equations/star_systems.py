from engine import q


class BinarySystem:
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

    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        if secondary.mass <= primary.mass:
            self.primary = primary
            self.secondary = secondary
        else:
            self.primary = secondary
            self.secondary = primary

        self.ecc_p = q(ep)
        self.ecc_s = q(es)
        self.average_separation = q(avgsep, 'au')
        self.barycenter = q(avgsep * (self.secondary.mass.m / (self.primary.mass.m + self.secondary.mass.m)), 'au')
        self.primary_distance = round(self.barycenter, 2)
        self.secondary_distance = round(self.average_separation - self.primary_distance, 2)

        self.system_name = self.__repr__()

    @staticmethod
    def calculate_distances(e, ref):
        max_sep = q((1 + e) * round(ref, 2), 'au')
        min_sep = q((1 - e) * round(ref, 2), 'au')
        return max_sep, min_sep

    def __repr__(self):
        return self.letter + '-Type Binary System'


class PTypeSystem(BinarySystem):
    letter = 'P'

    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        super().__init__(primary, secondary, avgsep, ep, es)

        assert 0.4 <= ep <= 0.7
        max_sep_p, min_sep_p = self.calculate_distances(ep, self.primary_distance.m)

        assert 0.4 <= es <= 0.7
        max_sep_s, min_sep_s = self.calculate_distances(es, self.secondary_distance.m)

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s
        assert self.min_sep.m > 0.1, "Stars will merge at {:~} minimum distance".format(self.min_sep)

        self.inner_forbbiden_zone = q(self.min_sep.m / 3, 'au')
        self.outer_forbbiden_zone = q(self.max_sep.m * 3, 'au')
        print('habitable world must orbit at {:~}'.format(self.max_sep * 4))

        # combined_mass = primary.mass + secondary.mass
        # combined_luminosity = primary.luminosity + secondary.luminosity
        # super().__init__(combined_mass, combined_luminosity)


class STypeSystem(BinarySystem):
    letter = 'S'

    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        assert 120 <= avgsep <= 600
        super().__init__(primary, secondary, avgsep, ep, es)

        assert 0.4 <= ep <= 0.7
        max_sep_p, min_sep_p = self.calculate_distances(ep, self.average_separation.m)

        assert 0.4 <= es <= 0.7
        max_sep_s, min_sep_s = self.calculate_distances(es, self.average_separation.m)

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s

        self.inner_forbbiden_zone = q(self.min_sep.m / 3, 'au')
        self.outer_forbbiden_zone = q(self.max_sep.m * 3, 'au')

        # self.primary_system = PlanetarySystem(primary.mass, primary.luminosity)
        # self.secondary_system = PlanetarySystem(secondary.mass, secondary.luminosity)


def system_type(separation):
    if 0.15 <= float(separation) < 6:
        system = PTypeSystem
    elif 120 <= float(separation) <= 600:
        system = STypeSystem
    else:
        raise AssertionError('the Average Separation is incompatible with S-Type or P-Type systems')
    return system

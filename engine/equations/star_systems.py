class BinarySystem:
    primary = None
    secondary = None
    average_separation = 0
    barycenter = 0
    max_sep, min_sep = 0, 0
    inner_forbbiden_zone = 0
    outer_forbbiden_zone = 0
    e_p, e_s = 0, 0

    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        if secondary.mass <= primary.mass:
            self.primary = primary
            self.secondary = secondary
        else:
            self.primary = secondary
            self.secondary = primary

        self.average_separation = avgsep
        self.barycenter = avgsep * (self.secondary.mass / (self.primary.mass + self.secondary.mass))

        assert 0.4 <= ep <= 0.7
        max_sep_p = (1 + ep) * avgsep
        min_sep_p = (1 - ep) * avgsep

        assert 0.4 <= es <= 0.7
        max_sep_s = (1 + es) * avgsep
        min_sep_s = (1 - es) * avgsep

        self.max_sep = max_sep_p + max_sep_s
        self.min_sep = min_sep_p + min_sep_s

        self.inner_forbbiden_zone = self.min_sep / 3
        self.outer_forbbiden_zone = self.min_sep * 3


class PTypeSystem(BinarySystem):
    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        assert 0.15 < avgsep < 6, 'Average Separation too pronounced'
        assert secondary.mass > 0.08, "it's not a star"
        super().__init__(primary, secondary, avgsep, ep, es)

        print('habitable world must orbit at', self.max_sep * 4)

        # combined_mass = primary.mass + secondary.mass
        # combined_luminosity = primary.luminosity + secondary.luminosity
        # super().__init__(combined_mass, combined_luminosity)

    def __repr__(self):
        return 'P-Type Star System'


class STypeSystem(BinarySystem):
    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        assert 120 <= avgsep <= 600
        super().__init__(primary, secondary, avgsep, ep, es)
        # self.primary_system = PlanetarySystem(primary.mass, primary.luminosity)
        # self.secondary_system = PlanetarySystem(secondary.mass, secondary.luminosity)

    def __repr__(self):
        return 'S-Type Star System'

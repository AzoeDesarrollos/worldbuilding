from math import sqrt


# from random import uniform
# from .orbit import StandardOrbit
# from .orbit import ClassicalGasGiantOrbit, TerrestialOrbit


class PlanetarySystem:
    stable_orbits = None
    inner_boundry = 0
    outer_boundry = 0

    def __init__(self, star_mass, star_luminosity):
        self.stable_orbits = []
        self.star_mass = star_mass
        self.star_luminosity = star_luminosity

        self.inner_boundry = star_mass * 0.01
        self.outer_boundry = star_mass * 40

        self.frost_line = 4.85 * sqrt(star_luminosity)
        self.habitable_zone_inner = sqrt(star_luminosity / 1.1)
        self.habitable_zone_outer = sqrt(star_luminosity / 0.53)

        # self.stable_orbits = [ClassicalGasGiantOrbit(self, a,e,i, name='largest_gas_giant_orbit')]

    # def add_distant_orbits(self, variance):
    #     """Do not run this method after check_orbits()"""
    #     assert 1.4 <= variance =< 2.0,'j'
    #     orbit = self.stable_orbits[0].semi_major_axis*variance
    #     # if self.inner_boundry < orbit < self.outer_boundry:
    #         # self.stable_orbits.append(StandardOrbit(self, orbit))
    #
    # def add_closing_orbits(self, variance):
    #     """Do not run this method after check_orbits()"""
    #     assert 1.4 <= variance =< 2.0
    #     orbit = self.stable_orbits[0].semi_major_axis/variance
    #     # if self.inner_boundry < orbit < self.outer_boundry:
    #         # self.stable_orbits.append(StandardOrbit(self, orbit))

    def check_orbits(self):
        """Run this method only after adding all the orbits"""
        self.stable_orbits.sort(key=lambda orbit: orbit.semi_major_axis)
        orbits = self.stable_orbits
        delete = []
        lenght = len(self.stable_orbits)
        for i in range(len(self.stable_orbits)):
            if not orbits[i].has_name and i + 1 < lenght:
                if orbits[i].semi_major_axis + 0.15 > orbits[i + 1].semi_major_axis:
                    delete.append(orbits[i])

        for flagged in delete:
            if flagged in self.stable_orbits:
                self.stable_orbits.remove(flagged)


class SolarSystem(PlanetarySystem):
    def __init__(self, star):
        super().__init__(star.mass, star.luminosity)

    def __repr__(self):
        return 'Solar Star System'


class BinarySystem:
    primary = None
    secondary = None
    average_separation = 0
    baricenter = 0
    max_sep, min_sep = 0, 0
    inner_forbbiden_zone = 0
    outer_forbbiden_zone = 0

    def build(self, primary, secondary, avgsep, ep=0, es=0):
        assert secondary.mass <= primary.mass
        self.primary = primary
        self.secondary = secondary
        self.average_separation = avgsep
        self.baricenter = avgsep * (secondary.mass / (primary.mass + secondary.mass))

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


class PTypeSystem(BinarySystem, PlanetarySystem):
    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        assert 0.15 < avgsep < 6, 'Average Separation too pronounced'
        assert secondary.mass > 0.08, "it's not a star"
        super().build(primary, secondary, avgsep, ep, es)

        print('habitable world must orbit at', self.max_sep * 4)

        combined_mass = primary.mass + secondary.mass
        combined_luminosity = primary.luminosity + secondary.luminosity
        super().__init__(combined_mass, combined_luminosity)

    def __repr__(self):
        return 'P-Type Star System'


class STypeSystem(BinarySystem):
    def __init__(self, primary, secondary, avgsep, ep=0, es=0):
        assert 120 <= avgsep <= 600
        super().build(primary, secondary, avgsep, ep, es)
        self.primary_system = PlanetarySystem(primary.mass, primary.luminosity)
        self.secondary_system = PlanetarySystem(secondary.mass, secondary.luminosity)

    def __repr__(self):
        return 'S-Type Star System'

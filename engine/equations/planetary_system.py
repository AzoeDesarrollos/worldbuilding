from math import sqrt


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

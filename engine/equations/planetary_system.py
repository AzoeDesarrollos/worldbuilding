class PlanetarySystem:
    stable_orbits = None
    inner_boundry = 0
    outer_boundry = 0

    def __init__(self):
        self.stable_orbits = []

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

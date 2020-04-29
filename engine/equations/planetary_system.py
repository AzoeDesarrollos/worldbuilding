from engine.backend.randomness import roll
from .orbit import RawOrbit, Orbit
from .planet import temp_by_pos
from bisect import bisect_right, bisect_left


class PlanetarySystem:
    raw_orbits = None
    stable_orbits = None
    planets = None

    def __init__(self, star):
        self.star = star
        self.raw_orbits = []
        self.stable_orbits = []
        self._axes = []
        self.planets = []

    def add_planet(self, planet):
        """Se puede correr éte metodo primero, añadiendo planetas en orbitas aleatorias o se puede correr add_orbits()
        primero, y colocar los planetas en las órbitas precalculadas.
        """

        self.planets.append(planet)
        avg_e = 0.584 * len(self.planets) ** (-1.2)
        avg_i = 2  # éste valor es arbitrario y es igual al de nuestro sistema solar.

        a, e, i = 0, 0, 0
        if planet.clase == 'Terrestial Planet':
            if planet.habitable:
                a = temp_by_pos(self.star)
                idx = bisect_left(self._axes, a)
                del self._axes[idx], self.raw_orbits[idx]
                self._axes.insert(idx, a)
                self.raw_orbits.insert(idx, a)
                e = roll(0.0, 0.2)
                i = 0
            else:
                a = roll(self.star.inner_boundry.m, self.star.frost_line.m - 1.2)
                e = roll(0.0, 1.0)
                i = roll(0.0, 180.0)
            self.stable_orbits.append(Orbit(a, e, i))

        elif planet.clase in ('Gas Giant', 'Puffy Giant'):
            # if this is the largest, it should occupy the fist orbit away from the frostline
            if max([p.mass.m for p in self.planets if planet.clase in ('Gas Giant', 'Puffy Giant')]):
                idx = bisect_right(self._axes, self.star.frost_line.m)
                a = self._axes[idx]
            else:
                a = roll(self.star.frost_line + 1, self.star.outer_boundry)
            e = roll(0.001, 0.09)
            i = roll(0.0, 90.0)
            self.stable_orbits.append(Orbit(a, e, i))

        elif planet.clase == 'Super Jupiter':
            a = roll(0.04, self.star.frost_line + 1.2)  # migration
            e = roll(0.001, 0.09)
            i = roll(0.0, 90.0)

        elif planet.clase == 'Gas Dwarf':
            a = roll(self.star.frost_line + 1.2, self.star.outer_boundry)
            # for extra added realism, the orbit should be very distant.
            i = roll(0.0, 90.0)
            e = roll(0.001, 0.09)

        elif planet.clase == 'Eccentric Jupiter':
            a = roll(self.star.inner_boundry.m, self.star.outer_boundry.m)
            e = roll(0.1, 0.2) if any([p.habitable for p in self.planets]) else roll(0.1, 0.9)
            i = roll(0.0, 90.0)

        elif planet.clase == 'Dwarf Planet':
            # no data. only resonant orbits
            pass

        elif planet.clase == 'Hot Jupiter':
            e = roll(0.001, 0.09)  # migration
            a = roll(0.04, 0.5)
            i = roll(10, 170)

        while (sum([o.e for o in self.stable_orbits]) / len(self.stable_orbits)).m > avg_e:
            for orbit in self.raw_orbits:
                if orbit.eccentricity > 0:
                    orbit.eccentricity -= 0.01

        while (sum([o.i for o in self.stable_orbits]) / len(self.stable_orbits)).m > avg_i:
            for orbit in self.raw_orbits:
                if orbit.inclination > 0:
                    orbit.inclination -= 0.01

        print(a, e, i)

    def check_orbits(self):
        """Run this method only after adding all the orbits"""
        self.raw_orbits.sort(key=lambda orbit: orbit.semi_major_axis)
        orbits = self.raw_orbits
        delete = []
        lenght = len(self.raw_orbits)
        for i in range(len(self.raw_orbits)):
            if i + 1 < lenght:
                if orbits[i].semi_major_axis.m + 0.15 > orbits[i + 1].semi_major_axis.m:
                    delete.append(orbits[i])
        j = 0
        for i, flagged in enumerate(delete, start=1):
            if flagged in self.raw_orbits and i % 2 == 0:
                j += 1
                self.raw_orbits.remove(flagged)

        return j

    def add_orbits(self):
        # our largest gas giant will form close to, but not ON the frost line
        # 1 to 1.2 away from the frost line is perfect
        initial_orbit = RawOrbit(roll(self.star.frost_line.m + 1.0, self.star.frost_line.m + 1.2), 'au')
        self.raw_orbits.append(initial_orbit)

        # starting at our gas giant we simply multiply it's distance from the star,
        next_orbit = initial_orbit
        # by a number anywhere from 1.4 and 2
        factor = roll(1.4, 2.0)

        # repeat this process until you reach the system outer boundry, then stop.
        while next_orbit * factor < self.star.outer_boundry.m:
            next_orbit = RawOrbit(next_orbit * factor, 'au')
            self.raw_orbits.append(next_orbit)
            # and hey presto, we have the next stable orbit away from our star
            factor = roll(1.4, 2.0)

        # next step is to start again at our gas giant
        next_orbit = initial_orbit
        factor = roll(1.4, 2.0)
        # repeat this process until you reach the system inner boundry, then stop.
        while next_orbit / factor > self.star.inner_boundry.m:
            # but this time simply work inward, and istead of multiplying, simply divide
            next_orbit = RawOrbit(next_orbit / factor, 'au')
            self.raw_orbits.append(next_orbit)
            factor = roll(1.4, 2.0)

        f = 1
        while f:
            f = self.check_orbits()

        for orbit in self.raw_orbits:
            self._axes.append(orbit.semi_major_axis.m)
        self._axes.sort()

    def __repr__(self):
        return 'Planetary System of ' + self.star.name

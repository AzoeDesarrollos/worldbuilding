from engine.backend.randomness import roll, choice
from .orbit import RawOrbit, Orbit
from engine import q


class OrbitException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message


class PlanetarySystem:
    raw_orbits = None
    stable_orbits = None
    planets = None

    def __init__(self, star):
        self.star = star
        self.raw_orbits = []
        self.stable_orbits = []
        self.planets = []

        self.current = None

        body_mass = q(star.mass.m * 1.4672, 'jupiter_mass')
        self.gigant_mass = q(body_mass.m * 0.998, 'jupiter_mass')
        self.terra_mass = q(body_mass.m * 6.356, 'earth_mass')

    def add_planet(self, planet):
        if planet not in self.planets:
            if planet.unit == 'earth':
                self.terra_mass -= planet.mass
            elif planet.unit == 'jupiter':
                self.gigant_mass -= planet.mass
            self.set_current(planet)
            self.planets.append(planet)

    def set_current(self, planet):
        self.current = planet

    def remove_planet(self, planet):
        pass

    def put_in_star_orbit(self, planet, last_planet=False):
        """Se puede correr éste metodo primero, añadiendo planetas en orbitas aleatorias o se puede correr add_orbits()
        primero, y colocar los planetas en las órbitas precalculadas.
        """

        self.add_planet(planet)
        avg_e = round(0.584 * (len(self.planets) ** (-1.2)), 3)
        avg_i = 2  # éste valor es arbitrario y es igual al de nuestro sistema solar.

        a, e, i = 0, 0, 0
        try:
            if planet.clase == 'Terrestial Planet':
                if planet.habitable:
                    a = round([o for o in self.raw_orbits if o.temperature == 'habitable'][0].a.m, 3)
                    e = round(roll(avg_e-0.2, avg_e+0.2), 3)
                    i = 0
                else:
                    other = [o for o in self.raw_orbits if o.temperature == 'hot' and o not in self.stable_orbits]
                    a = round(choice(other).a.m, 3)
                    e = roll(avg_e-0.2, avg_e+0.2)
                    i = roll(0.0, 180.0)
                self.stable_orbits.append(Orbit(a, e, i))

            elif planet.clase == 'Gas Giant':
                # if this is the largest, it should occupy the fist orbit away from the frostline
                it_is_the_largest = True
                for p in [j for j in self.planets if j.clase == 'Gas Giant']:
                    if p != planet and planet.mass < p.mass:
                        it_is_the_largest = False

                if it_is_the_largest:
                    a = round(min([o for o in self.raw_orbits if o.temperature == 'cold']).a.m, 3)
                else:
                    other = [o for o in self.raw_orbits if o.temperature == 'cold' and o not in self.stable_orbits]
                    if len(other):
                        a = round(min([o for o in other]).a.m, 3)
                    else:
                        raise OrbitException('There are no more cold orbits to occupy')
                e = roll(avg_e-0.2, avg_e+0.2)
                i = roll(0.0, 90.0)
                self.stable_orbits.append(Orbit(a, e, i))

            elif planet.clase == 'Super Jupiter':
                a = roll(0.04, self.star.frost_line + 1.2)  # migration
                e = roll(0.001, 0.09)
                i = roll(0.0, 90.0)

            elif planet.clase == 'Gas Dwarf':
                other = [o for o in self.raw_orbits if o.temperature == 'cold' and o not in self.stable_orbits]
                if len(other):
                    # for extra added realism, the orbit should be very distant.
                    a = round(max([o for o in other]).a.m, 3)
                else:
                    raise OrbitException('There are no more cold orbits to occupy')
                i = roll(0.0, 90.0)
                e = roll(0.001, 0.09)

            elif planet.clase == 'Eccentric Jupiter':
                other = [o for o in self.raw_orbits if o.temperature != 'habitable' and o not in self.stable_orbits]
                a = round(choice(other).a.m, 3)
                e = roll(avg_e-0.2, avg_e+0.2) if any([p.habitable for p in self.planets]) else roll(0.1, 0.9)
                i = roll(0.0, 90.0)

            elif planet.clase == 'Dwarf Planet':
                # no data. only resonant orbits
                pass

            elif planet.clase in ('Hot Jupiter', 'Puffy Giant'):
                other = [o for o in self.raw_orbits if o.temperature == 'hot' and o not in self.stable_orbits]
                a = round(min([o for o in other]).a.m, 3)
                if not 0.001 <= a <= 0.09:
                    raise OrbitException('The orbit @'+str(a)+' is beyond the limits for a '+planet.clase)
                e = roll(0.001, 0.09)  # migration
                i = roll(10, 170)

        except OrbitException as error:
            print(error)

        if last_planet:
            while round((sum([o.e for o in self.stable_orbits]) / len(self.stable_orbits)).m, 3) > avg_e:
                for orbit in self.stable_orbits:
                    if orbit.eccentricity.m > avg_e:
                        orbit.eccentricity -= 0.01
                    else:
                        orbit.eccentricity += 0.01

            while (sum([o.i for o in self.stable_orbits]) / len(self.stable_orbits)).m > avg_i:
                for orbit in self.stable_orbits:
                    if orbit.inclination.m > avg_i:
                        orbit.inclination -= 0.01
                    else:
                        orbit.inclination += 0.01

        print(a, round(e, 3), round(i, 3))

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
            if orbit.a.m > self.star.frost_line.m:
                orbit.set_temperature('cold')
            elif self.star.habitable_inner.m < orbit.a.m < self.star.habitable_outer.m:
                orbit.set_temperature('habitable')
            else:
                orbit.set_temperature('hot')

    def __repr__(self):
        return 'Planetary System of ' + self.star.name

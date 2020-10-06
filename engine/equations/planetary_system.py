from engine.backend.util import abrir_json, guardar_json
from engine.backend.eventhandler import EventHandler
# from engine.backend.randomness import roll
# from .orbit import Orbit
from engine import q
from os.path import join
from os import getcwd


class OrbitException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message


class PlanetarySystem:
    raw_orbits = None
    stable_orbits = None
    planets = None
    star = None
    planet_counter = 0

    def __init__(self):
        self.raw_orbits = []
        self.stable_orbits = []
        self.planets = []

        self.current = None
        self.body_mass = 0
        self.save_data = {}

        EventHandler.register(self.save, "SaveDataFile")
        EventHandler.register(self.compound_save_data, "SaveData")

    def set_star(self, star):
        self.star = star
        self.body_mass = q(star.mass.m * 1.4672, 'jupiter_mass')

    def get_available_mass(self):
        return self.body_mass

    def add_planet(self, planet):
        if planet not in self.planets:
            minus_mass = planet.mass
            if planet.unit == 'earth':
                minus_mass = planet.mass.to('jupiter_mass')

            self.body_mass -= minus_mass
            self.set_current(planet)
            self.planets.append(planet)
            if not planet.has_name:
                planet.name = planet.clase+' #'+str(self.planets.index(planet))
            return True
        else:
            return False

    def get_planet_by_name(self, planet_name):
        planet = [planet for planet in self.planets if planet.name == planet_name][0]
        return planet

    def set_current(self, planet):
        if planet.orbit is None:
            self.current = planet

    def remove_planet(self, planet):
        pass

    # def put_in_star_orbit(self, planet, orbit, last_planet=False): """Se puede correr éste metodo primero,
    # añadiendo planetas en orbitas aleatorias o se puede correr add_orbits() primero, y colocar los planetas en las
    # órbitas precalculadas. """
    #
    #     self.add_planet(planet)
    #     avg_e = round(0.584 * (len(self.planets) ** (-1.2)), 3)
    #     avg_i = 2  # éste valor es arbitrario y es igual al de nuestro sistema solar.
    #
    #     a, e, i = 0, 0, 0
    #     try:
    #         if planet.clase == 'Terrestial Planet':
    #             if planet.habitable:
    #                 e = round(roll(avg_e-0.2, avg_e+0.2), 3)
    #                 i = 0
    #             else:
    #                 e = roll(avg_e-0.2, avg_e+0.2)
    #                 i = roll(0.0, 180.0)
    #
    #         elif planet.clase == 'Gas Giant':
    #             # if this is the largest, it should occupy the fist orbit away from the frostline
    #             it_is_the_largest = True
    #             for p in [j for j in self.planets if j.clase == 'Gas Giant']:
    #                 if p != planet and planet.mass < p.mass:
    #                     it_is_the_largest = False
    #
    # if it_is_the_largest and orbit is None: a = round(min([o for o in self.raw_orbits if o.temperature ==
    # 'cold']).a.m, 3) else: if orbit is None: other = [o for o in self.raw_orbits if o.temperature == 'cold' and o
    # not in self.stable_orbits] if len(other): a = round(min([o for o in other]).a.m, 3) else: raise OrbitException(
    # 'There are no more cold orbits to occupy') e = roll(avg_e-0.2, avg_e+0.2) i = roll(0.0, 90.0)
    #
    #         elif planet.clase == 'Super Jupiter':
    #             e = roll(0.001, 0.09)
    #             i = roll(0.0, 90.0)
    #
    #         elif planet.clase == 'Gas Dwarf':
    #             if orbit is None:
    #                 other = [o for o in self.raw_orbits if o.temperature == 'cold' and o not in self.stable_orbits]
    #                 if len(other):
    #                     # for extra added realism, the orbit should be very distant.
    #                     a = round(max([o for o in other]).a.m, 3)
    #                 else:
    #                     raise OrbitException('There are no more cold orbits to occupy')
    #             i = roll(0.0, 90.0)
    #             e = roll(0.001, 0.09)
    #
    #         elif planet.clase == 'Eccentric Jupiter':
    #             e = roll(avg_e-0.2, avg_e+0.2) if any([p.habitable for p in self.planets]) else roll(0.1, 0.9)
    #             i = roll(0.0, 90.0)
    #
    #         elif planet.clase == 'Dwarf Planet':
    #             # no data. only resonant orbits
    #             pass
    #
    #         elif planet.clase in ('Hot Jupiter', 'Puffy Giant'):
    #             if orbit is None:
    #                 other = [o for o in self.raw_orbits if o.temperature == 'hot' and o not in self.stable_orbits]
    #                 a = round(min([o for o in other]).a.m, 3)
    #                 if not 0.001 <= a <= 0.09:
    #                     raise OrbitException('The orbit @'+str(a)+' is beyond the limits for a '+planet.clase)
    #             e = roll(0.001, 0.09)  # migration
    #             i = roll(10, 170)
    #
    #     except OrbitException as error:
    #         print(error)
    #
    #     if last_planet:
    #         while round((sum([o.e for o in self.stable_orbits]) / len(self.stable_orbits)).m, 3) > avg_e:
    #             for orbit in self.stable_orbits:
    #                 if orbit.eccentricity.m > avg_e:
    #                     orbit.eccentricity -= 0.01
    #                 else:
    #                     orbit.eccentricity += 0.01
    #
    #         while (sum([o.i for o in self.stable_orbits]) / len(self.stable_orbits)).m > avg_i:
    #             for orbit in self.stable_orbits:
    #                 if orbit.inclination.m > avg_i:
    #                     orbit.inclination -= 0.01
    #                 else:
    #                     orbit.inclination += 0.01

        # orb = Orbit(a, e, i)
        # self.stable_orbits.append(orb)
        # planet.set_orbit(self.star, orb)
        # orb.set_planet(planet)
        # return orb

    @staticmethod
    def save(event):
        ruta = join(getcwd(), 'data', 'savedata.json')
        data = abrir_json(ruta)
        data.update(event.data)
        guardar_json(ruta, data)

    def compound_save_data(self, event):
        for key in event.data:
            if key in self.save_data:
                self.save_data[key].update(event.data[key])
            else:
                self.save_data.update(event.data)
        if not EventHandler.is_quequed('SaveDataFile'):
            EventHandler.trigger('SaveDataFile', 'EngineData', self.save_data)

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
        f = 1
        while f:
            f = self.check_orbits()

        # for orbit in self.raw_orbits:
        #     if orbit.a.m > self.star.frost_line.m:
        #         orbit.set_temperature('cold')
        #     elif self.star.habitable_inner.m < orbit.a.m < self.star.habitable_outer.m:
        #         orbit.set_temperature('habitable')
        #     else:
        #         orbit.set_temperature('hot')

    def __repr__(self):
        return 'Planetary System of ' + self.star.name


system = PlanetarySystem()

__all__ = [
    'system'
]

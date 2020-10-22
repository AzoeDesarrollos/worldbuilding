from engine.backend.util import abrir_json, guardar_json
from engine.backend.eventhandler import EventHandler
from engine import q
from os.path import join
from os import getcwd


class PlanetarySystem:
    planets = None
    star = None
    stars = None

    def __init__(self):
        self.planets = []
        self.stars = []

        self.planet = None
        self.body_mass = q(0, 'jupiter_mass')
        self.save_data = {}

        EventHandler.register(self.save, "SaveDataFile")
        EventHandler.register(self.compound_save_data, "SaveData")

    def set_star(self, star):
        self.stars.append(star)
        self.body_mass += q(star.mass.m * 1.4672, 'jupiter_mass')

    def get_available_mass(self):
        return self.body_mass

    def add_planet(self, planet):
        if planet not in self.planets:
            minus_mass = planet.mass
            if planet.unit == 'earth':
                minus_mass = planet.mass.to('jupiter_mass')

            self.body_mass -= minus_mass
            self.set_current_planet(planet)
            self.planets.append(planet)
            if not planet.has_name:
                planet.name = planet.clase+' #'+str(self.planets.index(planet))
            return True
        else:
            return False

    def get_planet_by_name(self, planet_name):
        planet = [planet for planet in self.planets if planet.name == planet_name][0]
        return planet

    def set_current_planet(self, planet):
        if planet.orbit is None:
            self.planet = planet

    def remove_planet(self, planet):
        pass

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

    def __repr__(self):
        return 'Planetary System of ' + self.star.name


system = PlanetarySystem()

__all__ = [
    'system'
]

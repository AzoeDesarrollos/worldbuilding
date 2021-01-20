from engine.backend.util import abrir_json, guardar_json
from engine.backend.eventhandler import EventHandler
from os.path import join
from os import getcwd
from engine import q
from math import exp


class PlanetarySystem:
    planets = None
    satellites = None
    asteroids = None
    stars = None
    id = None

    def __init__(self, star_system):
        self.planets = []
        self.satellites = []
        self.asteroids = []
        self.star_system = star_system
        self.id = star_system.id
        self.body_mass = q(16 * exp(-0.6931 * star_system.mass.m) * 0.183391347289428, 'jupiter_mass')

    def get_available_mass(self):
        return self.body_mass

    def add_astro_obj(self, astro_obj):
        group = None
        if astro_obj.celestial_type == 'planet':
            group = self.planets
        elif astro_obj.celestial_type == 'satellite':
            group = self.satellites
        elif astro_obj.celestial_type == 'asteroid':
            group = self.asteroids

        if astro_obj not in group:
            minus_mass = astro_obj.mass.to('jupiter_mass')

            if minus_mass > self.body_mass:
                # prevents negative mass
                return False

            self.body_mass -= minus_mass
            group.append(astro_obj)
            if not astro_obj.has_name:
                astro_obj.name = astro_obj.clase + ' #' + str(group.index(astro_obj))
            return True

        return False

    def get_planet_by_name(self, planet_name):
        planet = [planet for planet in self.planets if planet.name == planet_name][0]
        return planet

    def is_planet_habitable(self, planet) -> bool:
        pln_orbit = planet.orbit.semi_major_axis
        star = self.star_system
        return star.habitable_inner.m <= pln_orbit.m <= star.habitable_outer.m

    def __eq__(self, other):
        return self.star_system == other.star_system

    def __repr__(self):
        return 'System of '+str(self.star_system)

    def __getitem__(self, item):
        if self.star_system.celestial_type == 'star':  # single-star system
            if item == 0:
                return self.star_system
            raise StopIteration()

        elif self.star_system.celestial_type == 'system':  # binary systems
            if item == 0:
                return self.star_system.primary
            elif item == 1:
                return self.star_system.secondary
            raise StopIteration()


class Systems:
    _systems = None
    loose_stars = None
    _flagged = []
    save_data = {}
    _current_idx = None

    @classmethod
    def init(cls):
        cls._systems = []
        cls.loose_stars = []
        cls._current_idx = 0

        EventHandler.register(cls.save, "SaveDataFile")
        EventHandler.register(cls.compound_save_data, "SaveData")

    @classmethod
    def set_system(cls, star):
        if star in cls.loose_stars:
            cls.loose_stars.remove(star)
        elif star.celestial_type != 'system':
            return
        if star.letter == 'S':
            for sub in star:
                cls.set_system(sub)
        else:
            system = PlanetarySystem(star)
            if system not in cls._systems:
                cls._systems.append(system)
            if star.letter is not None:
                for s in star:
                    if s in cls.loose_stars:
                        cls.loose_stars.remove(s)
                    else:
                        system = cls.get_system_by_star(s)
                        cls._systems.remove(system)

    @classmethod
    def get_system_by_id(cls, number):
        systems = [s for s in cls._systems if s.id == number]
        if len(systems) == 1:
            return systems[0]

    @classmethod
    def load_system(cls, star):
        cls.loose_stars.append(star)
        cls.set_system(star)

    @classmethod
    def swap_system(cls, idx):
        if 0 <= idx <= len(cls._systems):
            cls._current_idx = idx
            return cls._systems[idx]

    @classmethod
    def get_system_by_star(cls, star):
        for system in cls._systems:
            if system.star_system == star:
                return system

    @classmethod
    def cycle_systems(cls):
        idx = cls._current_idx + 1
        if 0 <= idx < len(cls._systems):
            cls._current_idx = idx
        else:
            cls._current_idx = 0

    @classmethod
    def get_current(cls):
        if len(cls._systems):
            return cls._systems[cls._current_idx]
        return 'None'

    @classmethod
    def get_current_star(cls):
        if len(cls._systems):
            return cls._systems[cls._current_idx].star_system
        return 'None'

    @classmethod
    def get_systems(cls):
        return cls._systems

    @classmethod
    def get_star_systems(cls):
        return [s.star_system for s in cls._systems]

    @classmethod
    def get_star_idx(cls, star):
        for system in cls._systems:
            if star == system.star_system:
                return cls._systems.index(system)

    @classmethod
    def get_current_idx(cls):
        return cls._current_idx

    @classmethod
    def add_star(cls, star):
        cls.loose_stars.append(star)

    @classmethod
    def del_star(cls, star):
        if star in cls.loose_stars:
            cls._flagged.append(cls.loose_stars.index(star))

    @classmethod
    def get_flagged(cls):
        return [star for star in cls.loose_stars if cls.loose_stars.index(star) in cls._flagged]

    @classmethod
    def get_stars(cls):
        return [i for i in cls.loose_stars if i not in cls._flagged]

    @staticmethod
    def save(event):
        ruta = join(getcwd(), 'data', 'savedata.json')
        data = abrir_json(ruta)
        data.update(event.data)
        guardar_json(ruta, data)

    @classmethod
    def compound_save_data(cls, event):
        for key in event.data:
            if key in cls.save_data:
                cls.save_data[key].update(event.data[key])
            else:
                cls.save_data.update(event.data)
        if not EventHandler.is_quequed('SaveDataFile'):
            EventHandler.trigger('SaveDataFile', 'EngineData', cls.save_data)

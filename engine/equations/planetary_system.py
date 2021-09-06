from engine.backend.util import abrir_json, guardar_json
from engine.backend.eventhandler import EventHandler
from math import exp, pow
from os.path import join
from os import getcwd
from engine import q


class PlanetarySystem:
    planets = None
    satellites = None
    asteroids = None
    stars = None
    id = None

    aparent_brightness = None
    average_visibility = None

    def __init__(self, star_system):
        self.planets = []
        self.satellites = []
        self.asteroids = []
        self.astro_bodies = []
        self.star_system = star_system
        self.id = star_system.id
        self.body_mass = q(16 * exp(-0.6931 * star_system.mass.m) * 0.183391347289428, 'jupiter_mass')

        self.aparent_brightness = {}

    def update(self):
        self.body_mass = q(16 * exp(-0.6931 * self.star_system.mass.m) * 0.183391347289428, 'jupiter_mass')

    def get_available_mass(self):
        return self.body_mass

    def visibility_of_stars(self, body):
        if body.id not in self.aparent_brightness:
            self.aparent_brightness[body.id] = {}

        for star in self.star_system:
            if body.orbit is not None and star.id not in self.aparent_brightness[body.id]:
                ab = star.luminosity.m / pow(body.orbit.a.m, 2)
                self.aparent_brightness[body.id][star.id] = ab

    def visibility_by_albedo(self):
        luminosity = self.star_system.luminosity.to('watt').m
        to_see = self.planets + self.satellites + self.asteroids
        for i, body in enumerate(to_see):
            if body.id not in self.aparent_brightness:
                self.aparent_brightness[body.id] = {}

            others = to_see[:i] + to_see[i + 1:]
            if body.orbit is not None:
                x = body.orbit.a.to('m').m  # position of the Observer's planet
                for other in [o for o in others if o.orbit is not None]:
                    y = other.orbit.a.to('m').m  # position of the observed body

                    distance = y - x if y >= x else x - y  # linear distance, much quicker
                    albedo = other.albedo.m / 100
                    radius = other.radius.to('m').m
                    semi_major_axis = other.orbit.semi_major_axis.to('m').m

                    ab = (albedo * luminosity * pow(radius, 2)) / (pow(semi_major_axis, 2) * pow(distance, 2))
                    if ab > 1.3e-7:
                        visibility = 'naked'
                    elif ab < 1.2e-9:
                        visibility = 'telescope'
                    else:
                        visibility = 'undetermined'
                    self.aparent_brightness[body.id][other.id] = visibility

    @property
    def star(self):
        return self.star_system

    def add_astro_obj(self, astro_obj):
        group = self._get_astro_group(astro_obj)

        if astro_obj not in group:
            minus_mass = astro_obj.mass.to('jupiter_mass')

            text = 'There is not enough mass in the system to create new bodies of this type.'
            assert minus_mass <= self.body_mass, text
            self.body_mass -= minus_mass
            group.append(astro_obj)
            self.astro_bodies.append(astro_obj)
            return True

        return False

    def remove_astro_obj(self, astro_obj):
        group = self._get_astro_group(astro_obj)
        plus_mass = group[group.index(astro_obj)].mass.to('jupiter_mass')
        self.body_mass += plus_mass
        group.remove(astro_obj)
        Systems.flag(astro_obj.id)
        return True

    def _get_astro_group(self, astro_obj):
        group = None
        if astro_obj.celestial_type == 'planet':
            group = self.planets
        elif astro_obj.celestial_type == 'satellite':
            group = self.satellites
        elif astro_obj.celestial_type == 'asteroid':
            group = self.asteroids

        return group

    def get_astrobody_by(self, tag_identifier, tag_type='name'):
        astrobody = None
        if tag_type == 'name':
            astrobody = [body for body in self.astro_bodies if body.name == tag_identifier][0]
        elif tag_type == 'id':
            astrobody = [body for body in self.astro_bodies if body.id == tag_identifier][0]

        return astrobody

    def is_habitable(self, planet) -> bool:
        pln_orbit = planet.orbit.semi_major_axis
        star = self.star_system
        return star.habitable_inner.m <= pln_orbit.m <= star.habitable_outer.m

    @property
    def habitable(self):
        # the system is considered habitable only if it hosts a habitable planet.
        for planet in self.planets:
            if planet.habitable and self.is_habitable(planet):
                return True
        return False

    def get_unnamed(self):
        unnamed = []
        if not self.star_system.has_name:
            unnamed.append(self.star_system)
        if self.star_system.letter is not None:
            for star in self.star_system:
                if not star.has_name:
                    unnamed.append(star)
        for body in self.astro_bodies:
            if not body.has_name:
                unnamed.append(body)

        return unnamed

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return 'System of ' + str(self.star_system)

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
        EventHandler.register(cls.load_data, 'LoadData')

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
                        if system is not None:
                            cls._systems.remove(system)

    @classmethod
    def unset_system(cls, star):
        system = cls.get_system_by_star(star)
        if star.letter is not None:
            if star.letter == system.star_system.primary:
                cls.loose_stars.append(system.star_system.secondary)
            elif star == system.star_system.secondary:
                cls.loose_stars.append(system.star_system.primary)
        else:
            cls.loose_stars.append(star)
        cls._systems.remove(system)

    @classmethod
    def dissolve_system(cls, system):
        if system.letter is None:
            cls.loose_stars.append(system)
            system = cls.get_system_by_star(system)
        else:
            for star in system:
                cls.loose_stars.append(star)

        if system in cls._systems:
            cls._systems.remove(system)
            cls._flagged.append(system.id)
            cls.cycle_systems()

    @classmethod
    def get_system_by_id(cls, id_number):
        systems = [s for s in cls._systems if s.id == id_number]
        if len(systems) == 1:
            return systems[0]
        else:
            raise AssertionError('System ID is invalid')

    @classmethod
    def get_star_by_id(cls, id_number):
        for star in cls.loose_stars:
            if star.id == id_number:
                return star
        for system in cls._systems:
            if id_number == system.id:
                return system
            else:
                for star in system:
                    if star.id == id_number:
                        return star

    @classmethod
    def get_system_by_star(cls, star):
        for system in cls._systems:
            if hasattr(system, 'letter'):
                if any([body == star for body in system.star_system.composition()]):
                    return system
            elif system.star_system == star:
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

    @classmethod
    def get_current_star(cls):
        if len(cls._systems):
            return cls._systems[cls._current_idx].star_system

    @classmethod
    def get_systems(cls):
        return cls._systems

    @classmethod
    def get_star_idx(cls, star):
        for system in cls._systems:
            if star == system.star_system:
                return cls._systems.index(system)

    @classmethod
    def get_current_idx(cls):
        return cls._current_idx

    @classmethod
    def get_system_idx_by_id(cls, id_number):
        star = cls.get_star_by_id(id_number)
        return cls.get_star_idx(star)

    @classmethod
    def add_star(cls, star):
        cls.loose_stars.append(star)

    @classmethod
    def remove_star(cls, star):
        cls._flagged.append(star.id)
        if star in cls.loose_stars:
            cls.loose_stars.remove(star)
        else:
            system = cls.get_system_by_star(star)
            if system is not None:
                cls.unset_system(system)

    @classmethod
    def flag(cls, id):
        cls._flagged.append(id)

    @classmethod
    def save(cls, event):
        ruta = join(getcwd(), 'data', 'savedata.json')
        data = abrir_json(ruta)
        read_data = abrir_json(ruta)
        keys = 'Asteroids', 'Planets', 'Satellites', 'Stars', 'Binary Systems', 'Planetary Orbits', 'Stellar Orbits'
        for key in keys:
            new_data = event.data.get(key, [])
            for item_id in new_data:
                item_data = new_data[item_id]
                if item_id in read_data[key]:
                    data[key][item_id].update(item_data)
                else:
                    data[key][item_id] = item_data

        for id in cls._flagged:
            for key in data:
                for item in data[key]:
                    if 'id' in item and item['id'] == id:
                        data[key].remove(item)

        guardar_json(ruta, data)

    @classmethod
    def compound_save_data(cls, event):
        cls.save_data.update(event.data)
        if not EventHandler.is_quequed('SaveDataFile'):
            EventHandler.trigger('SaveDataFile', 'EngineData', cls.save_data)

    @classmethod
    def load_data(cls, event):
        cls.save_data.update(event.data)

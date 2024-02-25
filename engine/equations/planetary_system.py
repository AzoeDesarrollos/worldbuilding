from engine.backend import EventHandler, Systems, q
from .general import Flagable
from .space import Universe
from math import exp


class PlanetarySystem(Flagable):
    planets = None
    satellites = None
    asteroids = None
    stars = None
    binary_planets = None
    id = None

    aparent_brightness = None

    age = 0
    body_mass = 0

    has_name = False

    is_a_system = True

    def __init__(self, star_system):
        self.planets = []
        self.satellites = []
        self.asteroids = []
        self.astro_bodies = []
        self.binary_planets = []
        self.star_system = star_system
        self.id = star_system.id
        if Systems.restricted_mode:
            self.set_available_mass()
        self.aparent_brightness = {}
        self.relative_sizes = {}
        self.distances = {}
        if star_system.letter != 'S':
            self.age = star_system.age

    def update(self):
        if Systems.restricted_mode:
            self.set_available_mass()

    def get_available_mass(self):
        if Systems.restricted_mode:
            return self.body_mass
        else:
            return 'Unlimited'

    def set_available_mass(self):
        if self.star_system.parent is not None:
            mass = self.star_system.parent.shared_mass
        elif self.star_system.shared_mass is not None:
            mass = self.star_system.shared_mass
        else:
            mass = self.star_system.mass

        self.body_mass = q(16 * exp(-0.6931 * mass.m) * 0.183391347289428, 'jupiter_mass')

    @property
    def star(self):
        return self.star_system

    @property
    def mass(self):
        return self.star_system.mass

    def astro_group(self, astro_obj):
        return self._get_astro_group(astro_obj)

    def add_astro_obj(self, astro_obj):
        Universe.add_astro_obj(astro_obj)
        group = self._get_astro_group(astro_obj)

        if astro_obj not in group:
            if Systems.restricted_mode and astro_obj.celestial_type != 'system':
                minus_mass = astro_obj.mass.to('jupiter_mass')
                text = 'There is not enough mass in the system to create new bodies of this type.'
                assert minus_mass <= self.body_mass, text
                self.body_mass -= minus_mass
            group.append(astro_obj)
            if astro_obj.celestial_type != 'system':
                self.astro_bodies.append(astro_obj)
            if astro_obj.celestial_type == 'planet' and astro_obj.planet_type == 'rocky':
                EventHandler.trigger('RockyPlanet', self, {'system_id': self.id,
                                                           'planet': astro_obj,
                                                           'operation': 'add'})
            return True

        return False

    def remove_astro_obj(self, astro_obj):
        Universe.remove_astro_obj(astro_obj)
        group = self._get_astro_group(astro_obj)
        if Systems.restricted_mode and astro_obj.celestial_type != 'system':
            plus_mass = astro_obj.mass.to('jupiter_mass')
            self.body_mass += plus_mass
        group.remove(astro_obj)
        astro_obj.flag()
        if astro_obj.celestial_type != 'system':
            self.astro_bodies.remove(astro_obj)
        if astro_obj.celestial_type == 'planet' and astro_obj.planet_type == 'rocky':
            EventHandler.trigger('RockyPlanet', self, {'system_id': self.id,
                                                       'planet': astro_obj,
                                                       'operation': 'remove'})
        return True

    def _get_astro_group(self, astro_obj):
        group = None
        if astro_obj.celestial_type == 'planet':
            group = self.planets
        elif astro_obj.celestial_type == 'satellite':
            group = self.satellites
        elif astro_obj.celestial_type == 'asteroid':
            group = self.asteroids
        elif astro_obj.celestial_type == 'system':
            group = self.binary_planets

        return group

    def get_astrobody_by(self, tag_identifier, tag_type='name', silenty=False):
        astrobody = None
        if tag_type == 'name':
            astrobody = [body for body in self.astro_bodies if body.name == tag_identifier]
        elif tag_type == 'id':
            astrobody = [body for body in self.astro_bodies if body.id == tag_identifier]

        if not len(astrobody):
            if self.star_system.letter == 'P':
                if self.star_system.id == tag_identifier:
                    astrobody = [self.star_system]
                else:
                    astrobody = [star for star in self.star_system.composition() if star.id == tag_identifier]
            else:  # tag_identifier could be a star's id
                astrobody = [star for star in self.star_system if star.id == tag_identifier]

        if not len(astrobody) and self.star_system.parent is not None:  # tag_identifier could be a star's parent id
            if self.star_system.parent.id == tag_identifier:
                astrobody = [self.star_system]

        if not silenty:
            assert len(astrobody), 'the ID "{}" is invalid'.format(tag_identifier)
            return astrobody[0]
        else:
            if not len(astrobody):
                return False
            else:
                return astrobody[0]

    def get_bodies_in_orbit_by_types(self, *types):
        bodies = []
        for tipo in types:
            for body in self.astro_bodies:
                if body.clase == tipo and body.orbit is not None:
                    bodies.append(body)
        return bodies

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
        if self.star_system.parent is not None:
            if not self.star_system.parent.has_name:
                unnamed.append(self.star_system.parent)
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
        if hasattr(other, 'id'):
            return self.id == other.id
        return False

    def __repr__(self):
        return 'System of ' + str(self.star_system)

    def __getitem__(self, item):
        if self.star_system.celestial_type != 'system':  # single-star system
            if item == 0:
                return self.star_system
            raise StopIteration()

        elif self.star_system.celestial_type == 'system':  # binary systems
            if item == 0:
                return self.star_system.primary
            elif item == 1:
                return self.star_system.secondary
            raise StopIteration()


class RoguePlanets:
    planets = []
    satellites = []
    asteroids = []
    astro_bodies = []
    binary_planets = []

    has_name = True
    name = 'Rogue Planets'

    id = 'rogues'

    is_a_system = False

    letter = None

    @classmethod
    def init(cls):
        cls.star_system = cls

    @classmethod
    def get_available_mass(cls):
        return 'Unlimited'

    @classmethod
    def add_astro_obj(cls, astro_obj):
        Universe.add_astro_obj(astro_obj)
        group = cls._get_astro_group(astro_obj)

        if astro_obj not in group:
            group.append(astro_obj)
            astro_obj.set_rogue()
            if astro_obj.celestial_type != 'system':
                cls.astro_bodies.append(astro_obj)
            else:
                astro_obj.temperature = q(2.7, 'kelvin')
            # Universe.visibility_by_albedo()
            if astro_obj.celestial_type == 'planet' and astro_obj.planet_type == 'rocky':
                EventHandler.trigger('RockyPlanet', 'RoguePlanets', {'system_id': cls.id,
                                                                     'planet': astro_obj,
                                                                     'operation': 'add'})
            return True

        return False

    @classmethod
    def remove_astro_obj(cls, astro_obj):
        Universe.remove_astro_obj(astro_obj)
        group = cls._get_astro_group(astro_obj)
        group.remove(astro_obj)
        astro_obj.flag()
        cls.astro_bodies.remove(astro_obj)
        if astro_obj.celestial_type == 'planet' and astro_obj.planet_type == 'rocky':
            EventHandler.trigger('RockyPlanet', 'RoguePlanets', {'system_id': cls.id,
                                                                 'planet': astro_obj,
                                                                 'operation': 'remove'})
        return True

    @classmethod
    def _get_astro_group(cls, astro_obj):
        group = None
        if astro_obj.celestial_type == 'planet':
            group = cls.planets
        elif astro_obj.celestial_type == 'satellite':
            group = cls.satellites
        elif astro_obj.celestial_type == 'asteroid':
            group = cls.asteroids

        return group

    @classmethod
    def get_astrobody_by(cls, tag_identifier, tag_type='name', silenty=False):
        astrobody = None
        if tag_type == 'name':
            astrobody = [body for body in cls.astro_bodies if body.name == tag_identifier]
        elif tag_type == 'id':
            astrobody = [body for body in cls.astro_bodies if body.id == tag_identifier]

        if not (len(astrobody)):
            astrobody = [body for body in Universe.astro_bodies if body.id == tag_identifier]
            if len(astrobody):
                if astrobody[0] in Universe.stars or astrobody[0].rogue is False:
                    return False

        if not silenty:
            assert len(astrobody), 'the ID "{}" is invalid'.format(tag_identifier)
            return astrobody[0]
        else:
            if not len(astrobody):
                return False
            else:
                return astrobody[0]

    @classmethod
    def get_unnamed(cls):
        unnamed = [body for body in cls.astro_bodies if not body.has_name]
        return unnamed

    @classmethod
    def astro_group(cls, astro_obj):
        return cls._get_astro_group(astro_obj)

    @classmethod
    def update(cls):
        pass

    @classmethod
    def __repr__(cls):
        return cls.name

    @classmethod
    def __str__(cls):
        return 'None'


RoguePlanets.init()
Systems.import_clases(rogues=RoguePlanets, planetary=PlanetarySystem)

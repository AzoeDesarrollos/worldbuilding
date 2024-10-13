from engine.backend import EventHandler, q
from .space import Universe
from math import exp


class PlanetarySystem:
    planets = None
    satellites = None
    asteroids = None
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

        self.terrestial_planets = []
        self.gas_giants = []
        self.dwarf_planets = []

        self.parent = star_system
        self.parent.planetary = self
        self.id = star_system.id
        self.set_available_mass()
        self.aparent_brightness = {}
        self.relative_sizes = {}
        self.distances = {}
        if star_system.letter != 'S':
            self.age = star_system.age

        EventHandler.register(self.dissolve_systems, 'DissolveSystem')

    def update(self):
        self.set_available_mass()

    def get_available_mass(self):
        return self.body_mass

    def set_available_mass(self):
        if self.parent.system_number == 'binary':
            mass = self.parent.mass
        elif self.parent.system_number == 'single':
            mass = self.parent.star.mass
        else:  # Triple System single companion
            mass = self.parent.shared_mass

        self.body_mass = q(16 * exp(-0.6931 * mass.m) * 0.183391347289428, 'jupiter_mass')

    def dissolve_systems(self, event):
        for star in event.data['system'].composition():
            if star.parent == self:
                self.parent.star.flag()
                for astro in self.astro_bodies:
                    astro.flag()

    def astro_group(self, astro_obj):
        return self._get_astro_group(astro_obj)

    def add_astro_obj(self, astro_obj):
        Universe.add_astro_obj(astro_obj)
        group = self._get_astro_group(astro_obj)

        if self._adding_a_planet:
            kind = self._get_astro_kind(astro_obj)

            if astro_obj not in kind:
                kind.append(astro_obj)
                astro_obj.idx = len(kind) - 1

        if astro_obj not in group:
            if astro_obj.celestial_type != 'system':
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
        if astro_obj.celestial_type != 'system':
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

    def _get_astro_kind(self, astro_obj):
        self._adding_a_planet = False
        if astro_obj.planet_type == 'gaseous':
            return self.gas_giants
        elif astro_obj.planet_type == 'rocky':
            return self.terrestial_planets
        elif astro_obj.relative_size == "Dwarf":
            return self.dwarf_planets

    def _get_astro_group(self, astro_obj):
        group = None
        if astro_obj.celestial_type == 'planet':
            group = self.planets
            self._adding_a_planet = True
        elif astro_obj.celestial_type == 'satellite':
            group = self.satellites
        elif astro_obj.celestial_type == 'asteroid':
            group = self.asteroids
        elif astro_obj.celestial_type == 'binary planet':
            group = self.binary_planets

        return group

    def get_astrobody_by(self, tag_identifier, tag_type='name', silenty=False):
        astrobody = None
        if tag_type == 'name':
            astrobody = [body for body in self.astro_bodies if body.name == tag_identifier]
        elif tag_type == 'id':
            astrobody = [body for body in self.astro_bodies if body.id == tag_identifier]

        if not len(astrobody):
            if self.parent.letter == 'P':
                if self.parent.id == tag_identifier:
                    astrobody = [self.parent]
                else:
                    astrobody = [star for star in self.parent.composition() if star.id == tag_identifier]
            else:  # tag_identifier could be a star's id
                astrobody = [star for star in self.parent if star.id == tag_identifier]

        if not len(astrobody) and self.parent.parent is not None:  # tag_identifier could be a star's parent id
            if self.parent.parent.id == tag_identifier:
                astrobody = [self.parent]

        if not silenty:
            assert len(astrobody), f'the ID "{tag_identifier}" is invalid'
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
        star = self.parent
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
        # if self.parent

        # if self.star_system.parent is not None:
        #     if not self.star_system.parent.has_name:
        #         unnamed.append(self.star_system.parent)
        # if not self.star_system.has_name:
        #     unnamed.append(self.star_system)
        # if self.star_system.letter is not None:
        #     for star in self.star_system:
        #         if not star.has_name:
        #             unnamed.append(star)
        for body in self.astro_bodies:
            if not body.has_name:
                unnamed.append(body)

        return unnamed

    def __eq__(self, other):
        if hasattr(other, 'id'):
            return self.id == other.id
        return False

    def __repr__(self):
        return 'Planetary System of ' + str(self.parent)

    def __str__(self):
        return str(self.parent)

    def __getitem__(self, item):
        if self.parent.system_number == 'single':  # single-star system
            if item == 0:
                return self.parent
            raise StopIteration()

        elif self.parent.system_number == 'binary':  # binary systems
            if item == 0:
                return self.parent.primary
            elif item == 1:
                return self.parent.secondary
            raise StopIteration()


class Rogues:
    planets = []
    satellites = []
    asteroids = []
    astro_bodies = []
    binary_planets = []

    black_holes = []
    neutron_stars = []
    brown_dwarfs = []
    white_dwarfs = []
    compact_objects = []

    has_name = True
    name = 'Rogue Planets'

    id = 'rogues'

    is_a_system = False

    letter = None

    parent = None

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


Rogues.init()

from engine.backend import small_angle_aproximation, Systems, q, eucledian_distance
from math import sqrt


class Universe:
    planets = None
    satellites = None
    asteroids = None
    stars = None
    galaxies = None
    bubbles = None

    aparent_brightness = None
    relative_sizes = None
    distances = None

    astro_bodies = None

    @classmethod
    def init(cls):
        cls.planets = []
        cls.satellites = []
        cls.asteroids = []
        cls.stars = []
        cls.galaxies = []
        cls.bubbles = []

        cls.aparent_brightness = {}
        cls.relative_sizes = {}
        cls.distances = {}

        cls.astro_bodies = []

    @classmethod
    def get_astrobody_by(cls, tag_identifier, tag_type='name', silenty=False):
        astrobody = None
        if tag_type == 'name':
            astrobody = [body for body in cls.astro_bodies if body.name == tag_identifier]
        elif tag_type == 'id':
            astrobody = [body for body in cls.astro_bodies if body.id == tag_identifier]

        if not silenty:
            assert len(astrobody), 'the ID "{}" is invalid'.format(tag_identifier)
            return astrobody[0]
        else:
            if not len(astrobody):
                return False
            else:
                return astrobody[0]

    @classmethod
    def add_astro_obj(cls, astro_obj):
        group = cls._get_astro_group(astro_obj)
        if astro_obj not in group:
            group.append(astro_obj)
            cls.astro_bodies.append(astro_obj)
        if hasattr(astro_obj, 'clase'):
            astro_obj.idx = len([i for i in group if i.clase == astro_obj.clase]) - 1
        elif hasattr(astro_obj, 'cls'):
            astro_obj.idx = len([i for i in group if i.cls == astro_obj.cls]) - 1

    @classmethod
    def remove_astro_obj(cls, astro_obj):
        group = cls._get_astro_group(astro_obj)
        group.remove(astro_obj)

    @classmethod
    def _get_astro_group(cls, astro_obj):
        group = None
        if astro_obj.celestial_type == 'planet':
            group = cls.planets
        elif astro_obj.celestial_type == 'satellite':
            group = cls.satellites
        elif astro_obj.celestial_type == 'asteroid':
            group = cls.asteroids
        elif astro_obj.celestial_type == 'star':
            group = cls.stars
        elif astro_obj.celestial_type == 'galaxy':
            group = cls.galaxies
        elif astro_obj.celestial_type == 'stellar bubble':
            group = cls.bubbles

        return group

    @classmethod
    def visibility_of_stars(cls, body):
        if body.id not in cls.aparent_brightness:
            cls.aparent_brightness[body.id] = {}
        if body.id not in cls.distances:
            cls.distances[body.id] = {}

        for system in Systems.get_stars_and_systems():
            if system.star_system.letter == 'P':
                stars = [system.star_system]
            else:
                stars = [s for s in system.star_system]

            for star in stars:
                if body.orbit is not None and star.id not in cls.aparent_brightness[body.id]:
                    # this chunk is for binary pairs or single stars
                    if star == body.find_topmost_parent(body):  # primary star
                        ab = round(q(star.luminosity.m / pow(body.orbit.a.m, 2), 'Vs'), 3)
                        cls.distances[body.id][star.id] = body.orbit.a
                    elif star in body.orbit.star:  # primary star's companion (in case of an S-Type System)
                        x1, y1, z1 = body.find_topmost_parent(body).position
                        x1 = body.orbit.a.m  # chapuza
                        x2, y2, z2 = star.position
                        d = q(sqrt(pow(abs(x2 - x1), 2) + pow(abs(y2 - y1), 2) + pow(abs(z2 - z1), 2)), 'au')
                        cls.distances[body.id][star.id] = round(d)
                        ab = q(star.luminosity.m / pow(d.to('au').m, 2), 'Vs')
                    else:  # Other stars in the universe
                        x1, y1, z1 = body.find_topmost_parent(body).position
                        x2, y2, z2 = star.position
                        d = q(sqrt(pow(abs(x2 - x1), 2) + pow(abs(y2 - y1), 2) + pow(abs(z2 - z1), 2)), 'lightyears')
                        cls.distances[body.id][star.id] = round(d)
                        ab = q(star.luminosity.m / pow(d.to('au').m, 2), 'Vs')

                    if star not in cls.relative_sizes[body.id]:
                        d = cls.distances[body.id][star.id]
                        value = small_angle_aproximation(star, d.to('km').m)
                        cls.relative_sizes[body.id][star.id] = value
                        cls.aparent_brightness[body.id][star.id] = ab

    @classmethod
    def visibility_by_albedo(cls):
        to_see = cls.planets + cls.satellites + cls.asteroids
        to_see = [i for i in to_see if i.orbit is not None or i.rogue is True]
        for i, body in enumerate(to_see):
            if body.orbit is not None:
                star = body.find_topmost_parent(body)
                luminosity = star.luminosity.to('watt').m
            else:
                luminosity = 0
            if body.id not in cls.aparent_brightness:
                cls.aparent_brightness[body.id] = {}
            if body.id not in cls.relative_sizes:
                cls.relative_sizes[body.id] = {}
            if body.id not in cls.distances:
                cls.distances[body.id] = {}

            others = to_see[:i] + to_see[i + 1:]
            if body.orbit is not None:
                cls.visibility_of_stars(body)
                stars = [star for star in body.orbit.star]
                x = body.orbit.a.to('m').m  # position of the Observer's planet
            else:
                stars = Systems.get_only_stars()
                x = body.position[0]
            for star in stars:
                if star.id not in cls.distances[body.id]:
                    if body.parent is not None:
                        if body.parent.celestial_type in ('star', 'system'):
                            relative_distance = body.orbit.a.to('km').m
                        else:
                            relative_distance = body.parent.orbit.a.to('km').m
                    else:
                        relative_distance = eucledian_distance(body.position, star.position)
                else:
                    relative_distance = cls.distances[body.id][star.id].to('km').m
                cls.relative_sizes[body.id][star.id] = small_angle_aproximation(star, relative_distance)

            others = [o for o in others]

            for other in others:
                if other.orbit is not None:
                    y = other.orbit.a.to('m').m  # position of the observed body
                elif other.rogue:
                    y = other.position[0]
                else:  # body is not in orbit yet, but it's not a rogue planet either.
                    y = None

                if y is not None:
                    distance = abs(y - x) if y > x else abs(x - y)  # linear distance, much quicker
                    cls.distances[body.id][other.id] = q(distance, 'm')
                    cls.relative_sizes[body.id][other.id] = small_angle_aproximation(other, distance)
                    albedo = other.albedo.m / 100
                    radius = other.radius.to('m').m
                    visibility = 'undetermined'
                    if other.rogue is not True:
                        semi_major_axis = other.orbit.semi_major_axis.to('m').m
                        ab = (albedo * luminosity * pow(radius, 2)) / (pow(semi_major_axis, 2) * pow(distance, 2))
                        if ab > 1.3e-7:
                            visibility = 'naked'
                        elif ab < 1.2e-9:
                            visibility = 'telescope'
                    cls.aparent_brightness[body.id][other.id] = visibility


Universe.init()
Systems.import_clases(universe=Universe)
# the orbital velocity of a planet in orbit is equal to sqrt(M/a) where M is the mass of the star and a is the sma.
# a planet ejected from its system retains its orbital velocity (I guess) but now traces a linear path, away from
# the system. In 3D space, is often said that a body is moving "towards a system", so
# x0 = a*cos(k)+c, donde c es el centro de la ellipse
# y0 = b*sin(k)

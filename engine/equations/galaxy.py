from engine.backend import q, generate_id, turn_into_roman
from .space import Universe
from random import uniform
from time import sleep


class Galaxy:
    radius = 0
    inner = None
    outer = None

    density_at_location = None

    name = 'Galaxy'

    celestial_type = 'galaxy'
    proto_stars = None

    orbit = None

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.density_at_location = {}  # tho this dict may get very large.
        self.proto_stars = []
        self.id = data['id'] if 'id' in data else generate_id()

    def add_proto_stars(self, list_of_dicts):
        for data in list_of_dicts:
            star = ProtoStar(data)
            self.proto_stars.append(star)
            # Este sleep es necesario porque de otro modo todas las ProtoStars tienen el mismo ID.
            sleep(0.001)

    def set_radius(self, radius):
        self.radius = q(radius, 'ly')
        self.inner = q(round((radius * 0.47), 0), 'ly')
        self.outer = q(round((radius * 0.6), 0), 'ly')
        Universe.add_astro_obj(self)

    def record_density_at_location(self, location, density):
        if location not in self.density_at_location:
            self.density_at_location[location] = density

    def get_density_at_location(self, location):
        if location in self.density_at_location:
            return self.density_at_location[location]

    def validate_position(self, location=2580):  # ly
        if self.inner is not None and self.outer is not None:
            assert self.inner <= q(location, 'ly') <= self.outer, "Neighbourhood is uninhabitable."
        else:
            raise AssertionError('Galactic Characteristics are not set.')


class ProtoStar:
    celestial_type = 'star'

    def __init__(self, data):
        self.cls = data['class']
        self.id = generate_id()
        self.idx = data['idx']

        mass = 0
        if self.cls.startswith('O'):
            mass = uniform(16.0, 120.0)
        elif self.cls.startswith('B'):
            mass = uniform(2.1, 16.0)
        elif self.cls.startswith('A'):
            mass = uniform(1.4, 2.1)
        elif self.cls.startswith('F'):
            mass = uniform(1.04, 1.4)
        elif self.cls.startswith('G'):
            mass = uniform(0.8, 1.04)
        elif self.cls.startswith('K'):
            mass = uniform(0.45, 0.8)
        elif self.cls.startswith('M'):
            mass = uniform(0.08, 0.45)

        self.mass = q(mass, 'sol_mass')

    def __str__(self):
        return f'{self.cls}_{turn_into_roman(self.idx+1)}'

    def __repr__(self):
        return f"ProtoStar {self.cls} #{self.idx}"

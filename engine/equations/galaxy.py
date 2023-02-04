from engine.backend import q, generate_id, turn_into_roman
from itertools import cycle


class Galaxy:
    radius = 0
    inner = None
    outer = None

    density_at_location = None

    name = 'Galaxy'

    celestial_type = 'galaxy'

    orbit = None

    id = None

    stellar_neighbourhoods = None
    neighbourhood_cycler = None
    current_neighbourhood = None

    def __init__(self):
        self.stellar_neighbourhoods = []
        self.neighbourhood_cycler = cycle(self.stellar_neighbourhoods)
        self.density_at_location = {}  # tho this dict may get very large.
        self.proto_stars = []

    def initialize(self, data=None):
        if data is None:
            self.id = generate_id()
        elif type(data) is dict:
            self.id = data['id']
            self.set_radius(data['radius'])
        elif type(data) is Galaxy:
            self.id = data.id
            self.set_radius(data.radius)

    def add_neighbourhood(self, new):
        if new not in self.stellar_neighbourhoods:
            self.stellar_neighbourhoods.append(new)
            if len(self.stellar_neighbourhoods) == 1:
                self.cycle_neighbourhoods()

    def cycle_neighbourhoods(self):
        new = next(self.neighbourhood_cycler)
        self.current_neighbourhood = new
        return new

    def set_radius(self, radius):
        self.radius = q(radius, 'ly')
        self.inner = q(round((radius * 0.47), 0), 'ly')
        self.outer = q(round((radius * 0.6), 0), 'ly')

    def record_density_at_location(self, location, density):
        if location not in self.density_at_location:
            self.density_at_location[location] = density

    def get_density_at_location(self, location):
        if location in self.density_at_location:
            return self.density_at_location[location]

    def validate_position(self, location):  # ly
        if self.inner is not None and self.outer is not None:
            return self.inner <= q(location, 'ly') <= self.outer
        else:
            raise AssertionError('Galactic Characteristics are not set.')

    def __repr__(self):
        return f'Galaxy #{self.id}'

    def __eq__(self, other):
        is_equal = self.id == other.id
        is_equal = is_equal and self.radius == other.radius
        is_equal = is_equal and self.inner == other.inner
        is_equal = is_equal and self.outer == other.outer
        return is_equal


class ProtoStar:
    celestial_type = 'star'

    def __init__(self, data):
        self.cls = data['class']
        self.id = generate_id()
        self.idx = data['idx']
        self.neighbourhood_idx = data['neighbourhood_idx']

        mass = 0
        b = self.idx + self.neighbourhood_idx
        if self.cls.startswith('O'):
            mass += 16.0 + b / 10
        elif self.cls.startswith('B'):
            mass += 2.1 + b / 10
        elif self.cls.startswith('A'):
            mass += 1.4 + b / 10
        elif self.cls.startswith('F'):
            mass += 1.04 + b / 10
        elif self.cls.startswith('G'):
            mass += 0.8 + b / 10
        elif self.cls.startswith('K'):
            mass += 0.45 + b / 10
        elif self.cls.startswith('M'):
            mass += 0.08 + b / 100

        self.mass = q(mass, 'sol_mass')

    def __str__(self):
        return f'{self.cls}{turn_into_roman(self.idx + 1)}'

    def __repr__(self):
        return f"ProtoStar {self.cls} #{self.idx}"

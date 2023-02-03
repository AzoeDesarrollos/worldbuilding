from math import pi, acos, sin, cos, floor
from engine.backend import q, generate_id
from random import uniform


class StellarNeighbourhood:
    _o_stars = 0
    _b_stars = 0
    _a_stars = 0
    _f_stars = 0
    _g_stars = 0
    _k_stars = 0
    _m_stars = 0
    _w_dwarfs = 0
    _b_dwarfs = 0
    _other = 0

    _total_stars = 0
    _total_systems = 0

    _single = 0
    _binary = 0
    _triple = 0
    _multiple = 0

    radius = None

    location = None
    density = None

    celestial_type = 'stellar bubble'

    main_sequence_stars = 0

    def __init__(self, parent):
        self.parent = parent
        self.galaxy = self.parent.parent.galaxy.characteristics
        self.pre_processed_system_positions = {
            "Single": [],
            "Binary": [],
            "Triple": [],
            "Multiple": []
        }

    def process_data(self, data):
        for system_id in data['Binary Systems']:
            system_data = data['Binary Systems'][system_id]
            x = system_data['pos']['x']
            y = system_data['pos']['y']
            z = system_data['pos']['z']
            self.pre_processed_system_positions['Binary'].append((x, y, z))

    def set_location(self, location, known_density=None):
        self.location = location
        if known_density is not None:
            self.galaxy.record_density_at_location(location, known_density)
            density = known_density
        else:
            density = self.galaxy.get_density_at_location(location)
        if density is None:
            self.density = uniform(0.003, 0.012)
            self.galaxy.record_density_at_location(location, self.density)
        else:
            self.density = density
        return self.density

    def set_radius(self, radius):
        assert radius < 500, 'Stellar Neighbourhood will pop out of the galatic disk'
        self.radius = q(radius, 'ly')
        self._calculate(self.density, self.radius.m)

    def _calculate(self, density, radius):
        stellar_factor = density * ((4 / 3) * pi * radius ** 3)

        self._o_stars = round(stellar_factor * 0.9 * 0.0000003, 0)
        self._b_stars = round(stellar_factor * 0.9 * 0.0013, 0)
        self._a_stars = round(stellar_factor * 0.9 * 0.006, 0)
        self._f_stars = round(stellar_factor * 0.9 * 0.03, 0)
        self._g_stars = round(stellar_factor * 0.9 * 0.076, 0)
        self._k_stars = round(stellar_factor * 0.9 * 0.121, 0)
        self._m_stars = round(stellar_factor * 0.9 * 0.7645, 0)
        self._w_dwarfs = round(stellar_factor * 0.09, 0)
        self._b_dwarfs = round(stellar_factor / 2.5, 0)
        self._other = floor(stellar_factor * 0.01)

        self._total_stars = sum([self._o_stars, self._b_stars, self._a_stars, self._f_stars, self._g_stars,
                                 self._k_stars, self._m_stars, self._w_dwarfs, self._b_dwarfs, self._other])

        self.main_sequence_stars = sum([self._o_stars, self._b_stars, self._a_stars, self._f_stars, self._g_stars,
                                        self._k_stars, self._m_stars])

        self._binary = int(round(((self._total_stars / 1.58) * 0.33), 0))
        self._triple = int(round(((self._total_stars / 1.58) * 0.08), 0))
        self._multiple = int(round(((self._total_stars / 1.58) * 0.03), 0))
        self._single = int(self._total_stars - ((self._binary * 2) + (self._triple * 3) + (self._multiple * 4)))

        self._total_systems = int(sum([self._single, self._binary, self._triple, self._multiple]))

        self.individual_stars = [{'class': 'O', 'idx': i} for i in range(int(self._o_stars))]
        self.individual_stars += [{'class': 'B', 'idx': i} for i in range(int(self._b_stars))]
        self.individual_stars += [{'class': 'A', 'idx': i} for i in range(int(self._a_stars))]
        self.individual_stars += [{'class': 'F', 'idx': i} for i in range(int(self._f_stars))]
        self.individual_stars += [{'class': 'G', 'idx': i} for i in range(int(self._g_stars))]
        self.individual_stars += [{'class': 'K', 'idx': i} for i in range(int(self._k_stars))]
        self.individual_stars += [{'class': 'M', 'idx': i} for i in range(int(self._m_stars))]

    def stars(self, spectral_type: str = 'g') -> int:

        types = 'o,b,a,f,g,k,m,wd,white,brown,bd,black hole'.split(',')
        assert spectral_type in types, f'spectral_type "{spectral_type}" is unrecognizable.'

        if spectral_type == 'o':
            returned = self._o_stars
        elif spectral_type == 'b':
            returned = self._b_stars
        elif spectral_type == 'a':
            returned = self._a_stars
        elif spectral_type == 'f':
            returned = self._f_stars
        elif spectral_type == 'g':
            returned = self._g_stars
        elif spectral_type == 'k':
            returned = self._k_stars
        elif spectral_type == 'm':
            returned = self._m_stars
        elif spectral_type in ('wd', 'white'):
            returned = self._w_dwarfs
        elif spectral_type in ('bd', 'brown'):
            returned = self._b_dwarfs
        else:
            returned = self._other

        return int(returned)

    def systems(self, configuration: str = 'single') -> int:
        if configuration == 'single':
            return self._single
        elif configuration == 'binary':
            return self._binary
        elif configuration == 'triple':
            return self._triple
        elif configuration == 'multiple':
            return self._multiple
        else:
            raise ValueError('Configuration is invalid.')

    def totals(self, kind: str = 'stars'):
        if kind == 'stars':
            return self._total_stars
        elif kind == 'systems':
            return self._total_systems
        elif kind == 'main sequence':
            return self.main_sequence_stars
        else:
            raise ValueError(f'Kind "{kind}" is unrecognizable.')

    def system_positions(self, seed=1):
        assert seed > 0, 'the seed must be greater than 0'
        systems = ['Single'] * (self.systems('single')) + ['Binary'] * self.systems('binary')
        systems += ['Triple'] * self.systems('triple') + ['Multiple'] * self.systems('multiple')

        divisor = 2 ** 31 - 1
        constant = 48271

        initial_value = (constant * seed) % divisor
        r_raw = initial_value
        distances = []
        for i, system in enumerate(systems):
            if len(self.pre_processed_system_positions[system]):
                x, y, z = self.pre_processed_system_positions[system].pop()
            else:
                p_raw = constant * r_raw % divisor
                w_raw = constant * p_raw % divisor
                r_raw = constant * w_raw % divisor

                p_normal = p_raw / divisor
                w_normal = w_raw / divisor
                r_normal = r_raw / divisor

                p = p_normal ** (1 / 3) * self.radius.m
                w = w_normal * 2 * pi
                r = acos(2 * r_normal - 1)

                x = round(p * sin(r) * cos(w), 2)
                y = round(p * sin(r) * sin(w), 2)
                z = round(p * cos(r), 2)

            distances.append({'configuration': systems[i], 'pos': [x, y, z]})

        return distances


class DefinedNeighbourhood:
    # this is the actual object. The class above is just a collection of functions
    # and it may be disassembled in the future.

    idx = None

    def __init__(self, data):
        self.location = data['location']
        self.radius = data['radius']
        self.systems = data['systems']

    def __repr__(self):
        return 'Neighbourhood Object'


class ProtoSystem:
    celestial_type = 'system'
    name = None

    orbit = None

    def __init__(self, data):
        self.composition = data['composition']
        self.location = data['location']
        self.idx = data['idx']
        self.id = generate_id()

    def __repr__(self):
        return f'{self.composition.title()} ProtoSystem'

from engine.backend import q, generate_id, turn_into_roman, roll
from .orbit import GalacticNeighbourhoodOrbit
from math import pi, acos, sin, cos, floor
from .galaxy import ProtoStar
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

    galaxy = None

    def __init__(self, parent):
        self.parent = parent

    def set_galaxy(self):
        self.galaxy = self.parent.parent.galaxy.current

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

    def recalculate(self, density, radius):
        self._calculate(float(density), float(radius))

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

        # The distribution of individual stars into systems only takes into account main sequence stars because
        # the program doesn't allow for neither the creation of brown or white dwarves or black holes yet.
        # this might change in future revisions.
        self._binary = int(round(((self.main_sequence_stars / 1.58) * 0.33), 0))
        self._triple = int(round(((self.main_sequence_stars / 1.58) * 0.08), 0))
        self._multiple = int(round(((self.main_sequence_stars / 1.58) * 0.03), 0))
        self._single = int(self.main_sequence_stars - ((self._binary * 2) + (self._triple * 3) + (self._multiple * 4)))
        # se agregan los cuerpos compatos porque por definicón son sistemas simples.
        self._single += int(self._w_dwarfs + self._b_dwarfs + self._other)

        self._total_systems = int(sum([self._single, self._binary, self._triple, self._multiple]))

        # this is because some of the binary pairs are part
        self._binary += self._triple + (self._multiple * 2)
        # of triple and cuadruple systems.

        self.individual_stars = [{'class': 'O', 'idx': i} for i in range(int(self._o_stars))]
        self.individual_stars += [{'class': 'B', 'idx': i} for i in range(int(self._b_stars))]
        self.individual_stars += [{'class': 'A', 'idx': i} for i in range(int(self._a_stars))]
        self.individual_stars += [{'class': 'F', 'idx': i} for i in range(int(self._f_stars))]
        self.individual_stars += [{'class': 'G', 'idx': i} for i in range(int(self._g_stars))]
        self.individual_stars += [{'class': 'K', 'idx': i} for i in range(int(self._k_stars))]
        self.individual_stars += [{'class': 'M', 'idx': i} for i in range(int(self._m_stars))]

    def stars(self, spectral_type: str = 'g') -> int:

        types = 'o,b,a,f,g,k,m,wd,white,brown,bd,black,black hole'.split(',')
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

    def system_positions(self, current_neighbourhood):
        if current_neighbourhood.nei_seed is None:
            seed = 1
        else:
            seed = current_neighbourhood.nei_seed

        systems = ['Single'] * (self.systems('single')) + ['Binary'] * self.systems('binary')
        systems += ['Triple'] * self.systems('triple') + ['Multiple'] * self.systems('multiple')

        divisor = 2 ** 31 - 1
        constant = 48271

        initial_value = (constant * seed) % divisor
        r_raw = initial_value
        distances = []
        for i, system in enumerate(systems):
            if len(current_neighbourhood.pre_processed_system_positions[system]):
                x, y, z = current_neighbourhood.pre_processed_system_positions[system].pop()
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

    pre_processed_system_positions = None

    proto_stars = None

    quantities = None

    systems = []

    nei_seed = None

    orbit = None

    def __init__(self, idx, data):
        self.idx = idx
        self.id = data['id'] if 'id' in data else generate_id()
        self.nei_seed = data['seed'] if 'seed' in data else self._roll_seed()
        self.location = data['location']
        self.radius = data['radius']
        self.density = data['density']
        self.other = data['other']
        self.proto_stars = []
        self.pre_processed_system_positions = {
            "Single": [],
            "Binary": [],
            "Triple": [],
            "Multiple": []
        }
        self.quantities = {
            "Single": 0,
            "Binary": 0,
            "Triple": 0,
            "Multiple": 0
        }
        self.orbit = GalacticNeighbourhoodOrbit(self.location)

    def set_quantity(self, key, quantity):
        self.quantities[key] = quantity

    def add_true_system(self, system):
        if system not in self.systems:
            self.systems.append(system)

    def get_system(self, id):
        for system in self.systems:
            if system.id == id:
                return system

    def __repr__(self):
        return f'{turn_into_roman(self.idx)}@{str(self.location)}'

    def process_data(self, data):
        for tag in 'Single Systems', 'Binary Systems':
            tag_name = tag.split()[0]
            for system_id in data[tag]:
                if data[tag][system_id]['neighbourhood_id'] == self.id:
                    system_data = data[tag][system_id]
                    if 'position' in system_data:
                        x = system_data['position']['x']
                        y = system_data['position']['y']
                        z = system_data['position']['z']
                        self.pre_processed_system_positions[tag_name].append((x, y, z))

    def add_proto_stars(self, list_of_dicts):
        for data in list_of_dicts:
            data.update({'neighbourhood_idx': self.idx - 1})
            star = ProtoStar(data)
            self.proto_stars.append(star)

    def __eq__(self, other):
        equal = self.id == other.id
        equal = equal and self.location == other.location
        equal = equal and self.radius == other.radius
        equal = equal and self.density == other.density
        return equal

    @staticmethod
    def _roll_seed():
        rolled = roll(1.0, 2 * 10 ** 8)
        return int(rolled)


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

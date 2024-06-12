from .general import BodyInHydrostaticEquilibrium
from engine.backend.util import q, generate_id
from random import randint, choice
from math import sqrt, pi


class CompactObject(BodyInHydrostaticEquilibrium):
    orbit = None
    celestial_type = 'compact'

    neighbourhood_id = None


class BinaryPartner:
    prefix = ''
    sub_pos = None
    _system = None
    _shared_mass = None
    _inner_forbidden = None
    _outer_forbidden = None

    _lifetime = None
    _age = None

    letter = None

    evolution_id = None

    def __init__(self, data):
        # Star's lifetime; compact objects may have their own way of calculating lifetime. Required for age.
        if hasattr(self, 'luminosity'):
            self._lifetime = data['mass'] / float(self.luminosity.m)
        else:
            self._lifetime = data['mass'] / pow(data['mass'], 3.5)

    def set_age(self, x=0):
        # copied from Star.set_age(). Might be wrong for black holes.
        if self._age == -1:
            self._age = (self._lifetime * 0.46) * 10 ** 10
        else:
            age = (self._lifetime * x) * 10 ** 10
            if age != self._age:
                self._age = age
                self.evolution_id = generate_id()

    def inherit(self, system, inner, outer, mass, idx):
        self.prefix = system.letter
        self.sub_pos = idx
        self._system = system
        self._shared_mass = mass
        self._inner_forbidden = inner
        self._outer_forbidden = outer

    @property
    def system(self):
        if self._system is not None:
            return self._system
        else:
            return self

    def composition(self):
        return [self]

    @property
    def shared_mass(self):
        return self._shared_mass

    @property
    def inner_forbbiden_zone(self):
        return self._inner_forbidden

    @property
    def outer_forbbiden_zone(self):
        return self._outer_forbidden

    def __getitem__(self, item):
        if type(item) is int:
            if item == 0:
                return self
            raise StopIteration()


class BlackHole(CompactObject, BinaryPartner):
    compact_subtype = 'black'

    age = 0
    mass = None
    event_horizon = None
    photon_sphere = None
    lifetime = None
    temperature = None

    rogue = True  # Black holes, by definition, do not orbit anything

    def __init__(self, data):
        mass = data['mass']
        assert mass >= 5, "A stellar mass black hole must have 5 solar masses or more."
        self._mass = mass
        self._event = 2.95 * mass
        self._photon = 1.5 * self._event

        self.id = data['id'] if 'id' in data else generate_id()
        self.evolution_id = self.id
        self.neighbourhood_id = data['neighbourhood_id'] if 'neighbourhood_id' in data else None

        super().__init__(data)
        # https://en.wikipedia.org/wiki/Hawking_radiation
        self._lifetime = 2.140e67 * mass ** 3
        self._temperature = 1 / (4 * pi * sqrt(2 * mass * self._event * (1 - (2 * mass / self._event))))
        if 'age' in data:
            self._age = data['age']
        else:
            self.set_age()
        self.set_qs()

    def set_qs(self):
        self.mass = q(self._mass, 'sol_mass')
        self.event_horizon = q(self._event, 'km')
        self.photon_sphere = q(self._photon, 'km')
        self.lifetime = q(self._lifetime, 'years')
        self.temperature = q(self._temperature, 'kelvin')
        self.age = q(self._age, 'years')

    @property
    def radius(self):
        return self.event_horizon

    def __repr__(self):
        return 'Black Hole'

    def __str__(self):
        if self.has_name:
            return self.name
        elif hasattr(self, 'idx'):
            return f'Black Hole #{self.idx}'


class NeutronStar(CompactObject, BinaryPartner):
    compact_subtype = 'neutron'

    def __init__(self, data):
        super().__init__(data)
        self._mass = data['mass']
        self._radius = data['radius']

        self.mass = q(self._mass, 'sol_mass')
        self.radius = q(self._radius, 'km')

        self.id = data['id'] if 'id' in data else generate_id()
        self.evolution_id = self.id
        self.neighbourhood_id = data['neighbourhood_id'] if 'neighbourhood_id' in data else None
        self.sub_cls = data['sub'] if 'sub' in data else choice(['RPP', 'RRAT', 'SGR', 'AXP'])
        if 'age' in data:
            self._age = data['age']
        else:
            self.set_age()

        self.age = q(self._age, 'years')

    @staticmethod
    def validate(value, name):
        if name == 'mass':
            assert 1.4 <= value <= 3.0, 'Neutron Stars have masses between 1.4 and 3 solar masses.'
            return True
        elif name == 'radius':
            assert 10 <= value <= 13, 'Neutron Stars have radii between 10 and 13 kilometers.'
            return True

    def __repr__(self):
        return 'Neutron Star'

    def __str__(self):
        if self._system is None:
            base = 'INS'  # means it is not in a binary
        else:
            base = 'XNS'  # the X stands for X-Ray
            # though the sub_class may not longer apply if it is part of a binary.
        return f'{base}-{self.sub_cls}'


class WhiteDwarf(CompactObject, BinaryPartner):
    compact_subtype = 'white'

    def __init__(self, data):
        mass = data['mass']
        assert 0.17 <= mass <= 1.4, 'White Dwarfs have masses between 0.17 and 1.4 solar masses'
        self._mass = mass
        self._radius = pow(mass, -1 / 3)
        self.mass = q(self._mass, 'sol_mass')
        self.radius = q(self._radius, 'earth_radius')

        self.id = data['id'] if 'id' in data else generate_id()
        self.evolution_id = self.id
        self.neighbourhood_id = data['neighbourhood_id'] if 'neighbourhood_id' in data else None
        self.sub_cls = data['sub'] if 'sub' in data else ''.join([str(randint(0, 9)) for _ in range(3)])

        luminosity = pow(mass, 3.5)
        temperature = pow((luminosity / pow(self._radius, 2)), (1 / 4))
        self.luminosity = q(luminosity, 'sol_luminosity')
        self.temperature = q(temperature, 'kelvin')
        super().__init__(data)

        if 'age' in data:
            self._age = data['age']
        else:
            self.set_age()
        self.age = q(self._age, 'years')

    def __repr__(self):
        return 'White Dwarf'

    def __str__(self):
        # "ns" is now the first four numbers of the last portion of the ID.
        ns = self.id.split('-')[1][0:4]
        return f'WD{ns}+{self.sub_cls}'


class BrownDwarf(CompactObject, BinaryPartner):
    compact_subtype = None  # this is intentional, because it is not compact.
    idx = 0

    def __init__(self, data):
        mass = data['mass']
        assert 13 <= mass <= 80, 'Brown Dwarfs have masses between 13 and 80 Jupiter masses'
        self._mass = mass
        self._radius = data['radius']

        self.mass = q(self._mass, 'jupiter_mass')
        self.radius = q(self._radius, 'jupiter_radius')

        self.id = data['id'] if 'id' in data else generate_id()
        self.evolution_id = self.id
        self.neighbourhood_id = data['neighbourhood_id'] if 'neighbourhood_id' in data else None

        luminosity = pow(mass, 3.5)
        temperature = pow((luminosity / pow(self._radius, 2)), (1 / 4))
        # based on https://en.wikipedia.org/wiki/Stellar_classification#Cool_red_and_brown_dwarf_classes
        if 9 <= mass <= 25:
            self.classification = 'Y'
        elif 25 < mass <= 63:  # this is made up
            self.classification = 'L'
        else:
            self.classification = 'T'

        self.cls = self.classification
        self.luminosity = q(luminosity, 'sol_luminosity')
        self.temperature = q(temperature, 'kelvin')
        super().__init__(data)
        if 'age' in data:
            self._age = data['age']
        else:
            self.set_age()
        self.age = q(self._age, 'years')

    def __repr__(self):
        return f"{self.cls}{self.idx + 1}"

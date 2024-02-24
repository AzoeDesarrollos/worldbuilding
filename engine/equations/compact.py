from engine.backend.util import q, generate_id
from .general import BodyInHydrostaticEquilibrium
from random import randint, choice


class CompactObject(BodyInHydrostaticEquilibrium):
    orbit = None
    celestial_type = 'compact'


class BlackHole(CompactObject):
    _mass = None
    _event = None
    _photon = None

    compact_subtype = 'black'

    def __init__(self, mass):
        assert mass >= 5, "A stellar mass black hole must have 5 solar masses or more."
        self._mass = mass
        self._event = 2.95 * mass
        self._photon = 1.5 * self._event
        self.id = generate_id()

    @property
    def mass(self):
        return q(self._mass, 'sol_mass')

    @property
    def event_horizon(self):
        return q(self._event, 'km')

    @property
    def photon_sphere(self):
        return q(self._photon, 'km')

    def __repr__(self):
        return 'Black Hole'


class NeutronStar(CompactObject):
    compact_subtype = 'neutron'

    prefix = None
    sub_pos = 0
    _system = None
    _shared_mass = 0
    _inner_forbidden = None
    _outer_forbidden = None

    def __init__(self, mass, radius):
        self._mass = mass
        self._radius = radius

        self.mass = q(mass, 'sol_mass')
        self.radius = q(radius, 'km')

        self.id = generate_id()
        self.sub_cls = choice(['RPP', 'RRAT', 'SGR', 'AXP'])

    @staticmethod
    def validate(value, name):
        if name == 'mass':
            assert 1.4 <= value <= 3.0, 'Neutron Stars have masses between 1.4 and 3 solar masses.'
            return True
        elif name == 'radius':
            assert 10 <= value <= 13, 'Neutron Stars have radii between 10 and 13 kilometers.'
            return True

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

    def __repr__(self):
        return 'Neutron Star'

    def __str__(self):
        if self._system is None:
            base = 'INS'  # means it is not in a binary
        else:
            base = 'XNS'  # the X stands for X-Ray
            # though the sub_class may not longer apply if it is part of a binary.
        return f'{base}-{self.sub_cls}'


class WhiteDwarf(CompactObject):
    compact_subtype = 'white'

    def __init__(self, mass):
        assert 0.17 <= mass <= 1.4, 'White Dwarfs have masses between 0.17 and 1.4 solar masses'
        self._mass = mass
        self._radius = pow(mass, -1 / 3)
        self.mass = q(self._mass, 'sol_mass')
        self.radius = q(self._radius, 'earth_radius')

        self.id = generate_id()

        luminosity = pow(mass, 3.5)
        temperature = pow((luminosity / pow(self._radius, 2)), (1 / 4))
        self.luminosity = q(luminosity, 'sol_luminosity')
        self.temperature = q(temperature, 'kelvin')

    def __repr__(self):
        return 'White Dwarf'

    def __str__(self):
        # the numbers are completely made up.
        ns = ''.join([str(randint(1, 9)) for _ in range(4)])
        us = ''.join([str(randint(0, 9)) for _ in range(3)])
        return f'WD{ns}+{us}'


class BrownDwarf(CompactObject):
    compact_subtype = None  # this is intentional, because it is not compact.
    idx = 0

    def __init__(self, mass):
        assert 13 <= mass <= 80, 'Brown Dwarfs have masses between 13 and 80 Jupiter masses'
        self._mass = mass
        self._radius = 0.089552239 * mass - 0.164179104  # this is made up (proportional)

        self.mass = q(self._mass, 'jupiter_mass')
        self.radius = q(self._radius, 'jupiter_radius')

        self.id = generate_id()

        luminosity = pow(mass, 3.5)
        temperature = pow((luminosity / pow(self._radius, 2)), (1 / 4))
        # based on https://en.wikipedia.org/wiki/Stellar_classification#Cool_red_and_brown_dwarf_classes
        if 9 <= mass <= 25:
            self.classification = 'Y'
        elif 550 <= temperature <= 1.300:
            self.classification = 'T'
        else:
            self.classification = 'L'

        self.cls = self.classification
        self.luminosity = q(luminosity, 'sol_luminosity')
        self.temperature = q(temperature, 'kelvin')

    def __repr__(self):
        return f"{self.cls}{self.idx + 1}"

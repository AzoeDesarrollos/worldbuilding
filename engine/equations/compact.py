from engine.backend.util import q, generate_id
from .general import BodyInHydrostaticEquilibrium


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

    def __init__(self, mass, radius):
        self._mass = mass
        self._radius = radius

        self.mass = q(mass, 'sol_mass')
        self.radius = q(radius, 'km')

        self.id = generate_id()

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


class WhiteDwarf(CompactObject):
    compact_subtype = 'white'

    def __init__(self, mass):
        assert 0.17 <= mass <= 1.4, 'White Dwarfs have masses between 0.17 and 1.4 solar masses'
        self._mass = mass
        self._radius = pow(mass, -1 / 3)
        self.mass = q(self._mass, 'sol_mass')
        self.radius = q(self._radius, 'earth_radius')

        self.id = generate_id()

    def __repr__(self):
        return 'White Dwarf'


class BrownDwarf(CompactObject):
    compact_subtype = None  # this is intentional, because it is not compact.

    def __init__(self, mass):
        assert 13 <= mass <= 80, 'Brown Dwarfs have masses between 13 and 80 Jupiter masses'
        self._mass = mass
        self._radius = 0.089552239 * mass - 0.164179104  # this is made up (proportional)

        self.mass = q(self._mass, 'jupiter_mass')
        self.radius = q(self._radius, 'jupiter_radius')

        self.id = generate_id()

    def __repr__(self):
        return 'Brown Dwarf'

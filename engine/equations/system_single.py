from engine.equations.general import Flagable, Point
from .orbit import NeighbourhoodSystemOrbit
from engine.backend import EventHandler, q
from math import sqrt


class SingleSystem(Flagable):
    star = None
    _orbit = None
    _cartesian = None
    letter = None
    celestial_type = 'system'
    system_number = 'single'

    _habitable_inner = 0
    _habitable_outer = 0
    _inner_boundry = 0
    _outer_boundry = 0
    _frost_line = 0

    habitable_inner = None
    habitable_outer = None
    inner_boundry = None
    outer_boundry = None
    frost_line = None

    inner_forbbiden_zone = None
    outer_forbbiden_zone = None

    shared_mass = None
    age = None

    planetary = None

    def __init__(self, star=None, neighbourhood_id=None):
        self.star = star
        self.age = star.age
        self.id = star.id
        self.neighbourhood = neighbourhood_id
        EventHandler.register(self.save_single_systems, 'Save')
        self.set_derivated_characteristics(star.luminosity.m)
        self.set_qs()
        self.parent = self.star.parent if self.star.parent is not None else None
        self.star.set_parent(self)

    def set_derivated_characteristics(self, luminosity):
        mass = pow(luminosity, (1 / 3.5))
        self._habitable_inner = round(sqrt(luminosity / 1.1), 3)
        self._habitable_outer = round(sqrt(luminosity / 0.53), 3)
        self._inner_boundry = round(mass * 0.01, 3)
        self._outer_boundry = round(mass * 40, 3)
        self._frost_line = round(4.85 * sqrt(luminosity), 3)

    def set_qs(self):
        self.habitable_inner = q(self._habitable_inner, 'au')
        self.habitable_outer = q(self._habitable_outer, 'au')
        self.inner_boundry = q(self._inner_boundry, 'au')
        self.outer_boundry = q(self._outer_boundry, 'au')
        self.frost_line = q(self._frost_line, 'au')

    def validate_orbit(self, orbit):
        return self._inner_boundry < orbit < self._outer_boundry

    @property
    def cartesian(self):
        return self._cartesian

    @cartesian.setter
    def cartesian(self, values):
        x, y, z = 0, 0, 0
        if type(values) is dict:
            x, y, z = list(values.values())
        elif type(values) in (list, tuple):
            x, y, z = values

        self._cartesian = Point(x, y, z)
        self.star.cartesian = Point(x, y, z)

    def set_orbit(self, offset):
        self._orbit = NeighbourhoodSystemOrbit(*self._cartesian, offset)

    def composition(self):
        return [self]

    @property
    def mass(self):
        return self.star.mass

    @property
    def evolution_id(self):
        return self.star.evolution_id

    def save_single_systems(self, event):
        data = {
            self.id: {
                "star": self.star.id,
                "neighbourhood_id": self.neighbourhood,
                "flagged": self.flagged
            }
        }

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Single Systems': data})

    def __str__(self):
        return str(self.star)

    def __repr__(self):
        return f'System of {str(self.star)}'

    def __getitem__(self, item):
        if item == 0:
            return self.star
        else:
            raise StopIteration

from .general import BodyInHydrostaticEquilibrium
from math import pi, sqrt
from engine import q, material_densities


class Satellite:
    def __init__(self, comp):
        self.composition = comp
        assert sum([comp[material] for material in comp]) == 1
        self.density = q(sum([comp[material] * material_densities[material] for material in comp]), 'g/cm^3')

    def __repr__(self):
        return 'Natural Satellite'


class Major(Satellite, BodyInHydrostaticEquilibrium):
    def __init__(self, data):
        name = data.get('name', None)
        if name:
            self.name = name
            self.has_name = True
        super().__init__(data['composition'])
        self.radius = q(data['radius'], 'earth_radius')
        self.mass = q((self.radius.m ** 3 * self.density.to('earth_density').m), 'earth_mass')
        self.gravity = q(self.mass.m / (self.radius.m ** 2), 'earth_gravity')
        self.density = self.calculate_density(self.mass.to('grams'), self.radius.to('centimeters'))
        self.volume = self.calculate_volume(self.radius.to('kilometers'))
        self.surface = self.calculate_surface_area(self.radius.to('kilometers'))
        self.circumference = self.calculate_circumference(self.radius.to('kilometers'))
        self.escape_velocity = q(sqrt(self.mass.magnitude / self.radius.magnitude), 'earth_escape')


class Minor(Satellite):
    def __init__(self, data):
        super().__init__(data['composition'])
        a, b, c = data['a'], data['b'], data['c']
        self.a = q(a, 'km')
        self.b = q(b, 'km')
        self.c = q(c, 'km')
        if a > b > c:
            self.shape = 'triaxial'
        elif a == b > c:
            self.shape = 'obleate'
        elif a == b < c:
            self.shape = 'prolate'
        else:
            raise ValueError('object is not an ellipsoid')
        _a, _b, _c = self.a, self.b, self.c
        self.mass = q(self.density.to('kg/m^3').m * (4 / 3) * pi * _a.to('m').m * _b.to('m').m * _c.to('m').m, 'kg')

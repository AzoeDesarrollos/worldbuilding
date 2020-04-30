from .general import BodyInHydrostaticEquilibrium
from math import pi, sqrt
from engine import q, material_densities
from engine.backend import roll


class Satellite:
    density = None

    @staticmethod
    def calculate_density(ice, silicate, iron):
        comp = {'water ice': ice, 'silicates': silicate, 'iron': iron}
        density = q(sum([comp[material] * material_densities[material] for material in comp]), 'g/cm^3')
        return density


class Major(Satellite, BodyInHydrostaticEquilibrium):
    def __init__(self, data):
        name = data.get('name', None)
        if name:
            self.name = name
            self.has_name = True
        self.radius = q(data['radius'], 'earth_radius')
        self.density = self.set_density(data['composition'])
        self.mass = q((self.radius.m ** 3 * self.density.to('earth_density').m), 'earth_mass')
        self.gravity = q(self.mass.m / (self.radius.m ** 2), 'earth_gravity')
        self.volume = q(self.calculate_volume(self.radius.to('km').m), 'km^3')
        self.surface = q(self.calculate_surface_area(self.radius.to('km').m), 'km^2')
        self.circumference = q(self.calculate_circumference(self.radius.to('km').m), 'km')
        self.escape_velocity = q(sqrt(self.mass.magnitude / self.radius.magnitude), 'earth_escape')

    @staticmethod
    def set_density():
        return NotImplemented


class Minor(Satellite):
    def __init__(self, data):
        self.density = self.set_density(data['composition'])
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

    @staticmethod
    def set_density():
        return NotImplemented

    def __repr__(self):
        return super().__repr__() + ' ({} Ellipsoid)'.format(self.shape.title())


class RockyMoon(Satellite):
    """A natural satellite made mostly of Silicates"""

    def set_density(self, composition):
        silicate = composition['silicates'] if 'silicates' in composition else roll(0.6, 0.9)
        ice = composition['ice'] if 'ice' in composition else roll(1 - silicate, 0.9 - silicate)
        iron = composition['iron'] if 'iron' in composition else 1.0 - (silicate + ice)
        return self.calculate_density(ice, silicate, iron)


class IcyMoon(Satellite):
    """A natural satellite made mostly of Ice"""

    def set_density(self, composition):
        ice = composition['ice'] if 'ice' in composition else roll(0.6, 0.9)
        silicate = composition['silicates'] if 'silicates' in composition else roll(1 - ice, 0.9 - ice)
        iron = composition['iron'] if 'iron' in composition else 1.0 - (silicate + ice)
        self.density = self.calculate_density(ice, silicate, iron)


class HeavyMoon(Satellite):
    """Fictional moon made mostly of Iron and Silicates"""

    def set_density(self, composition):
        iron = composition['iron'] if 'iron' in composition else roll(0.6, 0.9)
        silicate = composition['silicates'] if 'silicates' in composition else roll(1 - iron, 0.9 - iron)
        ice = composition['ice'] if 'ice' in composition else 1.0 - (silicate + iron)
        self.density = self.calculate_density(ice, silicate, iron)


class LightMoon(Satellite):
    """Fictional moon made mostly of Iron and Ice"""

    def set_density(self, composition):
        iron = composition['iron'] if 'iron' in composition else roll(0.6, 0.9)
        ice = composition['ice'] if 'ice' in composition else roll(1 - iron, 0.9 - iron)
        silicate = composition['silicates'] if 'silicates' in composition else 1.0 - (ice + iron)
        self.density = self.calculate_density(ice, silicate, iron)


def create_moon(planet, star, data):
    moon_composition = None
    # No planet is ever ON the frost line.
    if planet.orbit.a > star.frost_line:
        moon_composition = IcyMoon
    elif planet.orbit.a < star.frost_line:
        moon_composition = RockyMoon

    if planet.type == 'Terrestial':
        if planet.habitable:
            moon_type = Major
        else:
            moon_type = Minor
    elif 'a' in data and 'b' in data and 'c' in data:
        moon_type = Minor
    else:
        moon_type = Major

    # dynamic moon creation
    moon = type('Moon', (moon_composition, moon_type), {})
    return moon(data)

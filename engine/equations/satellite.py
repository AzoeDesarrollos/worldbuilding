from engine.frontend.globales import COLOR_ICYMOON, COLOR_ROCKYMOON, COLOR_IRONMOON
from .general import BodyInHydrostaticEquilibrium
from engine import q, material_densities
from engine.backend import roll
from math import pi, sqrt


class Satellite:
    density = None
    celestial_type = ''
    has_name = False
    cls = None

    @staticmethod
    def calculate_density(ice, silicate, iron):
        d_e = 'earth_density'
        comp = {'water ice': ice / 100, 'silicates': silicate / 100, 'iron': iron / 100}
        density = q(sum([comp[material] * material_densities[material] for material in comp]), 'g/cm^3').to(d_e)
        return density

    def __repr__(self):
        return self.cls


class Major(Satellite, BodyInHydrostaticEquilibrium):
    celestial_type = 'satellite'

    def __init__(self, data):
        name = data.get('name', None)
        if name:
            self.name = name
            self.has_name = True
        self.composition = data['composition']
        self.radius = q(data['radius'], 'earth_radius')
        self.density = self.set_density(data['composition'])
        self.mass = q((self.radius.m ** 3 * self.density.to('earth_density').m), 'earth_mass')
        self.gravity = q(self.mass.m / (self.radius.m ** 2), 'earth_gravity')
        self.volume = q(self.calculate_volume(self.radius.to('km').m), 'km^3')
        self.surface = q(self.calculate_surface_area(self.radius.to('km').m), 'km^2')
        self.circumference = q(self.calculate_circumference(self.radius.to('km').m), 'km')
        self.escape_velocity = q(sqrt(self.mass.magnitude / self.radius.magnitude), 'earth_escape')
        self.clase = 'Major Moon'
        self.cls = 'Major'

    # noinspection PyUnusedLocal
    @staticmethod
    def set_density(composition):
        return NotImplemented


class Minor(Satellite):
    celestial_type = 'asteroid'

    def __init__(self, data):
        self.composition = data['composition']
        self.density = self.set_density(data['composition'])
        a, b, c = data.get('a axis', 0), data.get('b axis', 0), data.get('c axis', 0)
        self.a_axis = q(a, 'km')
        self.b_axis = q(b, 'km')
        self.c_axis = q(c, 'km')
        if a > b > c:
            self.shape = 'Tri-Axial Ellipsoid'
        elif a == b > c:
            self.shape = 'Obleate Spheroid'
        elif a == b < c:
            self.shape = 'Prolate Spheroid'
        else:
            raise AssertionError('object is not an ellipsoid')
        _a, _b, _c = self.a_axis.to('m').m, self.b_axis.to('m').m, self.c_axis.to('m').m
        self.volume = q((4 / 3) * pi * _a * _b * _c, 'km^3')
        self.mass = q(self.density.to('kg/m^3').m * self.volume.m, 'kg')
        self.radius = q(max([a, b, c]), 'km')
        self.cls = self.shape.split(' ')[0]
        self.clase = 'Minor Moon'

    # noinspection PyUnusedLocal
    @staticmethod
    def set_density(composition):
        return NotImplemented


class RockyMoon(Satellite):
    """A natural satellite made mostly of Silicates"""

    color = COLOR_ROCKYMOON

    def set_density(self, composition: dict):
        percent = sum(composition.values())
        s = composition['silicates'] if 'silicates' in composition else roll(60, 90) if percent < 100 else 0
        i = composition['water ice'] if 'water ice' in composition else roll(100 - s, 90 - s)if percent < 100 else 0
        r = composition['iron'] if 'iron' in composition else 100 - (s + i)if percent < 100 else 0
        return self.calculate_density(i, s, r)


class IcyMoon(Satellite):
    """A natural satellite made mostly of Ice"""

    color = COLOR_ICYMOON

    def set_density(self, composition: dict):
        percent = sum(composition.values())
        i = composition['water ice'] if 'water ice' in composition else roll(0.6, 0.9) if percent < 100 else 0
        s = composition['silicates'] if 'silicates' in composition else roll(1 - i, 0.9 - i) if percent < 100 else 0
        r = composition['iron'] if 'iron' in composition else 1.0 - (s + i) if percent < 100 else 0
        return self.calculate_density(i, s, r)


class IronMoon(Satellite):
    """Fictional moon made mostly of Iron"""

    color = COLOR_IRONMOON

    def set_density(self, composition: dict):
        percent = sum(composition.values())
        r = composition['iron'] if 'iron' in composition else roll(0.6, 0.9) if percent < 100 else 0
        s = composition['silicates'] if 'silicates' in composition else roll(1 - r, 0.9 - r) if percent < 100 else 0
        i = composition['water ice'] if 'water ice' in composition else 1.0 - (s + r) if percent < 100 else 0
        return self.calculate_density(i, s, r)


def create_moon(planet, star, data):
    moon_composition = None
    assert planet.orbit is not None, 'Planet needs an orbit first'
    if planet.orbit.a > star.frost_line:
        moon_composition = IcyMoon
    elif planet.orbit.a < star.frost_line:
        moon_composition = RockyMoon

    if planet.clase == 'Terrestial Planet':
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


def _moon_composition(data):
    ice = data['composition'].get('water ice', 0)
    rock = data['composition'].get('silicates', 0)
    iron = data['composition'].get('iron', 0)

    if rock > ice + iron:
        composition = RockyMoon
    elif ice > rock + iron:
        composition = IcyMoon
    elif iron > rock + ice:
        composition = IronMoon
    else:
        raise AssertionError('A satellite must be composed mostly of a single element')

    return composition


def major_moon_by_composition(data):
    moon_composition = _moon_composition(data)
    moon = type('Moon', (moon_composition, Major), {})
    return moon(data)


def minor_moon_by_composition(data):
    moon_composition = _moon_composition(data)
    moon = type('Moon', (moon_composition, Minor), {})
    return moon(data)

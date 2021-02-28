from engine.frontend.globales import COLOR_ICYMOON, COLOR_ROCKYMOON, COLOR_IRONMOON
from .general import BodyInHydrostaticEquilibrium
from .lagrange import get_lagrange_points
from engine import q, material_densities
from engine.backend import roll
from datetime import datetime
from math import pi, sqrt
from .orbit import Orbit


class Satellite:
    mass = None
    density = None
    celestial_type = ''
    has_name = False
    cls = None
    orbit = None
    hill_sphere = 0
    roches_limit = 0
    temperature = 'N/A'
    comp = ''
    lagrange_points = None

    @staticmethod
    def calculate_density(ice, silicate, iron):
        comp = {'water ice': ice / 100, 'silicates': silicate / 100, 'iron': iron / 100}
        density = q(sum([comp[material] * material_densities[material] for material in comp]), 'g/cm^3')
        return density

    def set_orbit(self, planet, orbital_parameters):
        orbit = Orbit(*orbital_parameters)
        orbit.set_astrobody(planet, self)

        semi_major_axis = self.orbit.semi_major_axis.to('au').m
        planet_mass = planet.mass.to('sol_mass').m
        self.lagrange_points = get_lagrange_points(semi_major_axis, planet_mass, self.mass.to('earth_mass').m)

        self.hill_sphere = self.set_hill_sphere()
        return self.orbit

    def set_hill_sphere(self):
        a = self.orbit.semi_major_axis.magnitude
        mp = self.mass.to('earth_mass').magnitude
        ms = self.orbit.star.mass.to('sol_mass').magnitude
        return q(round((a * pow(mp / ms, 1 / 3) * 235), 3), 'earth_radius')

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
        assert data.get('radius'), "Must fill parameter \n'Radius'"
        self.radius = q(data['radius'], 'earth_radius')
        self.density = self.set_density(data['composition'])
        self.mass = q((float(self.radius.m) ** 3 * self.density.to('earth_density').m), 'earth_mass')
        self.gravity = q(self.mass.m / (float(self.radius.m) ** 2), 'earth_gravity')
        self.volume = q(self.calculate_volume(self.radius.to('km').m), 'km^3')
        self.surface = q(self.calculate_surface_area(self.radius.to('km').m), 'km^2')
        self.circumference = q(self.calculate_circumference(self.radius.to('km').m), 'km')
        self.escape_velocity = q(sqrt(self.mass.magnitude / self.radius.magnitude), 'earth_escape_velocity')
        self.clase = 'Major Moon'
        self.cls = self.comp + ' Major'
        self.title = 'Major'

        # ID values make each satellite unique, even if they have the same characteristics.
        now = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])
        self.id = data['id'] if 'id' in data else now

    # noinspection PyUnusedLocal
    @staticmethod
    def set_density(composition):
        return NotImplemented


class Minor(Satellite):
    celestial_type = 'asteroid'
    habitable = False

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
        self.title = self.cls

        # ID values make each satellite unique, even if they have the same characteristics.
        now = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])
        self.id = data['id'] if 'id' in data else now

    # noinspection PyUnusedLocal
    @staticmethod
    def set_density(composition):
        return NotImplemented


class RockyMoon(Satellite):
    """A natural satellite made mostly of Silicates"""

    color = COLOR_ROCKYMOON
    comp = 'Rocky'

    def set_density(self, composition: dict):
        percent = sum(composition.values())
        s = composition['silicates'] if 'silicates' in composition else roll(60, 90) if percent < 100 else 0
        i = composition['water ice'] if 'water ice' in composition else roll(100 - s, 90 - s) if percent < 100 else 0
        r = composition['iron'] if 'iron' in composition else 100 - (s + i) if percent < 100 else 0
        return self.calculate_density(i, s, r)


class IcyMoon(Satellite):
    """A natural satellite made mostly of Ice"""

    color = COLOR_ICYMOON
    comp = 'Icy'

    def set_density(self, composition: dict):
        percent = sum(composition.values())
        i = composition['water ice'] if 'water ice' in composition else roll(0.6, 0.9) if percent < 100 else 0
        s = composition['silicates'] if 'silicates' in composition else roll(1 - i, 0.9 - i) if percent < 100 else 0
        r = composition['iron'] if 'iron' in composition else 1.0 - (s + i) if percent < 100 else 0
        return self.calculate_density(i, s, r)


class IronMoon(Satellite):
    """Fictional moon made mostly of Iron"""

    color = COLOR_IRONMOON
    comp = 'Iron'

    def set_density(self, composition: dict):
        percent = sum(composition.values())
        r = composition['iron'] if 'iron' in composition else roll(0.6, 0.9) if percent < 100 else 0
        s = composition['silicates'] if 'silicates' in composition else roll(1 - r, 0.9 - r) if percent < 100 else 0
        i = composition['water ice'] if 'water ice' in composition else 1.0 - (s + r) if percent < 100 else 0
        return self.calculate_density(i, s, r)


def _moon_composition(data):
    ice = data['composition'].get('water ice', 0)
    rock = data['composition'].get('silicates', 0)
    iron = data['composition'].get('iron', 0)

    if rock > (ice + iron):
        composition = RockyMoon
    elif ice > (rock + iron):
        composition = IcyMoon
    elif iron > (rock + ice):
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

from .general import HydrostaticEquilibrium
from math import sqrt, pi
from engine import q


class Planet(HydrostaticEquilibrium):
    mass = 0
    radius = 0
    gravity = 0
    density = 0
    escape_velocity = 0
    composition = None

    def __init__(self, name, mass=None, radius=None, gravity=None):
        if not mass and not radius and not gravity:
            raise ValueError('must specify at least two values')

        self.name = name

        if mass:
            self.mass = q(mass, 'earth_masses')
        if radius:
            self.radius = q(radius, 'earth_radius')
        if gravity:
            self.gravity = q(gravity, 'earth_gravity')

        if not self.gravity:
            self.gravity = q(mass / (radius ** 2), 'earth_gravity')
        if not self.radius:
            self.radius = q(sqrt(mass / gravity), 'earth_radius')
        if not self.mass:
            self.mass = q(gravity * radius ** 2, 'earth_masses')

        self.density = self.calculate_density(self.mass, self.radius)
        self.volume = self.calculate_volume(self.radius.to('kilometers'))
        self.surface = self.calculate_surface_area(self.radius.to('kilometers'))
        self.calculate_circumference(self.radius.to('kilometers'))
        self.escape_velocity = q(sqrt(self.mass / self.radius), 'earth_escape')
        self.composition = {}


def planet_temperature(star_mass, semi_major_axis, albedo, greenhouse):
    # adapted from http://www.astro.indiana.edu/ala/PlanetTemp/index.html

    sigma = 5.6703 * (10 ** -5)
    l = 3.846 * (10 ** 33) * (star_mass ** 3)
    d = semi_major_axis * 1.496 * (10 ** 13)
    a = albedo / 100
    t = greenhouse * 0.5841

    x = sqrt((1 - a) * l / (16 * pi * sigma))

    T_eff = sqrt(x) * (1 / sqrt(d))
    T_eq = ((T_eff ** 4)) * (1 + (3 * t / 4))
    T_sur = T_eq / 0.9
    T_kel = round(sqrt(sqrt(T_sur)))

    kelvin = q(T_kel, 'degK')
    celcius = T_kel-273

    return round(kelvin.to('degC'))


# Mass
# Dwarf planet: 0.0001 to 0.1 earth masses
# Gas Giant: 10 earth masses to 13 Jupiter masses
# PuffyGiant more than 2 Jupiter masses

# Radius:
# Dwarf planet: greater than 0.03 earth radius
# Super earth:  1.25 to 2 earth radius
# Gas Giant:
# ------- if mass <= 2 Jupiter masses: less than 1 Jupiter radius
# ------- elif 2 < mass <= 13 Jupiter masses: 1 +- 0.10 Jupiter radius
# PuffyGiant: more than 1 Jupiter radius


# Gravity
# Terrestial: 0.4 to 1.6

Terrestial = [0.1, 3.5, 0.5, 1.5]
GasDwarf = [1, 20, 0, 2]

from math import sqrt, pi


class Planet:
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
            self.mass = mass
        if radius:
            self.radius = radius
        if gravity:
            self.gravity = gravity

        if not self.gravity:
            self.gravity = mass / (radius ** 2)
        if not self.radius:
            self.radius = sqrt(mass / gravity)
        if not self.mass:
            self.mass = gravity * radius ** 2

        self.density = self.mass / (self.radius ** 3)
        self.escape_velocity = sqrt(self.mass / self.radius)
        self.composition = {}


def planet_temperature(star_mass, semi_major_axis, albedo, greenhouse):
    # adapted from http://www.astro.indiana.edu/ala/PlanetTemp/index.html

    j = 3.846 * (10 ** 33) * (star_mass ** 3)
    d = semi_major_axis * 1.496 * (10 ** 33)
    a = albedo / 100
    t = greenhouse * 0.5841

    sigma = 5.6703 * (10 ** -5)
    x = sqrt((1 - a) * j / (16 * pi * sigma))

    eff_temp = sqrt(x) * (1 / sqrt(d))
    eq_temp = (eff_temp ** 4) * (1 + 3 * t / 4)
    kelvin_t = round(sqrt(sqrt(eq_temp / 0.9)))
    celsius = kelvin_t - 273

    return celsius


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

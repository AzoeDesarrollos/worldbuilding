# noinspection PyUnresolvedReferences
from math import sqrt, pi
from engine.globs.constants import EARTH_RADIUS, EARTH_MASS, EARTH_GRAVITY
from engine.globs.constants import EARTH_DENSITY, EARTH_ESCAPE_VELOCITY
from engine.globs.constants import JUPITER_MASS, JUPITER_RADIUS
from engine.globs.constants import UNIT_KG, UNIT_KM, UNIT_M_S2, UNIT_KM_S, UNIT_KM2, UNIT_KM3, UNIT_G_CM3
from math import pi, sqrt


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

    @staticmethod
    def to_excel(value):
        s = str(value)
        s = s.replace('.', ',')
        return s

    def export(self):
        x = {
            'name': self.name,
            'relatives': {
                'mass': self.to_excel(self.mass),
                'radius': self.to_excel(self.radius),
                'gravity': self.to_excel(round(self.gravity, 2)),
                'escape velocity': self.to_excel(round(self.escape_velocity, 2)),
                'density': self.to_excel(round(self.density, 2))
            },
            'absolutes': {
                'mass': '{0:.2E}'.format(self.mass * EARTH_MASS) + ' ' + UNIT_KG,
                'radius': '{0:.2E}'.format(self.radius * EARTH_RADIUS) + ' ' + UNIT_KM,
                'gravity': str(round(self.gravity * EARTH_GRAVITY, 3)) + ' ' + UNIT_M_S2,
                'escape velocity': str(round(self.escape_velocity * EARTH_ESCAPE_VELOCITY, 3)) + ' ' + UNIT_KM_S,
                'density': str(round(self.density * EARTH_DENSITY, 3)) + ' ' + UNIT_G_CM3,
                'circumference': str(round(2 * pi * (self.radius * EARTH_RADIUS), 3)) + ' ' + UNIT_KM,
                'surface area': '{0:.2E}'.format(4 * pi * ((self.radius * EARTH_RADIUS) ** 2)) + ' ' + UNIT_KM2,
                'volume': '{0:.2E}'.format((4 / 3) * pi * ((self.radius * EARTH_RADIUS) ** 3)) + ' ' + UNIT_KM3
            }
        }
        return x


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


class DwarfPlanet(Planet):
    def __init__(self, name, m, r):
        assert 0.0001 * EARTH_MASS > m > 0.1 * EARTH_MASS, "inaccurate mass"
        assert 0.03 * EARTH_RADIUS > r, "inaccurate radius"
        super().__init__(name, mass=m, radius=r)

    def __repr__(self):
        return 'DwarfPlanet'


class GasGiant(Planet):
    def __init__(self, name, m, r):
        m *= JUPITER_MASS
        r *= JUPITER_RADIUS
        assert 10 * EARTH_MASS > m > 13 * JUPITER_MASS, "inaccurate mass"

        if 2 * JUPITER_MASS:
            r = JUPITER_RADIUS

        super().__init__(name, mass=m, radius=r)

    def __repr__(self):
        return 'GasGiant'


class PuffyGiant(Planet):
    def __init__(self, name, m, r):
        m *= JUPITER_MASS
        r *= JUPITER_RADIUS
        assert m >= 2 * JUPITER_MASS, "inaccurate mass"
        assert r > JUPITER_RADIUS, "inaccurate radius"

        super().__init__(name, mass=m, radius=r)

    def __repr__(self):
        return 'PuffyGiant'

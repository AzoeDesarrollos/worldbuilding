from .general import BodyInHydrostaticEquilibrium
from math import sqrt, pi
from engine import q


class Planet(BodyInHydrostaticEquilibrium):
    mass = 0
    radius = 0
    gravity = 0
    density = 0
    escape_velocity = 0
    composition = None
    name = None
    has_name = False
    habitable = True

    def __init__(self, data):
        name = data.get('name', None)
        mass = data.get('mass', False)
        radius = data.get('radius', False)
        gravity = data.get('gravity', False)
        if not mass and not radius and not gravity:
            raise ValueError('must specify at least two values')

        if name:
            self.name = name
            self.has_name = True

        unit = data.get('unit', "earth")
        self.habitable = data['habitable'] if 'habitable' in data else False

        if mass:
            self.mass = q(mass, unit + '_masses')
        if radius:
            self.radius = q(radius, unit + '_radius')
        if gravity:
            self.gravity = q(gravity, unit + '_gravity')

        self.clase = data['class'] if 'class' in data else self.set_class(self.mass, self.radius)

        if not self.gravity:
            self.gravity = q(mass / (radius ** 2), unit + '_gravity')
        if not self.radius:
            self.radius = q(sqrt(mass / gravity), unit + '_radius')
        if not self.mass:
            self.mass = q(gravity * radius ** 2, unit + '_masses')

        self.density = self.calculate_density(self.mass.to('grams'), self.radius.to('centimeters'))
        self.volume = self.calculate_volume(self.radius.to('kilometers'))
        self.surface = self.calculate_surface_area(self.radius.to('kilometers'))
        self.circumference = self.calculate_circumference(self.radius.to('kilometers'))
        self.escape_velocity = q(sqrt(self.mass.magnitude / self.radius.magnitude), 'earth_escape')
        self.composition = {}

    @staticmethod
    def set_class(mass, radius):
        em = 'earth_mass'
        jm = 'jupiter_mass'
        if q(0.0001, em) < mass < q(0.1, em) and radius > q(0.03, 'earth_radius'):
            return 'Dwarf planet'
        if q(10, em) < mass < q(13, jm):
            return 'Gas Giant'
        if mass < q(2, jm) and radius > q(1, jm):
            return 'Puffy Giant'

    def __repr__(self):
        return self.clase+' '+str(self.mass.m)


def planet_temperature(star_mass, semi_major_axis, albedo, greenhouse=1):
    """

    :rtype: q
    """
    # adapted from http://www.astro.indiana.edu/ala/PlanetTemp/index.html

    sigma = 5.6703 * (10 ** -5)
    _l = 3.846 * (10 ** 33) * (star_mass ** 3)
    d = semi_major_axis * 1.496 * (10 ** 13)
    a = albedo / 100
    t = greenhouse * 0.5841

    x = sqrt((1 - a) * _l / (16 * pi * sigma))

    t_eff = sqrt(x) * (1 / sqrt(d))
    t_eq = (t_eff ** 4) * (1 + (3 * t / 4))
    t_sur = t_eq / 0.9
    t_kel = round(sqrt(sqrt(t_sur)))

    kelvin = q(t_kel, 'kelvin')

    return round(kelvin.to('celsius'))


# Mass
# Dwarf planet: 0.0001 to 0.1 earth masses
# Gas Giant: 10 earth masses to 13 Jupiter masses
# PuffyGiant less than 2 Jupiter masses

# Radius:
# Dwarf planet: greater than 0.03 earth radius
# Super earth:  1.25 to 2 earth radius
# Gas Giant:
# ------- if mass <= 2 Jupiter masses: 1.10 Jupiter radius or more
# ------- elif 2 < mass <= 13 Jupiter masses: 1 +- 0.10 Jupiter radius
# PuffyGiant: more than 1 Jupiter radius


# Gravity
# Terrestial: 0.4 to 1.6

# use graph with these parameters # earth units
Terrestial = [0.0, 3.5, 0.0, 1.5]
GasDwarf = [1, 20.5, 2, 0]


def temp_by_pos(star, albedo=29, greenhouse=1):
    granularidad = 10
    resultados = []
    if hasattr(star, 'mass'):
        # star_class = star.classification
        # noinspection PyUnresolvedReferences
        rel_mass = star.mass.m
        hab_inner = star.habitable_inner.m
        hab_outer = star.habitable_outer.m
    elif type(star) is list:
        # star_class = star[0]
        rel_mass = star[1]
        hab_inner = star[6]
        hab_outer = star[7]
    else:  # suponemos un dict
        # star_class = star['class']
        rel_mass = star['mass']
        hab_inner = star['inner']
        hab_outer = star['outer']

    total_dist = hab_outer - hab_inner
    unidad = total_dist / granularidad

    for i in range(granularidad):
        dist = hab_inner + unidad * i
        if dist <= hab_outer:
            t = planet_temperature(rel_mass, dist, albedo, greenhouse).magnitude
            if 13 <= t < 16:
                resultados.append(round(dist, 5))
                # resultados.append({'name': star_class, 'd': round(dist, 5), 'temp': t})

    resultados.sort(reverse=True)

    return resultados[0]

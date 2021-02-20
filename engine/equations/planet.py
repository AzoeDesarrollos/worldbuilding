from .general import BodyInHydrostaticEquilibrium
from .lagrange import get_lagrange_points
from .planetary_system import Systems
from math import sqrt, pi, pow
from .orbit import Orbit
from engine import q


class Planet(BodyInHydrostaticEquilibrium):
    celestial_type = 'planet'

    mass = 0
    radius = 0
    gravity = 0
    escape_velocity = 0
    composition = None
    name = None
    has_name = False
    habitable = True

    orbit = None
    albedo = 29
    greenhouse = 1
    temperature = q(0, 'celsius')

    atmosphere = None
    satellites = None
    lagrange_points = None
    hill_sphere = 0
    roches_limit = 0

    axial_tilt = 0
    spin = ''

    def __init__(self, data):
        name = data.get('name', None)
        mass = data.get('mass', False)
        radius = data.get('radius', False)
        gravity = data.get('gravity', False)
        if not mass and not radius and not gravity:
            raise AssertionError('must specify at least two values')

        if name:
            self.name = name
            self.has_name = True
        else:
            self.name = ''

        unit = data.get('unit', "earth")
        self.unit = unit

        self._mass = None if not mass else mass
        self._radius = None if not radius else radius
        self._gravity = None if not gravity else gravity
        self._temperature = 0

        if not self._gravity:
            self._gravity = mass / pow(radius, 2)
        if not self._radius:
            self._radius = sqrt(mass / gravity)
        if not self._mass:
            self._mass = gravity * pow(radius, 2)

        self.set_qs(unit)
        self.composition = {}
        self.atmosphere = {}
        self.habitable = self.set_habitability()
        self.clase = data['clase'] if 'clase' in data else self.set_class(self.mass, self.radius)
        self.albedo = q(data['albedo']) if 'albedo' in data else q(29)
        self.greenhouse = q(data['greenhouse']) if 'albedo' in data else q(1)

        self.satellites = []

        star = Systems.get_current_star()
        if 0 <= self.axial_tilt < 90:
            self.spin = star.spin
        elif 90 <= self.axial_tilt <= 180:
            self.spin = 'CW' if star.spin == 'CCW' else 'CCW'

    def set_qs(self, unit):
        m = unit + '_mass'
        r = unit + '_radius'

        self.mass = q(self._mass, m)
        self.radius = q(self._radius, r)
        self.gravity = q(self._gravity, unit + '_gravity')
        self.density = self.calculate_density(self.mass.to('grams'), self.radius.to('centimeters'))
        self.volume = self.calculate_volume(self.radius.to('kilometers'))
        self.surface = self.calculate_surface_area(self.radius.to('kilometers'))
        self.circumference = self.calculate_circumference(self.radius.to('kilometers'))
        self.escape_velocity = q(sqrt(self.mass.m / self.radius.m), unit + '_escape_velocity')

    def set_habitability(self):
        mass = self.mass
        radius = self.radius
        gravity = self.gravity

        habitable = q(0.1, 'earth_mass') < mass < q(3.5, 'earth_mass')
        habitable = habitable and q(0.5, 'earth_radius') < radius < q(1.5, 'earth_radius')
        habitable = habitable and q(0.4, 'earth_gravity') < gravity < q(1.6, 'earth_gravity')
        habitable = habitable and (0 <= self.axial_tilt <= 80 or 110 <= self.axial_tilt <= 180)
        return habitable

    def set_temperature(self, star_mass, semi_major_axis):
        t = planet_temperature(star_mass, semi_major_axis, self.albedo.m, self.greenhouse.m)
        self._temperature = round(t.to('earth_temperature').m)
        return t

    def set_orbit(self, star, orbital_parameters):
        orbit = Orbit(*orbital_parameters)
        self.temperature = self.set_temperature(star.mass.m, orbit.semi_minor_axis.m)
        orbit.temperature = self.temperature
        orbit.set_planet(star, self)
        self.lagrange_points = get_lagrange_points(self.orbit.semi_major_axis.m, star.mass.m, self.mass.m)
        self.hill_sphere = self.set_hill_sphere()
        return self.orbit

    def set_hill_sphere(self):
        a = self.orbit.semi_major_axis.magnitude
        mp = self.mass.to('earth_mass').magnitude
        ms = self.orbit.star.mass.to('sol_mass').magnitude
        return q(round((a * pow(mp / ms, 1 / 3) * 235), 3), 'earth_radius')

    def set_roche(self, obj_density):
        density = self.density.to('earth_density').m
        radius = self.radius.to('earth_radius').m

        roches = q(round(2.44 * radius * pow(density / obj_density, 1 / 3), 3), 'earth_radius')
        if self.roches_limit == 0 or roches < self.roches_limit:
            self.roches_limit = roches
        return self.roches_limit

    @staticmethod
    def set_class(mass, radius):
        em = 'earth_mass'
        jm = 'jupiter_mass'
        jr = 'jupiter_radius'
        if q(0.0001, em) < mass < q(0.1, em) and radius > q(0.03, 'earth_radius'):
            return 'Dwarf Planet'
        elif q(10, em) < mass < q(13, jm):
            return 'Gas Giant'
        elif mass < q(2, jm) and radius > q(1, jr):
            return 'Puffy Giant'
        else:
            raise AssertionError("couldn't class the planet")

    def set_atmosphere(self, data):
        self.atmosphere.update(data)

    def update_everything(self):
        if self.orbit is not None:
            star = self.orbit.star
            orbit = self.orbit
            a, e, i, u = orbit.a, orbit.e, orbit.i, 'au'

            self.set_qs(self.unit)
            self.set_habitability()
            self.set_orbit(star, [a, e, i, u])

    def __eq__(self, other):
        a = (self.mass.m, self.radius.m, self.clase, self.orbit, self.unit, self.name)
        b = (other.mass.m, other.radius.m, other.clase, self.orbit, other.unit, other.name)
        return a == b

    def __repr__(self):
        return self.clase + ' ' + str(self.mass.m)


def planet_temperature(star_mass, semi_major_axis, albedo, greenhouse):
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
# terrestial: 0.1 to 10 earth masses (not earth-like)
# Gas Giant: 10 earth masses to 13 Jupiter masses
# PuffyGiant less than 2 Jupiter masses

# Radius:
# Mini neptune 1.7 to 3.9 earth radius
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


def temp_by_lat(lat) -> int:
    """Devuelve la temperatura media relativa a la latitud seleccionada"""
    if type(lat) is q:
        lat = lat.m

    if lat > 90:
        lat -= 90
    elif lat < 0:
        lat = abs(lat)

    if 0 <= lat <= 10:
        return -(5 * lat / 9) + 33
    elif 11 <= lat <= 37:
        return -(9 * lat / 26) + 31
    elif 38 <= lat <= 60:
        return -(17 * lat / 24) + 44
    elif 61 <= lat <= 75:
        return round(((lat / 60) - 3), 0) * (lat - 60)
    elif 76 <= lat <= 90:
        return -lat + 45
    else:
        raise ValueError('La latitud {} no es válida'.format(lat))

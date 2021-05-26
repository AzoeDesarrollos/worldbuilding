from .general import BodyInHydrostaticEquilibrium, Ring
from .lagrange import get_lagrange_points
from .planetary_system import Systems
from math import pi, tan
from datetime import datetime
from pygame import Color
from .orbit import Orbit
from engine import q, d


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

    sprite = None

    duracion_ciclo = 0
    radio_circulo = 0

    sky_color = None

    def __init__(self, data):
        mass = data.get('mass', False)
        radius = data.get('radius', False)
        gravity = data.get('gravity', False)
        if not mass and not radius and not gravity:
            raise AssertionError('must specify at least two values')

        name = data.get('name', None)
        if name is not None:
            self.name = name
            self.has_name = True

        unit = data.get('unit', "earth")
        self.unit = unit
        self.idx = data.get('idx', 0)

        self._mass = None if not mass else mass
        self._radius = None if not radius else radius
        self._gravity = None if not gravity else gravity
        self._temperature = d(0)

        if not self._gravity:
            self._gravity = d(mass) / (d(radius) ** 2)
        if not self._radius:
            self._radius = (d(mass) / d(gravity)).sqrt()
        if not self._mass:
            self._mass = d(gravity) * (d(radius) ** 2)

        self.set_qs(unit)
        if 'composition' in data and data['composition'] is not None:
            self.composition = {
                'water ice': data['composition'].get('water ice', 0),
                'silicates': data['composition'].get('silicates', 0),
                'iron': data['composition'].get('iron', 0),
                'helium': data['composition'].get('helium', 0),
                'hydrogen': data['composition'].get('hydrogen', 0),
            }

        self.atmosphere = {}
        self.habitable = self.set_habitability()
        self.clase = data['clase'] if 'clase' in data else self.set_class(self.mass, self.radius)
        self.albedo = q(data['albedo']) if 'albedo' in data else q(d(29))
        self.greenhouse = q(data['greenhouse']) if 'albedo' in data else q(d(1))
        self.axial_tilt = q(data['tilt']) if 'tilt' in data else q(d(0))

        self.satellites = []

        star = Systems.get_current_star()
        if d(0) <= self.axial_tilt < d(90):
            self.spin = star.spin
        elif d(90) <= self.axial_tilt <= d(180):
            self.spin = 'CW' if star.spin == 'CCW' else 'CCW'

        # ID values make each planet unique, even if they have the same characteristics.
        now = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])
        self.id = data['id'] if 'id' in data else now

        self.system_id = data.get('system', None)

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
        self.escape_velocity = q((self.mass.m / self.radius.m).sqrt(), unit + '_escape_velocity')

    def set_habitability(self):
        mass = self.mass
        radius = self.radius
        gravity = self.gravity

        habitable = q(d(0.1), 'earth_mass') < mass < q(d(3.5), 'earth_mass')
        habitable = habitable and q(d(0.5), 'earth_radius') < radius < q(d(1.5), 'earth_radius')
        habitable = habitable and q(d(0.4), 'earth_gravity') < gravity < q(d(1.6), 'earth_gravity')
        habitable = habitable and (d(0) <= self.axial_tilt <= d(80) or d(110) <= self.axial_tilt <= d(180))
        return habitable

    def set_temperature(self, star_mass, semi_major_axis):
        t = planet_temperature(star_mass, semi_major_axis, self.albedo.m, self.greenhouse.m)
        self._temperature = round(t.to('earth_temperature').m)
        return t

    def set_orbit(self, star, orbital_parameters):
        orbit = Orbit(*orbital_parameters)
        self.temperature = self.set_temperature(star.mass.m, orbit.semi_minor_axis.m)
        orbit.temperature = self.temperature
        orbit.set_astrobody(star, self)
        self.lagrange_points = get_lagrange_points(self.orbit.semi_major_axis.m, star.mass.m, self.mass.m)
        self.hill_sphere = self.set_hill_sphere()
        if star.letter is None:
            self.sky_color = self.set_sky_color(star)
        return self.orbit

    def set_hill_sphere(self):
        a = self.orbit.semi_major_axis.to('au').magnitude
        mp = self.mass.to('earth_mass').magnitude
        ms = self.orbit.star.mass.to('sol_mass').magnitude
        return q(round((a * ((mp / ms) ** d(1/3))), 3), 'earth_hill_sphere').to('earth_radius')

    def set_roche(self, obj_density):
        density = self.density.to('earth_density').m
        radius = self.radius.to('earth_radius').m

        roches = q(round(d('2.44') * radius * (density / obj_density ** d('1/3')), 3), 'earth_radius')
        if self.roches_limit == 0 or roches < self.roches_limit:
            self.roches_limit = roches
        return self.roches_limit

    def set_precession_cycle(self):
        tilt = self.axial_tilt
        self.duracion_ciclo = q(d('-7.095217823187172') * (tilt ** d(2)) + d('1277.139208333333') * tilt, 'years')
        self.radio_circulo = tan(tilt) * self.radius.to('km')

    def create_ring(self, asteroid):
        mass = asteroid.mass.to('ring_mass').m
        density = asteroid.density.to('earth_density').m
        vol = mass / density

        outer_limit = self.roches_limit.to('km')
        inner_limit = q(self._radius + d(10000), 'km')
        # "10K" debería ser seteado por el Atmosphere Panel, porque es el fin de la atmósfera.
        wideness = outer_limit - inner_limit

        ro = d(outer_limit.to('earth_radius').m)
        ri = d(inner_limit.to('earth_radius').m)
        ra = (d(vol) / (d(4 / 3) * d(pi))) ** 3

        thickness = q(d(4 / 3) * ((ra ** d(3)) / ((ro ** d(2)) - (ri ** d(2)))), 'km').to('m')

        return Ring(self, inner_limit, outer_limit, wideness, thickness)

    @staticmethod
    def set_sky_color(star):
        p = star.peak_light.frequency

        color = None
        if d('43.4941208') <= p <= d('1664.635167'):
            if d('43.4941208') <= p <= d('290'):
                color = Color(73, 96, 251)
            elif d('290') <= p <= d('300'):
                color = Color(88, 104, 251)
            elif d('300') <= p <= d('310'):
                color = Color(91, 112, 251)
            elif d('310') <= p <= d('320'):
                color = Color(97, 117, 251)
            elif d('320') <= p <= d('330'):
                color = Color(104, 124, 251)
            elif d('330') <= p <= d('340'):
                color = Color(112, 131, 251)
            elif d('340') <= p <= d('350'):
                color = Color(117, 136, 251)
            elif d('350') <= p <= d('360'):
                color = Color(125, 143, 252)
            elif d('360') <= p <= d('370'):
                color = Color(131, 148, 252)
            elif d('370') <= p <= d('380'):
                color = Color(136, 152, 252)
            elif d('380') <= p <= d('390'):
                color = Color(141, 157, 252)
            elif d('390') <= p <= d('400'):
                color = Color(146, 162, 252)
            elif d('400') <= p <= d('410'):
                color = Color(149, 164, 252)
            elif d('410') <= p <= d('420'):
                color = Color(155, 168, 252)
            elif d('420') <= p <= d('430'):
                color = Color(160, 174, 252)
            elif d('430') <= p <= d('440'):
                color = Color(163, 176, 252)
            elif d('440') <= p <= d('450'):
                color = Color(166, 180, 252)
            elif d('450') <= p <= d('460'):
                color = Color(171, 183, 253)
            elif d('460') <= p <= d('470'):
                color = Color(174, 186, 253)
            elif d('470') <= p <= d('480'):
                color = Color(178, 189, 253)
            elif d('480') <= p <= d('490'):
                color = Color(182, 192, 253)
            elif d('490') <= p <= d('500'):
                color = Color(185, 195, 253)
            elif d('500') <= p <= d('510'):
                color = Color(188, 198, 253)
            elif d('510') <= p <= d('520'):
                color = Color(191, 200, 253)
            elif d('520') <= p <= d('530'):
                color = Color(194, 203, 253)
            elif d('530') <= p <= d('540'):
                color = Color(197, 205, 253)
            elif d('540') <= p <= d('550'):
                color = Color(200, 208, 253)
            elif d('550') <= p <= d('560'):
                color = Color(203, 210, 253)
            elif d('560') <= p <= d('570'):
                color = Color(205, 212, 253)
            elif d('570') <= p <= d('580'):
                color = Color(207, 214, 253)
            elif d('580') <= p <= d('590'):
                color = Color(209, 216, 254)
            elif d('590') <= p <= d('600'):
                color = Color(212, 218, 254)
            elif d('600') <= p <= d('610'):
                color = Color(214, 220, 254)
            elif d('610') <= p <= d('620'):
                color = Color(216, 222, 254)
            elif d('620') <= p <= d('630'):
                color = Color(218, 223, 254)
            elif d('630') <= p <= d('640'):
                color = Color(220, 225, 254)
            elif d('640') <= p <= d('650'):
                color = Color(222, 227, 254)
            elif d('650') <= p <= d('660'):
                color = Color(224, 228, 254)
            elif d('660') <= p <= d('670'):
                color = Color(226, 230, 254)
            elif d('670') <= p <= d('680'):
                color = Color(229, 233, 254)
            elif d('680') <= p <= d('690'):
                color = Color(230, 233, 254)
            elif d('690') <= p <= d('700'):
                color = Color(231, 234, 254)
            elif d('700') <= p <= d('710'):
                color = Color(233, 236, 254)
            elif d('710') <= p <= d('720'):
                color = Color(235, 237, 254)
            elif d('720') <= p <= d('730'):
                color = Color(236, 238, 254)
            elif d('730') <= p <= d('740'):
                color = Color(240, 243, 255)
            elif d('740') <= p <= d('750'):
                color = Color(244, 246, 255)
            elif d('750') <= p <= d('760'):
                color = Color(248, 250, 255)
            elif d('760') <= p <= d('770'):
                color = Color(254, 255, 255)
            elif d('770') <= p <= d('780'):
                color = Color(253, 249, 233)
            elif d('780') <= p <= d('790'):
                color = Color(251, 241, 202)
            elif d('790') <= p <= d('800'):
                color = Color(249, 232, 168)
            elif d('800') <= p <= d('810'):
                color = Color(247, 224, 138)
            elif d('810') <= p <= d('820'):
                color = Color(244, 215, 106)
            elif d('820') <= p <= d('830'):
                color = Color(242, 207, 81)
            elif d('830') <= p <= d('840'):
                color = Color(240, 198, 57)
            elif d('840') <= p <= d('850'):
                color = Color(239, 191, 45)
            elif d('850') <= p <= d('860'):
                color = Color(239, 174, 45)

        return color

    @staticmethod
    def set_class(mass, radius):
        em = 'earth_mass'
        jm = 'jupiter_mass'
        jr = 'jupiter_radius'
        if q(d('0.0001'), em) < mass < q(d('0.1'), em) and radius > q(d('0.03'), 'earth_radius'):
            return 'Dwarf Planet'
        elif q(d(10), em) < mass < q(d(13), jm):
            return 'Gas Giant'
        elif mass < q(d(2), jm) and radius > q(d(1), jr):
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
        if not hasattr(other, 'clase') or not hasattr(other, 'unit'):
            return False
        b = (other.mass.m, other.radius.m, other.clase, self.orbit, other.unit, other.name)
        return a == b

    def __repr__(self):
        return self.clase + ' ' + str(self.mass.m)

    def __str__(self):
        return "{} #{}".format(self.clase, self.idx)


def planet_temperature(star_mass: d, semi_major_axis: d, albedo: d, greenhouse: d):
    """
    :rtype: q
    """
    # adapted from http://www.astro.indiana.edu/ala/PlanetTemp/index.html

    sigma = d('5.6703') * d(10 ** -5)
    _l = d('3.846') * d(10 ** 33) * d(star_mass ** 3)
    k = semi_major_axis * d('1.496') * d(10 ** 13)
    a = d(albedo / 100)
    t = greenhouse * d('0.5841')

    x = ((1 - a) * _l / d(16 * d(pi) * sigma)).sqrt()

    t_eff = x.sqrt() * (1 / k.sqrt())
    t_eq = (t_eff ** d(4)) * (d(1) + (d(3) * t / d(4)))
    t_sur = t_eq / d('0.9')
    t_kel = int((t_sur.sqrt().sqrt()).quantize(d('1')))

    kelvin = q(t_kel, 'kelvin')

    return round(kelvin.to('celsius'))


# Terrestial Graph parameters
Terrestial = [d('0.0'), d('3.5'), d('0.0'), d('1.5')]
GasDwarf = [d('1'), d('20.5'), d('2'), d('0')]


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


def temp_by_lat(lat) -> q:
    """Devuelve la temperatura media relativa a la latitud seleccionada
    
    :rtype: q
    """
    if type(lat) is q:
        lat = lat.m

    if lat > 90:
        lat -= 90
    elif lat < 0:
        lat = abs(lat)

    temp = None
    if 0 <= lat <= 10:
        temp = -(5 * lat / 9) + 33

    elif 11 <= lat <= 37:
        temp = -(9 * lat / 26) + 31

    elif 38 <= lat <= 60:
        temp = -(17 * lat / 24) + 44

    elif 61 <= lat <= 75:
        a = ((lat / 60) - 3)
        b = (lat - 60)
        temp = a * b if b != 0 else 0.0

    elif 76 <= lat <= 90:
        temp = -lat + 45

    if temp is not None:
        return q(round(temp, 2), 'celsius')
    else:
        raise ValueError('La latitud "{}" no es válida'.format(lat))

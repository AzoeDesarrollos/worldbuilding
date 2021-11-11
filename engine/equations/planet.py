from .general import BodyInHydrostaticEquilibrium, Ring
from engine import molecular_weight, q, albedos
from .orbit import PlanetOrbit, SatelliteOrbit
from engine.backend.util import generate_id
from .lagrange import get_lagrange_points
from math import sqrt, pi, pow, tan
from pygame import Color


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
    _greenhouse = 1
    temperature = q(0, 'celsius')

    atmosphere = None

    lagrange_points = None
    hill_sphere = 0
    roches_limit: q = 0

    _tilt = 'Not set'
    spin = 'N/A'

    sprite = None

    duracion_ciclo_precession = 0
    radio_circulo_precession = 0

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
        self._temperature = 0

        if not self._gravity:
            self._gravity = mass / pow(radius, 2)
        if not self._radius:
            self._radius = sqrt(mass / gravity)
        if not self._mass:
            self._mass = gravity * pow(radius, 2)

        rocky = {'silicates', 'iron', 'water ice'}

        self.set_qs(unit)
        if 'composition' in data and data['composition'] is not None:
            if len(data['composition'].keys() & rocky):
                self.composition = {
                    'water ice': data['composition'].get('water ice', 0),
                    'silicates': data['composition'].get('silicates', 0),
                    'iron': data['composition'].get('iron', 0)
                }
                self.planet_type = 'rocky'

            else:
                self.composition = {
                    'helium': data['composition'].get('helium', 0),
                    'hydrogen': data['composition'].get('hydrogen', 0)
                }
                self.planet_type = 'gaseous'

        else:
            self.planet_type = 'gaseous'

        self.atmosphere = {}
        if len(data.get('atmosphere', [])):
            self.set_atmosphere(data['atmosphere'])
        else:
            self._greenhouse = 1
        self.albedo = q(data['albedo'])
        self.clase = data['clase'] if 'clase' in data else self.set_class(self.mass, self.radius)
        self.relative_size = 'Dwarf' if 'Dwarf' in self.clase else 'Giant' if 'Giant' in self.clase else 'Medium'
        self.tilt = data['tilt'] if 'tilt' in data else 0

        self.satellites = []

        # ID values make each planet unique, even if they have the same characteristics.
        self.id = data['id'] if 'id' in data else generate_id()

        self.system_id = data.get('system', None)

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        if 0 <= value < 90:
            self.spin = 'prograde'
        elif 90 <= value <= 180:
            self.spin = 'retrograde'
        self._tilt = q(value, 'degree')
        self.habitable = self.set_habitability()

    @property
    def greenhouse(self):
        return q(self.global_warming())

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
        habitable = habitable and (0 <= self.tilt <= 80 or 110 <= self.tilt <= 180)

        return habitable

    def set_temperature(self, star_mass, semi_major_axis):
        t = planet_temperature(star_mass, semi_major_axis, self.albedo.m, self.greenhouse.m)
        self._temperature = round(t.to('earth_temperature').m)
        self.temperature = q(self._temperature, 'earth_temperature').to('celsius')
        return t

    def get_temperature(self):
        star = self.orbit.star
        orbit = self.orbit.a
        t = planet_temperature(star.mass.m, orbit.m, self.albedo, self.greenhouse.m)
        return t

    def set_orbit(self, star, orbital_parameters):
        if star.celestial_type in ('star', 'system'):
            self.orbit = PlanetOrbit(star, *orbital_parameters)
            temp = star.temperature_mass
        else:
            self.orbit = SatelliteOrbit(*orbital_parameters)
            temp = star.parent.temperature_mass

        self.temperature = self.set_temperature(temp, self.orbit.semi_minor_axis.m)
        self.orbit.set_astrobody(star, self)
        if hasattr(star, 'letter') and star.letter == 'P':
            self.lagrange_points = get_lagrange_points(self.orbit.a.m, star.shared_mass.m, self.mass.m)
        else:
            self.lagrange_points = get_lagrange_points(self.orbit.a.m, star.mass.m, self.mass.m)

        self.hill_sphere = self.set_hill_sphere()
        if star.celestial_type == 'star':
            self.sky_color = self.set_sky_color(star)
        return self.orbit

    def set_hill_sphere(self):
        a = self.orbit.semi_major_axis.to('au').magnitude
        mp = self.mass.to('earth_mass').magnitude
        star = self.orbit.star
        if hasattr(star, 'letter') and star.letter == 'P':
            ms = star.shared_mass.to('sol_mass').m
        else:
            ms = star.mass.to('sol_mass').magnitude
        return q(round((a * pow(mp / ms, 1 / 3)), 3), 'earth_hill_sphere').to('earth_radius')

    def unset_orbit(self):
        del self.orbit
        self.orbit = None
        self.temperature = q(0, 'celsius')
        self.hill_sphere = 0
        self.roches_limit = 0
        self.sky_color = None
        self.lagrange_points = None
        for satellite in self.satellites:
            satellite.unset_orbit()

    def set_roche(self, obj_density):
        density = self.density.to('earth_density').m
        radius = self.radius.to('earth_radius').m

        roches = q(round(2.44 * radius * pow(density / obj_density, 1 / 3), 3), 'earth_radius')
        if self.roches_limit == 0 or roches < self.roches_limit:
            self.roches_limit = roches
        return self.roches_limit

    def set_precession_cycle(self):
        tilt = self.tilt
        self.duracion_ciclo_precession = q(-7.095217823187172 * pow(tilt, 2) + 1277.139208333333 * tilt, 'years')
        self.radio_circulo_precession = tan(tilt) * self.radius.to('km')

    def create_ring(self, asteroid):
        mass = asteroid.mass.to('ring_mass').m
        density = asteroid.density.to('earth_density').m
        vol = mass / density

        outer_limit = self.roches_limit.to('km')
        inner_limit = q(self._radius + 10000, 'km')
        # "10K" debería ser seteado por el Atmosphere Panel, porque es el fin de la atmósfera.
        wideness = outer_limit - inner_limit

        ro = outer_limit.to('earth_radius').m
        ri = inner_limit.to('earth_radius').m
        ra = pow((vol / (4 / 3 * pi)), 3)

        thickness = q(4 / 3 * (pow(ra, 3) / (pow(ro, 2) - pow(ri, 2))), 'km').to('m')

        return Ring(self, inner_limit, outer_limit, wideness, thickness)

    @staticmethod
    def set_sky_color(star):
        p = star.peak_light.frequency.m

        color = None
        if 43.4941208 <= p <= 1664.635167:
            if 43.4941208 <= p <= 290:
                color = Color(73, 96, 251)
            elif 290 <= p <= 300:
                color = Color(88, 104, 251)
            elif 300 <= p <= 310:
                color = Color(91, 112, 251)
            elif 310 <= p <= 320:
                color = Color(97, 117, 251)
            elif 320 <= p <= 330:
                color = Color(104, 124, 251)
            elif 330 <= p <= 340:
                color = Color(112, 131, 251)
            elif 340 <= p <= 350:
                color = Color(117, 136, 251)
            elif 350 <= p <= 360:
                color = Color(125, 143, 252)
            elif 360 <= p <= 370:
                color = Color(131, 148, 252)
            elif 370 <= p <= 380:
                color = Color(136, 152, 252)
            elif 380 <= p <= 390:
                color = Color(141, 157, 252)
            elif 390 <= p <= 400:
                color = Color(146, 162, 252)
            elif 400 <= p <= 410:
                color = Color(149, 164, 252)
            elif 410 <= p <= 420:
                color = Color(155, 168, 252)
            elif 420 <= p <= 430:
                color = Color(160, 174, 252)
            elif 430 <= p <= 440:
                color = Color(163, 176, 252)
            elif 440 <= p <= 450:
                color = Color(166, 180, 252)
            elif 450 <= p <= 460:
                color = Color(171, 183, 253)
            elif 460 <= p <= 470:
                color = Color(174, 186, 253)
            elif 470 <= p <= 480:
                color = Color(178, 189, 253)
            elif 480 <= p <= 490:
                color = Color(182, 192, 253)
            elif 490 <= p <= 500:
                color = Color(185, 195, 253)
            elif 500 <= p <= 510:
                color = Color(188, 198, 253)
            elif 510 <= p <= 520:
                color = Color(191, 200, 253)
            elif 520 <= p <= 530:
                color = Color(194, 203, 253)
            elif 530 <= p <= 540:
                color = Color(197, 205, 253)
            elif 540 <= p <= 550:
                color = Color(200, 208, 253)
            elif 550 <= p <= 560:
                color = Color(203, 210, 253)
            elif 560 <= p <= 570:
                color = Color(205, 212, 253)
            elif 570 <= p <= 580:
                color = Color(207, 214, 253)
            elif 580 <= p <= 590:
                color = Color(209, 216, 254)
            elif 590 <= p <= 600:
                color = Color(212, 218, 254)
            elif 600 <= p <= 610:
                color = Color(214, 220, 254)
            elif 610 <= p <= 620:
                color = Color(216, 222, 254)
            elif 620 <= p <= 630:
                color = Color(218, 223, 254)
            elif 630 <= p <= 640:
                color = Color(220, 225, 254)
            elif 640 <= p <= 650:
                color = Color(222, 227, 254)
            elif 650 <= p <= 660:
                color = Color(224, 228, 254)
            elif 660 <= p <= 670:
                color = Color(226, 230, 254)
            elif 670 <= p <= 680:
                color = Color(229, 233, 254)
            elif 680 <= p <= 690:
                color = Color(230, 233, 254)
            elif 690 <= p <= 700:
                color = Color(231, 234, 254)
            elif 700 <= p <= 710:
                color = Color(233, 236, 254)
            elif 710 <= p <= 720:
                color = Color(235, 237, 254)
            elif 720 <= p <= 730:
                color = Color(236, 238, 254)
            elif 730 <= p <= 740:
                color = Color(240, 243, 255)
            elif 740 <= p <= 750:
                color = Color(244, 246, 255)
            elif 750 <= p <= 760:
                color = Color(248, 250, 255)
            elif 760 <= p <= 770:
                color = Color(254, 255, 255)
            elif 770 <= p <= 780:
                color = Color(253, 249, 233)
            elif 780 <= p <= 790:
                color = Color(251, 241, 202)
            elif 790 <= p <= 800:
                color = Color(249, 232, 168)
            elif 800 <= p <= 810:
                color = Color(247, 224, 138)
            elif 810 <= p <= 820:
                color = Color(244, 215, 106)
            elif 820 <= p <= 830:
                color = Color(242, 207, 81)
            elif 830 <= p <= 840:
                color = Color(240, 198, 57)
            elif 840 <= p <= 850:
                color = Color(239, 191, 45)
            elif 850 <= p <= 860:
                color = Color(239, 174, 45)

        return color

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
        self.update_everything()

    def global_warming(self):
        gases = ['CO2', 'H2O', 'CH4', 'N2O', 'O3']  # Greenhouse gases
        effect = 0
        for symbol in gases:
            gas = molecular_weight[symbol]
            if symbol in self.atmosphere:
                effect += (self.atmosphere[symbol] / 100) * gas['GWP']
        return effect

    def update_everything(self):
        if self.orbit is not None:
            star = self.orbit.star
            orbit = self.orbit
            a, e, i = orbit.a, orbit.e, orbit.i
            loan = orbit.longitude_of_the_ascending_node
            aop = orbit.argument_of_periapsis

            self.set_qs(self.unit)
            self.set_habitability()
            self.set_orbit(star, [a, e, i, loan, aop])

    def __eq__(self, other):
        a = (self.mass.m, self.radius.m, self.clase, self.unit, self.name, self.id)
        if not hasattr(other, 'clase') or not hasattr(other, 'unit'):
            return False
        b = (other.mass.m, other.radius.m, other.clase, other.unit, other.name, other.id)
        return a == b

    def __repr__(self):
        return self.clase + ' ' + str(self.mass.m)

    def __str__(self):
        if self.has_name:
            return self.name
        else:
            return "{} #{}".format(self.clase, self.idx)

    def __getitem__(self, item):
        if type(item) is int:
            if item == 0:
                return self
            raise StopIteration()


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


# Terrestial Graph parameters
Terrestial = [0.0, 3.5, 0.0, 1.5]
GasDwarf = [1, 20.5, 2, 0]


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


def albedo_by_lat(material: str, lat: float) -> float:
    """Devuelve el Albedo de un material según la latitud"""
    y1 = albedos[material]['low']
    y2 = albedos[material]['high']

    dx = 90
    m = (y2 - y1) / -dx
    n = y1 - m * dx

    return round(m * lat + n, 2)

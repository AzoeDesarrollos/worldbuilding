from .general import BodyInHydrostaticEquilibrium
from bisect import bisect_right
from datetime import datetime
from random import choice
from pygame import Color
from engine import q, d


class Star(BodyInHydrostaticEquilibrium):
    celestial_type = 'star'

    mass = 1
    radius = 1
    luminosity = 1
    lifetime = 1
    temperature = 1
    classification = 'G'
    name = None
    has_name = False

    habitable_inner = 0
    habitable_outer = 0
    inner_boundry = 0
    outer_boundry = 0
    frost_line = 0

    sprite = None
    letter = None
    idx = None

    _lifetime = 0
    _temperature = 0
    _habitable_inner = 0
    _habitable_outer = 0
    _inner_boundry = 0
    _outer_boundry = 0
    _frost_line = 0

    _spin = ''

    def __init__(self, data):
        mass = data.get('mass', False)
        luminosity = data.get('luminosity', False)
        assert mass or luminosity, 'Must specify at least mass or luminosity.'

        name = data.get('name', None)
        if name is not None:
            self.name = name
            self.has_name = True

        self.idx = data.get('idx', 0)

        if mass:
            self._mass = d(mass)
        elif luminosity:
            self._luminosity = d(luminosity)

        if not mass and luminosity:
            self._mass = d(luminosity) ** (d('1') / d('3.5'))

        elif not luminosity and mass:
            self._luminosity = d((d(mass) ** d('3.5')))

        self._spin = choice(['clockwise', 'counter-clockwise']) if 'spin' not in data else data['spin']
        self._radius = self.set_radius()
        self.set_derivated_characteristics()
        self.set_qs()
        invalid_mass_warning = 'Invalid Mass: Stellar mass must be between 0.08 and 120 solar masses.'
        assert d('0.08') <= self.mass.m < d('120'), invalid_mass_warning

        self.classification = self.stellar_classification()
        self.cls = self.classification
        self.color = self.true_color(self.temperature)
        self.peak_light = LightWave(self.peak_lightwave_frequency(self.temperature.m))

        # ID values make each star unique, even if they have the same mass and name.
        now = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])
        self.id = data['id'] if 'id' in data else now

    @property
    def spin(self):
        if self._spin == 'clockwise':
            return 'clockwise'
        elif self._spin == 'counter-clockwise':
            return 'counter-clockwise'

    def set_radius(self):
        radius = '1'
        if self._mass < d('1'):
            radius = self._mass ** d('0.8')
        elif self._mass > d('1'):
            radius = self._mass ** d('0.5')
        return d(radius)

    def set_derivated_characteristics(self):
        self._lifetime = self._mass / self._luminosity
        self._temperature = (self._luminosity / (self._radius ** d('2'))) ** (d('1') / d('4'))
        self._habitable_inner = round(d((self._luminosity / d('1.1')).sqrt()), 3)
        self._habitable_outer = round(d((self._luminosity / d('0.53')).sqrt()), 3)
        self._inner_boundry = self._mass * d('0.01')
        self._outer_boundry = self._mass * d('40')
        self._frost_line = round(d('4.85') * self._luminosity.sqrt(), 3)

    def set_qs(self):
        self.mass = q(self._mass, 'sol_mass')
        self.luminosity = q(self._luminosity, 'sol_luminosity')
        self.radius = q(self._radius, 'sol_radius')
        self.lifetime = q(self._lifetime, 'sol_lifetime')
        self.temperature = q(self._temperature, 'sol_temperature')
        self.volume = q(self.calculate_volume(self.radius.to('km').m), 'km^3')
        self.density = q(self.calculate_density(self.mass.to('g').m, self.radius.to('cm').m), 'g/cm^3')
        self.circumference = q(self.calculate_circumference(self.radius.to('km').m), 'km')
        self.surface = q(self.calculate_surface_area(self.radius.to('km').m), 'km^2')
        self.habitable_inner = q(self._habitable_inner, 'au')
        self.habitable_outer = q(self._habitable_outer, 'au')
        self.inner_boundry = q(self._inner_boundry, 'au')
        self.outer_boundry = q(self._outer_boundry, 'au')
        self.frost_line = q(self._frost_line, 'au')

    def stellar_classification(self):
        masses = [d('0.08'), d('0.45'), d('0.8'), d('1.04'), d('1.4'), d('2.1'), d('16')]
        classes = ["M", "K", "G", "F", "A", "B", "O"]
        idx = bisect_right(masses, self._mass)
        return classes[idx - 1:idx][0]

    @staticmethod
    def true_color(temperature):
        t = temperature.to('kelvin').m.quantize(d('1'))

        kelvin = [d(2660), d(3120), d(3230), d(3360), d(3500), d(3680), d(3920), d(4410), d(4780), d(5240), d(5490),
                  d(5610), d(5780), d(5920), d(6200), d(6540), d(6930), d(7240), d(8190), d(8620), d(9730), d(10800),
                  d(12400), d(13400), d(14500), d(15400), d(16400), d(18800), d(22100), d(24200), d(27000), d(30000),
                  d(31900), d(35000), d(38000)]

        hexs = ['#ffad51', '#ffbd71', '#ffc177', '#ffc57f', '#ffc987', '#ffcd91', '#ffd39d', '#ffddb4', '#ffe4c4',
                '#ffead5', '#ffeedd', '#ffefe1', '#fff1e7', '#fff3eb', '#fff6f3', '#fff9fc', '#f9f6ff', '#f2f2ff',
                '#e3e8ff', '#dde4ff', '#d2dcff', '#cad6ff', '#c1d0ff', '#bccdff', '#b9caff', '#b6c8ff', '#b4c6ff',
                '#afc2ff', '#abbfff', '#a9bdff', '#a7bcff', '#a5baff', '#a4baff', '#a3b8ff', '#a2b8ff']

        if t in kelvin:
            return Color(hexs[kelvin.index(t)])

        elif t < kelvin[0]:
            # "extrapolación" lineal positiva
            despues = 1
            antes = 0
        elif t > kelvin[-1]:
            # "extrapolación" lineal nagativa
            despues = -1
            antes = -2
        else:
            # interpolación lineal
            despues = bisect_right(kelvin, t)
            antes = despues - 1

        x1 = kelvin[antes]
        x2 = kelvin[despues]

        y1 = Color((hexs[antes]))
        y2 = Color((hexs[despues]))

        diff_x = x2 - x1
        ar = (y2.r - y1.r) / diff_x
        ag = (y2.g - y1.g) / diff_x
        ab = (y2.b - y1.b) / diff_x

        br = y1.r - ar * x1
        bg = y1.g - ag * x1
        bb = y1.b - ab * x1

        x = t - x1 if t > x1 else x1 - t

        def cap(number):
            number = number.quantize(d('1'))
            if number >= d('255'):
                return 255
            elif number <= d('0'):
                v = abs(number)
                return cap(v)
            else:
                return int(number)

        r = cap((ar * x + br))
        g = cap((ag * x + bg))
        b = cap((ab * x + bb))

        color = Color(r, g, b)
        return color

    @staticmethod
    def peak_lightwave_frequency(temperature):
        return d('0.0028977729') / (temperature * d('5778')) * d('1000000000')

    def validate_orbit(self, orbit):
        return self._inner_boundry < orbit < self._outer_boundry

    def update_everything(self):
        if self.mass != self._mass:
            self._mass = self.mass.m
            self._luminosity = self._mass ** d('3.5')

        elif self.luminosity != self._luminosity:
            self._luminosity = self.luminosity.m
            self._mass = self._luminosity ** (d('1') / d('3.5'))

        self._radius = self.set_radius()
        self.set_derivated_characteristics()
        self.set_qs()

        invalid_mass_warning = 'Invalid Mass: Stellar mass must be between 0.08 and 120 solar masses.'
        assert d('0.08') <= self.mass.m < d('120'), invalid_mass_warning

        self.classification = self.stellar_classification()
        self.cls = self.classification
        self.color = self.true_color(self.temperature)

    def __str__(self):
        if self.has_name:
            return self.name
        else:
            return "{}-Star #{}".format(self.cls, self.idx)

    def __repr__(self):
        if self.has_name is False:
            return "Star " + self.name + ' {}'.format(self.mass.m)
        else:
            return self.name

    def __eq__(self, other):
        test = all([self.mass.m == other.mass.m, self.name == other.name, self.id == other.id])
        return test

    def __hash__(self):
        return hash((self.mass.m, self.name, self.id))


class LightWave:
    _color = None
    frequency = None

    def __init__(self, frequency):
        self.frequency = frequency
        self.spectrum = self.radiation_type(frequency)

    @staticmethod
    def visible_color(frequency: d):
        color = None
        if d('43.4941208') < frequency < d('1664.635167'):
            if d('43.4941208') <= frequency <= d(400):
                color = Color(0, 0, 0)
            elif d(400) <= frequency <= d(410):
                color = Color(37, 12, 83)
            elif d(410) <= frequency <= d(420):
                color = Color(66, 28, 163)
            elif d(420) <= frequency <= d(430):
                color = Color(96, 37, 247)
            elif d(430) <= frequency <= d(440):
                color = Color(78, 55, 232)
            elif d(440) <= frequency <= d(450):
                color = Color(63, 73, 217)
            elif d(450) <= frequency <= d(460):
                color = Color(58, 92, 203)
            elif d(460) <= frequency <= d(470):
                color = Color(63, 111, 188)
            elif d(470) <= frequency <= d(480):
                color = Color(68, 120, 173)
            elif d(480) <= frequency <= d(490):
                color = Color(73, 129, 157)
            elif d(490) <= frequency <= d(500):
                color = Color(78, 138, 143)
            elif d(500) <= frequency <= d(510):
                color = Color(83, 147, 128)
            elif d(510) <= frequency <= d(520):
                color = Color(88, 156, 114)
            elif d(520) <= frequency <= d(530):
                color = Color(93, 165, 100)
            elif d(530) <= frequency <= d(540):
                color = Color(99, 175, 87)
            elif d(540) <= frequency <= d(550):
                color = Color(115, 190, 76)
            elif d(550) <= frequency <= d(560):
                color = Color(141, 206, 68)
            elif d(560) <= frequency <= d(570):
                color = Color(175, 222, 62)
            elif d(570) <= frequency <= d(580):
                color = Color(214, 238, 59)
            elif d(580) <= frequency <= d(590):
                color = Color(255, 255, 60)
            elif d(590) <= frequency <= d(600):
                color = Color(234, 169, 40)
            elif d(600) <= frequency <= d(610):
                color = Color(223, 86, 15)
            elif d(610) <= frequency <= d(620):
                color = Color(219, 0, 0)
            elif d(620) <= frequency <= d(630):
                color = Color(197, 0, 0)
            elif d(630) <= frequency <= d(640):
                color = Color(174, 0, 0)
            elif d(640) <= frequency <= d(650):
                color = Color(152, 0, 0)
            elif d(650) <= frequency <= d(660):
                color = Color(130, 0, 0)
            elif d(660) <= frequency <= d(670):
                color = Color(109, 0, 0)
            elif d(670) <= frequency <= d(680):
                color = Color(87, 0, 0)
            elif d(680) <= frequency <= d(690):
                color = Color(67, 0, 0)
            elif d(690) <= frequency <= d(700):
                color = Color(47, 0, 0)
            elif d(700) <= frequency <= d(710):
                color = Color(27, 0, 0)
            elif d(710) <= frequency <= d('1664.635167'):
                color = Color(0, 0, 0)

        return color

    def radiation_type(self, frequency):
        if frequency < d(400):
            return "ULTRA-VIOLET"
        elif frequency > d(710):
            return "INFRARED"
        else:
            self._color = self.visible_color(frequency)
            return "VISIBLE"

    @property
    def color(self):
        return self._color

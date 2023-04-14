from engine.backend import decimal_round, generate_id, q, turn_into_roman
from .general import BodyInHydrostaticEquilibrium
from bisect import bisect_right
from math import sqrt, pow
from random import choice
from pygame import Color


class Star(BodyInHydrostaticEquilibrium):
    celestial_type = 'star'

    mass = 1
    radius = 1
    luminosity = 1
    lifetime = 1
    temperature = 1
    classification = 'G'

    habitable_inner = 0
    habitable_outer = 0
    inner_boundry = 0
    outer_boundry = 0
    frost_line = 0

    letter = None
    idx = None

    _lifetime = 0
    _temperature = 0
    _habitable_inner = 0
    _habitable_outer = 0
    _inner_boundry = 0
    _outer_boundry = 0
    _frost_line = 0

    _system = None
    _inner_forbidden = None
    _outer_forbidden = None
    _shared_mass = None

    _spin = ''

    _age = -1
    age = 0

    evolution_id = None

    sub_classification = 0

    neighbourhood_idx = None

    position = None

    prefix = ''
    sub_pos = 0

    light_color = None

    def __init__(self, data):
        mass = data.get('mass', False)
        luminosity = data.get('luminosity', False)
        assert mass or luminosity, 'Must specify at least mass or luminosity.'

        name = data.get('name', None)
        if name is not None:
            self.name = name
            self.has_name = True

        if mass:
            self._mass = mass
        elif luminosity:
            self._luminosity = luminosity

        if not mass and luminosity:
            self._mass = pow(luminosity, (1 / 3.5))

        elif not luminosity and mass:
            self._luminosity = pow(mass, 3.5)
        self.base_lum = self._luminosity
        self.temperature_mass = self._mass

        self.habitable = 0.5 <= self._mass <= 1.4
        self._spin = choice(['clockwise', 'counter-clockwise']) if 'spin' not in data else data['spin']
        self._radius = self.set_radius()
        self._lifetime = self._mass / self._luminosity
        if 'age' in data:
            self._age = data['age']
        else:
            self.set_age()
        self.set_derivated_characteristics()
        self.set_qs()
        assert 0.08 <= self.mass.m < 120, 'Invalid Mass: Stellar mass must be between 0.08 and 120 solar masses.'

        self.classification = self.stellar_classification(mass)
        self.cls = self.classification
        self.light_color = self.true_color(self.temperature)
        self.peak_light = LightWave(self.peak_lightwave_frequency(self.temperature))

        # ID values make each star unique, even if they have the same mass and name.
        self.id = data['id'] if 'id' in data else generate_id()
        self.evolution_id = self.id

    @property
    def spin(self):
        if self._spin == 'clockwise':
            return 'clockwise'
        elif self._spin == 'counter-clockwise':
            return 'counter-clockwise'

    def set_radius(self, mass=None):
        radius = 1
        if mass is None:
            mass = self._mass

        if mass < 1:
            radius = pow(mass, 0.8)
        elif mass > 1:
            radius = pow(mass, 0.5)
        return radius

    def set_age(self, x=0):
        if self._age == -1:
            # reseting the star's mass should not change it's age, because it is the same star that is being remodeled.
            self._age = (self._lifetime * 0.46) * 10 ** 10
        else:
            age = (self._lifetime * x) * 10 ** 10
            if age != self._age:
                self._age = age
                self.set_luminosity(self._age)
                self.evolution_id = generate_id()
            return q(age, 'years')

    def set_derivated_characteristics(self):
        mass = pow(self._luminosity, (1 / 3.5))
        self._temperature = pow((self._luminosity / pow(self._radius, 2)), (1 / 4))
        self._habitable_inner = round(sqrt(self._luminosity / 1.1), 3)
        self._habitable_outer = round(sqrt(self._luminosity / 0.53), 3)
        self._inner_boundry = round(mass * 0.01, 3)
        self._outer_boundry = round(mass * 40, 3)
        self._frost_line = round(4.85 * sqrt(self._luminosity), 3)

    def set_qs(self):
        self.mass = q(self._mass, 'sol_mass')
        self.luminosity = q(self._luminosity, 'sol_luminosity')
        self.radius = q(self._radius, 'sol_radius')
        self.lifetime = q(self._lifetime, 'solar_lifetime')
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
        self.age = q(self._age, 'years')
        self.extend_classification()

    @staticmethod
    def stellar_classification(mass):
        assert mass > 0, 'Star mass must be greater than 0.'
        masses = [0.08, 0.45, 0.8, 1.04, 1.4, 2.1, 16]
        classes = ["M", "K", "G", "F", "A", "B", "O"]
        idx = bisect_right(masses, mass)
        return classes[idx - 1]

    def luminosity_at_age(self, age=None):
        lum = self.base_lum
        forty_six_percent = self.lifetime.to('years').m * 0.46
        if age is None:
            age = self._age

        lum_at_age = lum * (0.25 / forty_six_percent * age + 0.75)
        return lum_at_age

    def set_luminosity(self, age):
        self._luminosity = self.luminosity_at_age(age)
        mass = pow(self._luminosity, (1 / 3.5))
        self.temperature_mass = mass
        self._radius = self.set_radius(mass)
        self.set_derivated_characteristics()
        self.set_qs()

    @classmethod
    def get_class(cls, mass):
        return cls.stellar_classification(mass)

    @staticmethod
    def true_color(temperature):
        t = decimal_round(temperature.to('kelvin').m)

        kelvin = [2660, 3120, 3230, 3360, 3500, 3680, 3920, 4410, 4780, 5240, 5490, 5610, 5780, 5920, 6200, 6540, 6930,
                  7240, 8190, 8620, 9730, 10800, 12400, 13400, 14500, 15400, 16400, 18800, 22100, 24200, 27000, 30000,
                  31900, 35000, 38000]

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
            if number >= 255:
                return 255
            elif number <= 0:
                v = abs(number)
                return cap(v)
            else:
                return number

        r, g, b = 0, 0, 0
        try:
            r = cap(decimal_round(ar * x + br))
            g = cap(decimal_round(ag * x + bg))
            b = cap(decimal_round(ab * x + bb))
        except RecursionError:
            # No sé porqué, pero a veces pasa esto.
            print(r, g, b)
            r = 1
            g = 1
            b = 1

        color = Color(r, g, b)
        return color

    # These 4 methods correspond to a star that is part of a binary system.
    def inherit(self, system, inner, outer, mass, idx):
        self.prefix = system.letter
        self.sub_pos = idx
        self._system = system
        self._shared_mass = mass
        self._inner_forbidden = inner
        self._outer_forbidden = outer

    @property
    def system(self):
        if self._system is not None:
            return self._system
        else:
            return self

    def composition(self):
        return [self]

    @property
    def shared_mass(self):
        return self._shared_mass

    @property
    def inner_forbbiden_zone(self):
        return self._inner_forbidden

    @property
    def outer_forbbiden_zone(self):
        return self._outer_forbidden

    @property
    def star_system(self):
        return self

    @staticmethod
    def peak_lightwave_frequency(temperature):
        return 0.0028977729 / (temperature * 5778) * 1000000000

    def validate_orbit(self, orbit):
        return self._inner_boundry < orbit < self._outer_boundry

    def extend_classification(self):
        t = decimal_round(self.temperature.to('kelvin').m)
        temps = {"M": [2000, 1700],
                 "K": [3700, 1500],
                 "G": [5200, 800],
                 "F": [6000, 1500],
                 "A": [7500, 2500],
                 "B": [10000, 23000],
                 "O": [33000, 62000]}
        a, b = temps[self.classification]

        self.sub_classification = (round((1 - (t - a) / b) * 10, 1))

    def update_everything(self, **kwargs):
        if self.mass != self._mass:
            self._mass = self.mass.m
            self._luminosity = pow(self._mass, 3.5)

        elif self.luminosity != self._luminosity:
            self._luminosity = self.luminosity.m
            self._mass = pow(self._luminosity, (1 / 3.5))

        self.temperature_mass = self._mass
        self.habitable = 0.5 <= self._mass <= 1.4
        self._radius = self.set_radius()
        self.set_derivated_characteristics()
        self._lifetime = self._mass / self._luminosity
        # self.set_age()  # not sure, 'cause tweeking the mass means the same star is being remodeled. See line 119.
        self.set_qs()
        assert 0.08 <= self.mass.m < 120, 'Invalid Mass: Stellar mass must be between 0.08 and 120 solar masses.'

        self.classification = self.stellar_classification(self._mass)
        self.cls = self.classification
        self.light_color = self.true_color(self.temperature)

    def compare(self, other):
        if hasattr(other, 'cls'):
            return self.cls == other.cls
        else:
            return False

    def __str__(self):
        if self.has_name:
            return self.name
        # elif self.prefix != '':
        #     sub = self.sub_classification
        #     return f"{self.prefix}{turn_into_roman(self.sub_pos)}{self.cls}{sub}{turn_into_roman(self.idx + 1)}"
        else:
            return f"{self.cls}{self.sub_classification}{turn_into_roman(self.idx + 1)}"

    def __repr__(self):
        if self.has_name is False:
            return f"Star {self.name} {self.mass.m}"
        else:
            return self.name

    def __eq__(self, other):
        if not hasattr(other, 'celestial_type'):
            return False
        elif self.celestial_type == other.celestial_type:
            return all([self.mass.m == other.mass.m, self.name == other.name, self.id == other.id])
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.mass.m, self.name, self.id))

    def __getitem__(self, item):
        if type(item) is int:
            if item == 0:
                return self
            raise StopIteration()


class LightWave:
    _color = None
    frequency = None

    def __init__(self, frequency):
        self.frequency = frequency
        self.spectrum = self.radiation_type(frequency)

    @staticmethod
    def visible_color(frequency):
        color = None
        if 43.4941208 < frequency < 1664.635167:
            if 43.4941208 <= frequency <= 400:
                color = Color(0, 0, 0)
            elif 400 <= frequency <= 410:
                color = Color(37, 12, 83)
            elif 410 <= frequency <= 420:
                color = Color(66, 28, 163)
            elif 420 <= frequency <= 430:
                color = Color(96, 37, 247)
            elif 430 <= frequency <= 440:
                color = Color(78, 55, 232)
            elif 440 <= frequency <= 450:
                color = Color(63, 73, 217)
            elif 450 <= frequency <= 460:
                color = Color(58, 92, 203)
            elif 460 <= frequency <= 470:
                color = Color(63, 111, 188)
            elif 470 <= frequency <= 480:
                color = Color(68, 120, 173)
            elif 480 <= frequency <= 490:
                color = Color(73, 129, 157)
            elif 490 <= frequency <= 500:
                color = Color(78, 138, 143)
            elif 500 <= frequency <= 510:
                color = Color(83, 147, 128)
            elif 510 <= frequency <= 520:
                color = Color(88, 156, 114)
            elif 520 <= frequency <= 530:
                color = Color(93, 165, 100)
            elif 530 <= frequency <= 540:
                color = Color(99, 175, 87)
            elif 540 <= frequency <= 550:
                color = Color(115, 190, 76)
            elif 550 <= frequency <= 560:
                color = Color(141, 206, 68)
            elif 560 <= frequency <= 570:
                color = Color(175, 222, 62)
            elif 570 <= frequency <= 580:
                color = Color(214, 238, 59)
            elif 580 <= frequency <= 590:
                color = Color(255, 255, 60)
            elif 590 <= frequency <= 600:
                color = Color(234, 169, 40)
            elif 600 <= frequency <= 610:
                color = Color(223, 86, 15)
            elif 610 <= frequency <= 620:
                color = Color(219, 0, 0)
            elif 620 <= frequency <= 630:
                color = Color(197, 0, 0)
            elif 630 <= frequency <= 640:
                color = Color(174, 0, 0)
            elif 640 <= frequency <= 650:
                color = Color(152, 0, 0)
            elif 650 <= frequency <= 660:
                color = Color(130, 0, 0)
            elif 660 <= frequency <= 670:
                color = Color(109, 0, 0)
            elif 670 <= frequency <= 680:
                color = Color(87, 0, 0)
            elif 680 <= frequency <= 690:
                color = Color(67, 0, 0)
            elif 690 <= frequency <= 700:
                color = Color(47, 0, 0)
            elif 700 <= frequency <= 710:
                color = Color(27, 0, 0)
            elif 710 <= frequency <= 1664.635167:
                color = Color(0, 0, 0)

        return color

    def radiation_type(self, frequency):
        if frequency.m < 400:
            return "ULTRA-VIOLET"
        elif frequency.m > 710:
            return "INFRARED"
        else:
            self._color = self.visible_color(frequency.m)
            return "VISIBLE"

    @property
    def color(self):
        return self._color


from .general import BodyInHydrostaticEquilibrium
from engine import q
from bisect import bisect_right
from math import sqrt, pow
from pygame import Color
from engine.backend.util import decimal_round
from datetime import datetime


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

    def __init__(self, data):
        mass = data.get('mass', False)
        luminosity = data.get('luminosity', False)
        assert mass or luminosity, 'Must specify at least mass or luminosity'

        name = data.get('name', None)
        if name is not None:
            self.name = name
            self.has_name = True
        else:
            self.name = "NoName"

        self.idx = data.get('idx', 0)

        if mass:
            self._mass = mass
        elif luminosity:
            self._luminosity = luminosity

        if not mass and luminosity:
            self._mass = pow(luminosity, (1 / 3.5))

        elif not luminosity and mass:
            self._luminosity = pow(mass, 3.5)

        if self._mass < 1:
            self._radius = pow(self._mass, 0.8)
        elif self._mass > 1:
            self._radius = pow(self._mass, 0.5)
        else:
            self._radius = 1

        self._lifetime = self._mass / self._luminosity
        self._temperature = pow((self._luminosity / pow(self._radius, 2)), (1 / 4))
        self._habitable_inner = round(sqrt(self._luminosity / 1.1), 3)
        self._habitable_outer = round(sqrt(self._luminosity / 0.53), 3)
        self._inner_boundry = self._mass * 0.01
        self._outer_boundry = self._mass * 40
        self._frost_line = round(4.85 * sqrt(self._luminosity), 3)

        self.set_qs()
        assert 0.08 <= self.mass.m < 120, 'Invalid Mass: Stellar mass must be between 0.08 and 120 solar masses.'

        self.classification = self.stellar_classification()
        self.cls = self.classification
        self.color = self.true_color()

        # ID values make each star unique, even if they have the same mass and name.
        self.id = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])

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
        masses = [0.08, 0.45, 0.8, 1.04, 1.4, 2.1, 16]
        classes = ["M", "K", "G", "F", "A", "B", "O"]
        idx = bisect_right(masses, self._mass)
        return classes[idx - 1:idx][0]

    def true_color(self):
        t = decimal_round(self.temperature.to('kelvin').m)

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

        ar = (y2.r - y1.r) / (x2 - x1)
        ag = (y2.g - y1.g) / (x2 - x1)
        ab = (y2.b - y1.b) / (x2 - x1)

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

        r = cap(decimal_round(ar * x + br))
        g = cap(decimal_round(ag * x + bg))
        b = cap(decimal_round(ab * x + bb))

        color = Color(r, g, b)
        return color

    def __str__(self):
        return "{}-Star #{}".format(self.cls, self.idx)

    def __repr__(self):
        return "Star " + self.name + ' {}'.format(self.mass.m)

    def __eq__(self, other):
        test = all([self.mass.m == other.mass.m, self.name == other.name, self.id == other.id])
        return test

    def __hash__(self):
        return hash((self.mass.m, self.name, self.id))

from .general import BodyInHydrostaticEquilibrium
from engine import q
from bisect import bisect_right
from math import sqrt
from pygame import Color


class Star(BodyInHydrostaticEquilibrium):
    mass = 1
    radius = 1
    luminosity = 1
    lifetime = 1
    temperature = 1
    classification = 'G'
    name = None
    has_name = False

    def __init__(self, data):
        mass = data.get('mass', False)
        luminosity = data.get('luminosity', False)
        if not mass and not luminosity:
            raise ValueError('must specify at least mass or luminosity')

        name = data.get('name', None)
        if name is not None:
            self.name = name
            self.has_name = True
        else:
            self.name = "NoName"

        if mass:
            self.mass = q(mass, 'sol_mass')
        elif luminosity:
            self.luminosity = q(luminosity, 'sol_luminosity')

        if not mass and luminosity:
            self.mass = q(luminosity ** (1/3.5),'sol_mass')
        elif not luminosity and mass:
            self.luminosity = q(mass ** 3.5, 'sol_luminosity')

        if self.mass.m < 1:
            self.radius = q(self.mass.m ** 0.8, 'sol_radius')
        elif self.mass.m > 1:
            self.radius = q(self.mass.m ** 0.5, 'sol_radius')
        else:
            self.radius = q(1, 'sol_radius')

        self.lifetime = q(self.mass.m / self.luminosity.m, 'sol_lifetime')
        self.temperature = q((self.luminosity.m / (self.radius.m ** 2)) ** (1 / 4), 'sol_temperature')
        self.volume = q(self.calculate_volume(self.radius.to('km').m), 'km^3')
        self.density = q(self.calculate_density(self.mass.to('g').m, self.radius.to('cm').m), 'g/cm^3')
        self.circumference = q(self.calculate_circumference(self.radius.to('km').m), 'km')
        self.surface = q(self.calculate_surface_area(self.radius.to('km').m), 'km^2')
        self.classification = self.stellar_classification(self.mass.m)
        self.cls = self.classification

        self.habitable_inner = q(round(sqrt(self.luminosity.magnitude / 1.1), 3), 'au')
        self.habitable_outer = q(round(sqrt(self.luminosity.magnitude / 0.53), 3), 'au')

        self.inner_boundry = q(self.mass.m * 0.01, 'au')
        self.outer_boundry = q(self.mass.m * 40, 'au')

        self.frost_line = q(round(4.85 * sqrt(self.luminosity.magnitude), 3), 'au')
        self.color = self.true_color()

    @staticmethod
    def stellar_classification(mass):
        masses = [0.08, 0.45, 0.8, 1.04, 1.4, 2.1, 16]
        classes = ["M", "K", "G", "F", "A", "B", "O"]
        idx = bisect_right(masses, mass)
        return classes[idx - 1:idx][0]

    def true_color(self):
        def hex_to_rgb(value):
            # from: https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
            value = value.lstrip('#')
            lv = len(value)
            return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

        t = self.temperature.to('kelvin').m

        kelvin = [2660, 3120, 3230, 3360, 3500, 3680, 3920, 4410, 4780, 5240, 5490, 5610, 5780, 5920, 6200, 6540, 6930,
                  7240, 8190, 8620, 9730, 10800, 12400, 13400, 14500, 15400, 16400, 18800, 22100, 24200, 27000, 30000,
                  31900, 35000, 38000]

        hexs = ['#ffad51', '#ffbd71', '#ffc177', '#ffc57f', '#ffc987', '#ffcd91', '#ffd39d', '#ffddb4', '#ffe4c4',
                '#ffead5', '#ffeedd', '#ffefe1', '#fff1e7', '#fff3eb', '#fff6f3', '#fff9fc', '#f9f6ff', '#f2f2ff',
                '#e3e8ff', '#dde4ff', '#d2dcff', '#cad6ff', '#c1d0ff', '#bccdff', '#b9caff', '#b6c8ff', '#b4c6ff',
                '#afc2ff', '#abbfff', '#a9bdff', '#a7bcff', '#a5baff', '#a4baff', '#a3b8ff', '#a2b8ff']

        idx = bisect_right(kelvin, t)
        if idx > len(kelvin) - 1:
            return Color(hex_to_rgb(hexs[-1]))
        else:
            return Color(hex_to_rgb(hexs[idx]))

    def __repr__(self):
        return "Star " + self.name

from .general import BodyInHydrostaticEquilibrium
from engine import q
from bisect import bisect_right
from math import sqrt


class Star(BodyInHydrostaticEquilibrium):
    mass = 1
    radius = 1
    luminosity = 1
    lifetime = 1
    temperature = 1
    classification = 'G'

    def __init__(self, name, mass):
        self.name = name
        self.mass = q(mass, 'sol_mass')
        if mass < 1:
            self.radius = q(mass ** 0.8, 'sol_radius')
        elif mass > 1:
            self.radius = q(mass ** 0.5, 'sol_radius')

        self.luminosity = q(mass ** 3.5, 'sol_luminosity')
        self.lifetime = q(mass / self.luminosity, 'sol_lifetime')
        self.temperature = (self.luminosity / (self.radius ** 2)) ** (1 / 4)
        self.volume = self.calculate_volume(self.radius.to('kilometers'))
        self.density = self.calculate_density(self.mass, self.radius)
        self.circumference = self.calculate_circumference(self.radius.to('kilometers'))
        self.surface = self.calculate_surface_area(self.radius.to('kilometers'))
        self.classification = self.stellar_classification(mass)

        self.habitable_inner = q(sqrt(self.luminosity.magnitude / 1.1), 'au')
        self.habitable_inner = q(sqrt(self.luminosity.magnitude / 0.53), 'au')

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

        kelvin = [2660, 3120, 3230, 3360, 3500, 3680, 3920, 4410, 4780, 5240, 5490, 5610, 5780, 5920, 6200, 6540, 6930,
                  7240, 8190, 8620, 9730, 10800, 12400, 13400, 14500, 15400, 16400, 18800, 22100, 24200, 27000, 30000,
                  31900, 35000, 38000]

        hexs = ['#ffad51', '#ffbd71', '#ffc177', '#ffc57f', '#ffc987', '#ffcd91', '#ffd39d', '#ffddb4', '#ffe4c4',
                '#ffead5', '#ffeedd', '#ffefe1', '#fff1e7', '#fff3eb', '#fff6f3', '#fff9fc', '#f9f6ff', '#f2f2ff',
                '#e3e8ff', '#dde4ff', '#d2dcff', '#cad6ff', '#c1d0ff', '#bccdff', '#b9caff', '#b6c8ff', '#b4c6ff',
                '#afc2ff', '#abbfff', '#a9bdff', '#a7bcff', '#a5baff', '#a4baff', '#a3b8ff', '#a2b8ff']

        idx = bisect_right(kelvin, self.temperature.magnitude)
        return hex_to_rgb(hexs[idx - 1:idx][0])

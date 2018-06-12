from math import pi


class HydrostaticEquilibrium:
    circumference = 0
    surface = 0
    volume = 0
    density = 0

    @staticmethod
    def calculate_circumference(r):
        return 2 * pi * r

    @staticmethod
    def calculate_surface_area(r):
        return 4 * pi * (r ** 2)

    @staticmethod
    def calculate_volume(r):
        return (4 / 3) * pi * (r ** 3)

    @classmethod
    def calculate_density(cls, m, r):
        v = cls.calculate_volume(r)
        return m / v

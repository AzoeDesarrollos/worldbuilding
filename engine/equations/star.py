from .general import HydrostaticEquilibrium
from engine import q


class Star(HydrostaticEquilibrium):
    mass = 1
    radius = 1
    luminosity = 1
    lifetime = 1
    temperature = 1
    clase = 'G'

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

        # for minimo, maximo in STELAR_CLASIFICATION:
        #     if minimo <= mass <= maximo:
        #         self.clase = STELAR_CLASIFICATION[(minimo, maximo)]

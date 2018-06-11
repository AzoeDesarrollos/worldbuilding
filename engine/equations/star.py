# from engine.globs.constants import UNIT_KG, UNIT_KM, UNIT_WATTS, UNIT_KELVIN, UNIT_YEAR, UNIT_KM2, UNIT_KM3
# from engine.globs.constants import SOL_MASS, SOL_LUMINOSITY, SOL_RADIUS, SOL_TEMPERATURE, SOL_LIFETIME
# from engine.globs.constants import STELAR_CLASIFICATION
# from math import pi


class Star:
    mass = 1
    radius = 1
    luminosity = 1
    lifetime = 1
    temperature = 1
    clase = 'G'

    def __init__(self, name, mass):
        self.name = name
        self.mass = mass
        if mass < 1:
            self.radius = mass ** 0.8
        elif mass > 1:
            self.radius = mass ** 0.5

        self.luminosity = mass ** 3.5
        self.lifetime = mass / self.luminosity
        self.temperature = (self.luminosity / (self.radius ** 2)) ** (1 / 4)

        # for minimo, maximo in STELAR_CLASIFICATION:
        #     if minimo <= mass <= maximo:
        #         self.clase = STELAR_CLASIFICATION[(minimo, maximo)]

    @staticmethod
    def to_excel(value):
        s = str(value)
        s = s.replace('.', ',')
        return s

    # def export(self):
    #     x = {'name': self.name,
    #          'relatives': {
    #              'mass': self.to_excel(self.mass),
    #              'radius': self.to_excel(round(self.radius, 2)),
    #              'lifetime': self.to_excel(round(self.lifetime, 2)),
    #              'temperature': self.to_excel(round(self.temperature, 2)),
    #              'luminosity': self.to_excel(round(self.luminosity, 2))
    #          },
    #          'absolutes': {
    #              'mass': '{0:.2E}'.format(self.mass * SOL_MASS) + ' ' + UNIT_KG,
    #              'radius': '{0:.2E}'.format(self.radius * SOL_RADIUS) + ' ' + UNIT_KM,
    #              'luminosity': '{0:.2E}'.format(self.luminosity * SOL_LUMINOSITY) + ' ' + UNIT_WATTS,
    #              'temperature': '{0:.2E}'.format(self.temperature * SOL_TEMPERATURE) + ' ' + UNIT_KELVIN,
    #              'lifetime': '{0:.2E}'.format(self.lifetime * SOL_LIFETIME) + ' ' + UNIT_YEAR,
    #              'circumference': '{0:.2E}'.format(2 * pi * self.radius * SOL_RADIUS) + ' ' + UNIT_KM,
    #              'surface area': '{0:.2E}'.format(4 * pi * ((self.radius * SOL_RADIUS) ** 2)) + ' ' + UNIT_KM2,
    #              'volume': '{0:.2E}'.format((4 / 3) * pi * ((self.radius * SOL_RADIUS) ** 3)) + ' ' + UNIT_KM3,
    #              'type': self.clase
    #          }
    #          }
    #     return x

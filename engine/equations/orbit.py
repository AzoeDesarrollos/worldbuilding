from math import sqrt


class Orbit:
    semi_major_axis = 0
    eccentricity = 0
    inclination = 0

    semi_minor_axis = 0
    periapsis = 0
    apoapsis = 0

    period = 0
    velocity = 0
    motion = ''

    has_name = False
    name = ''

    def __init__(self, star_mass, a, e, i, name=None):
        self.eccentricity = float(e)
        self.inclination = float(i)
        self.semi_major_axis = float(a)

        if name is not None:
            self.name = name
            self.has_name = True
        else:
            self.name = 'Orbit @' + str(a)
            self.has_name = False

        self.semi_minor_axis = a * sqrt(1 - e ** 2)
        self.periapsis = a * (1 - e)
        self.apoapsis = a * (1 + e)
        self.velocity = sqrt(star_mass / a)

        if self.inclination in (0, 180):
            self.motion = 'equatorial'
        elif self.inclination == 90:
            self.motion = 'polar'

        if 0 <= self.inclination <= 90:
            self.motion += 'prograde'
        elif 90 < self.inclination <= 180:
            self.motion += 'retrograde'

        self.period = sqrt((a ** 3) / star_mass)


# class StandardOrbit(Orbit):
#     def __init__(self, system, a, e=0, i=0, name=''):
#         self.semi_major_axis = a
#         self.period = sqrt((a ** 3) / system.star_mass)
#         super().__init__(system, a, e, i, name)
#
#     def __repr__(self):
#         if self.name != '':
#             return str(self.name) + ' @' + str(round(self.semi_major_axis, 3))
#         else:
#             return str(round(self.semi_major_axis, 3))
#
#
# class ResonantOrbit(Orbit):
#     def __init__(self, system, primary, resonance, e=0, i=0, name=''):
#         x, y = [int(i) for i in resonance.split(':')]
#         self.period = (y * primary) / x
#         a = ((self.period ** 2) * system.star_mass) ** (1 / 3)
#         super().__init__(system, a, e, i, name)
#
#     def __repr__(self):
#         return 'Resonant Orbit'


# class TerrestialOrbit(StandardOrbit):
#     def __init__(self, system, a, e=0, name='', habitable=False):
#         assert 0 <= e <= 0.2
#
#         hi, ho = system.habitable_zone_inner, system.habitable_zone_outer
#         if habitable:
#             print('habitable terrestial planet should orbit between', hi, 'and', ho)
#
#         super().__init__(system, a, e, 0, name)
#
#         if habitable:
#             assert self.periapsis >= hi, 'periapsis falls outside of the habitable zone'
#             assert self.apoapsis <= ho, 'apoapsis falls outside of the habitable zone'
#
#
# class GasGiantOrbit(StandardOrbit):
#     def __init__(self, system, a, e, i, name=''):
#         assert 0.001 <= e <= 0.09, "inaccurate eccentricity"
#         assert 0 < i < 90, 'orbital motion must be prograde'
#         super().__init__(system, a, e, i, name)
#
#
# class ClassicalGasGiantOrbit(GasGiantOrbit):
#     def __init__(self, system, a, e, i, name=''):
#         fl = system.frost_line
#         assert fl < a <= fl * 1.2
#         super().__init__(system, a, e, i, name)
#
#
# class HotJupiterOrbit(GasGiantOrbit):
#     def __init__(self, system, a, e=0, i=0, name=None):
#         assert 0.04 <= a <= 0.5, "inaccurate semi_major_axis"
#
#         assert -10 <= i <= 10, "inclination is unrealistic"
#         if i < 0:
#             i += 180
#         super().__init__(system, a, e, i, name)
#         assert self.period < 3, 'lower limit for orbital period exceeded'
#
#
# class SuperJupiterOrbit(GasGiantOrbit):
#     def __init__(self, system, a, e, i, name=''):
#         assert 0.04 <= a <= system.frost_line + 1.2
#         super().__init__(system, a, e, i, name)
#
#
# class GasDwarfOrbit(GasGiantOrbit):
#     def __init__(self, system, a, e, i, name=''):
#         assert system.frost_line + 1.2 <= a <= system.outer_boundry
#         super().__init__(system, a, e, i, name)

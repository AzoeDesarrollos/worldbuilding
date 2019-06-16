from math import sqrt
from pygame import draw, Rect
from engine import q


def put_in_star_orbit(body, star, a, e, i):
    body.orbit = PlanetOrbit(star.mass.magnitude, a, e, i)


def put_in_planet_orbit(body, planet, star, a, e, i):
    body.orbit = SatelliteOrbit(planet.mass.m, star.mass.m, a, e, i)


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

    def __init__(self, a, e, i, unit='au'):
        self.eccentricity = q(float(e))
        self.inclination = q(float(i), "degree")
        self.semi_major_axis = q(float(a), unit)

        self.semi_minor_axis = q(a * sqrt(1 - e ** 2), unit)
        self.periapsis = q(a * (1 - e), unit)
        self.apoapsis = q(a * (1 + e), unit)

        if self.inclination in (0, 180):
            self.motion = 'equatorial'
        elif self.inclination == 90:
            self.motion = 'polar'
        elif 0 <= self.inclination <= 90:
            self.motion = 'prograde'
        elif 90 < self.inclination <= 180:
            self.motion = 'retrograde'

    def draw(self, surface):
        rect = Rect(0, 0, 2 * self.semi_major_axis, 2 * self.semi_minor_axis)
        screen_rect = surface.get_rect()
        rect.center = screen_rect.center
        draw.ellipse(surface, (255, 255, 255), rect, width=1)


class PlanetOrbit(Orbit):
    def __init__(self, star_mass, a, e, i):
        super().__init__(a, e, i, 'au')
        self.velocity = q(sqrt(star_mass / a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(sqrt((a ** 3) / star_mass), 'year')


class SatelliteOrbit(Orbit):
    def __init__(self, planet_mass, moon_mass, a, e, i):
        super().__init__(a, e, i, 'earth_radius')
        self.velocity = q(sqrt(planet_mass / a), 'earth_orbital_velocity').to('kilometer per second')
        self.period = q(0.0588*(a**3/sqrt(planet_mass+moon_mass)), 'day')

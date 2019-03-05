from math import sqrt
from pygame import draw, Rect


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

    def draw(self, surface):
        rect = Rect(0, 0, 2 * self.semi_major_axis, 2 * self.semi_minor_axis)
        screen_rect = surface.get_rect()
        rect.center = screen_rect.center
        draw.ellipse(surface, (255, 255, 255), rect, width=1)

from math import sqrt, sin, cos, pi
# adapted from https://www.desmos.com/calculator/znsuonopre
sun_mass = 1

planet = object()
orbit = type('Orbit', dict={'a': 1, 'period': 1, 'e': 0})
planet.orbit = orbit()
planet.orbit.a = 1  # the semi-major axis of your planet in AU (distance between Earth and its sun)
planet.orbit.period = 1  # "p" is the orbital period of your planet in Earth years
planet.r = 1  # the radius of your planet in Earth radii
planet.d = 1  # the density of your planet compared to Earth's density
planet.m = 1  # the mass of your planet compared to Earth

moon = type('Moon')
moon_a = moon()
moon_a.r = 1  # the radius of your habitable moon A in Earth radii
moon_a.d = 1  # the density of your habitable moon A compared to Earth
moon_a.orbit = orbit()
moon_a.orbit.a = 1  # the semi-major axis of Moon A's orbit in Earth radii
moon_a.orbit.e = 0.01  # the eccentricity of Moon A's orbit
moon_a.orbit.period = 1  # the orbital period of Moon A in Earth days

moon_b = moon()
moon_b.r = 1  # the radius of your habitable moon B in Earth radii
moon_b.d = 1  # the density of your habitable moon B compared to Earth
moon_b.orbit = orbit()
moon_b.orbit.a = 1  # the semi-major axis of Moon B's orbit in Earth radii
moon_b.orbit.e = 0.01  # the eccentricity of Moon B's orbit
moon_b.orbit.period = 1  # the orbital period of Moon B in Earth days

assert (abs(moon_b.orbit.a - moon_a.orbit.a) > 10 * planet.r), "orbits will merge"

L = 44  # We will be looking at the height of the tides at point "L" on Moon A. When L=0 degrees, we are at the point
# on Moon A that is perpetually facing the planet. When L=180 degrees, we are at the point that is perpetually
# facing away from the planet. As we travel around the equator of Moon A, the height of the tides will change.
# Select  the value of "L".


x = 0


def y_abdistance(moon_x, moon_y, xt):
    a_a = moon_x.orbit.a
    a_b = moon_x.orbit.a
    p_a = moon_y.orbit.period
    p_b = moon_y.orbit.period
    return sqrt((a_a ** 2 + a_b) - 2 * a_a * a_b * cos(((2 * pi * xt) / p_b) - ((2 * pi * xt) / p_a)))


Wa = moon_a.r ** 3 * moon_a.d
Wb = moon_b.r ** 3 * moon_b.d
pixt2 = 2 * pi * x

Tba = (2230000 * moon_a.r * moon_a.d) / y_abdistance(moon_a, moon_b, x) ** 3
Ca = moon_a.orbit.a * (Wa / (planet.m + Wa))
Cb = moon_b.orbit.b * (Wb / (planet.m + Wb))

y_xa = moon_a.orbit.a * cos(pixt2 / moon_a.orbit.period) + Ca
y_ya = moon_b.orbit.a * sin(pixt2 / moon_a.orbit.period)

y_xb = moon_a.orbit.b * cos(pixt2 / moon_b.orbit.period) + Cb
y_yb = moon_a.orbit.a * sin(pixt2 / moon_b.orbit.period)
La = sqrt(y_xa ** 2 + y_ya ** 2)
Lb = sqrt(y_xb ** 2 + y_yb ** 2)

# readability
y_ab_d = y_abdistance(moon_a, moon_b, x)
y_abd_2_La_Lb = y_ab_d ** 2 + La ** 2 - Lb ** 2
pi_L_90 = pi * L / 90
La_y_ab_d = La * y_ab_d

# This purple graph is the effect of Moon B on the tides of Moon A (note this is not in metres)
T_moon_b = Tba * ((2 * (y_abd_2_La_Lb / 2 * La_y_ab_d) ** 2 - 1) * cos(pi_L_90) - 2 * (Lb / y_ab_d) *
                  sin((pixt2 / moon_b.orbit.period) - (pixt2 / moon_a.orbit.period)) *
                  (y_abd_2_La_Lb / 2 * La_y_ab_d) * sin(pi_L_90))

T_sun = ((0.46 * sun_mass * moon_a.d) / moon_a.orbit.a ** 3) * cos(pi_L_90)
T_pla = ((2230000 * planet.m * moon_a.d) / moon_a.orbit.a ** 3) * cos(pi_L_90)

T = 0.54 * (T_moon_b + T_sun + T_pla)
# This blue graph is the tides (in metres) at point "L" on Moon A. The x-axis represents time in Earth days.
# if you have a massive planet the tides may be permanently hugely positive or negative depending on point "L"

from math import log, trunc
from engine.backend import q


def aprox_day_leght(planet, bya):
    """Aproximate formula of day leght for Earth. It is not exact, but close enough.

    where:
    h = the duration of the day in modern times.
    bya = billion years (10^8) ago. (ex x=-46*10**8 = -4.600.000.000)
    bya can be positive or negative.
    """

    if abs(bya) / (10 ** 8) > 0:
        bya /= (10 ** 8)

    day_leght = q(planet.reference_rotation / (1.03 ** -bya), 'hour/day')
    in_history(planet, day_leght.m)
    return day_leght


def what_bya(planet, t):
    """At what moment in the history of the planet day_leght had a value of t?

    where:
    t = day_leght between planet formation (p) y current times (h).
    h = the duration of the day in modern times.
    """
    assert in_history(planet, t), "Moment in time is outside of the planet's history"
    bya = log(planet.reference_rotation / t) / log(1 / 1.03)  # natural logarithms.
    return bya


def in_history(planet, t):
    p = planet.reference_rotation / (1.03 ** -planet.formation.m)
    return p <= t <= planet.reference_rotation


def twenty_four_hour_day_moment(planet):
    """Momento en la historia en la que la rotación del planeta es de 24 horas por dia.

    Tiene más sentido cuando day_leght != 24 hs.
    """
    bya = log(round(planet.rotation.to('hours/day').m, 3) / 24) / log(1 / 1.03)
    return bya


def cells_per_hemisphere(planet):
    # Earth's rotation rate: for wind patterns.
    r = round(planet.rotation.to('hours/day').m, 3) / 24
    rs = (16, 8, 4, 2, 1, 0.5, 0.25, 0.125)
    ratios = [r / d for d in rs]
    most = [i - 1 for i in ratios]
    idx = min(enumerate(most), key=lambda x: abs(x[1]))[0]

    do = 'nothing'
    if 0 <= idx <= 3:
        do = '1 cell per hemisphere (0°-90°)'
    elif 4 <= idx <= 5:
        do = '3 cells (0°-30°, 30°-60°, 60°-90°)'
    elif idx == 6:
        do = '7 cells (0-24°, 24°-27°, 27°-31°, 31°-41°, 41°-58°, 58°-71°, 71°-90°)'
    elif idx == 7:
        do = '5 cells (0-23°, 23°-30°, 30°-47°, 47°-56°, 56°-90°)'

    return do


def to_hours_mins_secs(sample):
    if sample > 24:
        dias = trunc(sample/24)
        sample = ((sample/24) - dias)*24
    else:
        dias = 0
    horas = trunc(sample)

    sample = (sample - horas) * 60
    minutos = trunc(sample)

    sample = (sample - minutos) * 60
    segundos = trunc(sample)

    return dias, horas, minutos, segundos

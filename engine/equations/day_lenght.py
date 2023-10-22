from math import trunc
from engine.backend import q


def aprox_daylenght(planet, bya):
    """Aproximate formula of day lenght for Earth. It is not exact, but close enough.

    where:
    h = the duration of the day in modern times.
    bya = billion years (10^8) ago. (ex x=-46*10**8 = -4.600.000.000)
    bya can be positive or negative.
    """

    if abs(bya) / (10 ** 8) > 0:
        bya /= (10 ** 8)

    return q(planet.reference_rotation / (1.03 ** -bya), 'hour/day')


def to_hours_mins_secs(sample):
    if sample > 24:
        dias = trunc(sample / 24)
        sample = ((sample / 24) - dias) * 24
    else:
        dias = 0
    horas = trunc(sample)

    sample = (sample - horas) * 60
    minutos = trunc(sample)

    sample = (sample - minutos) * 60
    segundos = trunc(sample)

    return dias, horas, minutos, segundos

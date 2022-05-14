from math import log, trunc


def aprox_day_leght(planet, bya):
    """Aproximate formula of day leght for Earth. It is not exact, but close enough.

    where:
    h = the duration of the day in modern times.
    bya = billions of years (10^8) ago. (ex x=-46*10**8 = -4.600.000.000)
    bya can be positive or negative. It is internally turned negative.
    """
    if bya > 0:
        bya = -bya/(10**8)

    day_leght = round(planet.rotation.to('hours/day').m, 3) / (1.03 ** -bya)
    what_bya(planet, day_leght)
    return day_leght/24


def what_bya(planet, t):
    """At what moment in the history of the planet day_leght had a value of t?

    where:
    t = day_leght between planet formation (p) y current times (h).
    h = the duration of the day in modern times.
    """
    assert in_history(planet, t), "Moment in time is outside of the planet's history"
    bya = log(round(planet.rotation.to('hours/day').m, 3) / t) / log(1 / 1.03)  # natural logarithms.
    return bya


def in_history(planet, t):
    if not hasattr(planet, 'formation'):
        planet.formation = 46  # 46 because Earth formed 4.6 billions years ago, this value is arbitrary.

    p = round(planet.rotation.to('hours/day').m, 3) / (1.03 ** planet.formation)
    return p <= t <= round(planet.rotation.to('hours/day').m, 3)


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
    horas = trunc(sample)

    sample = (sample - horas) * 60
    minutos = trunc(sample)

    sample = (sample - minutos) * 60
    segundos = trunc(sample)

    return horas, minutos, segundos


if __name__ == '__main__':
    hours = 30
    ano = twenty_four_hour_day_moment(hours)
    result = aprox_day_leght(hours, ano)
    print(ano)

    print(to_hours_mins_secs(round(result, 3)))
    print(cells_per_hemisphere(float(round(result, 3))))

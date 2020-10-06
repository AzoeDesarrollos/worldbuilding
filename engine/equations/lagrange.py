from math import pi, pow, cos, sin


# sma = semi major axis in AU
# m_primary = mass of the star in solar masses
# m_secondary = mass of the planet in earth masses

def acc(option, d_lp, m_primary, m_secondary, sma, period_secondary):
    g = 6.6725985e-11
    bc = sma * m_secondary / (m_secondary + m_primary)

    if option == 3:
        v = 2 * pi * (d_lp + bc) / period_secondary
        ac = v * v / (d_lp + bc)
    else:
        v = 2 * pi * (d_lp - bc) / period_secondary
        ac = (v * v) / (d_lp - bc)

    if option == 1:
        ag = (g * m_primary / (d_lp * d_lp)) - (g * m_secondary / ((d_lp - sma) * (d_lp - sma)))

    elif option == 2:
        ag = (g * m_primary / (d_lp * d_lp)) + (g * m_secondary / ((d_lp - sma) * (d_lp - sma)))

    else:
        ag = (g * m_primary / (d_lp * d_lp)) + (g * m_secondary / ((d_lp + sma) * (d_lp + sma)))

    return ac - ag


def lagrange(sma, m_primary, m_secondary):

    sma *= 149597870691
    m_primary *= 1.98894729428839E+30
    m_secondary *= 5.97378250603408E+24

    period_secondary = 2 * pi * pow(sma * sma * sma / (6.6725985e-11 * (m_primary + m_secondary)), 0.5)

    delta_a_limit = 1
    for i in reversed(range(15)):
        if sma > pow(10, i):
            delta_a_limit = pow(1 / 10, (15 - i))
            break

    return delta_a_limit, m_primary, m_secondary, sma, period_secondary


def compute_lagrage_one(sma, m_primary, m_secondary):
    delta_a_limit, m_primary, m_secondary, sma, period_secondary = lagrange(sma, m_primary, m_secondary)
    a = 1
    delta_a = 1000000000000

    while delta_a > delta_a_limit:
        b = acc(1, a, m_primary, m_secondary, sma, period_secondary)
        c = acc(1, a + delta_a, m_primary, m_secondary, sma, period_secondary)
        a = a + delta_a

        while abs(b) > abs(c):
            a = a - 2 * delta_a
            delta_a /= 10

    l1_secondary_distance = sma - a  # in meters
    print(l1_secondary_distance)

    l1_primary_distance = a  # in meters
    return l1_primary_distance


def compute_lagrage_two(sma, m_primary, m_secondary):
    delta_a_limit, m_primary, m_secondary, sma, period_secondary = lagrange(sma, m_primary, m_secondary)

    a = sma + 1
    delta_a = 1000000000000

    while delta_a > delta_a_limit:
        b = acc(2, a, m_primary, m_secondary, sma, period_secondary)
        c = acc(2, a + delta_a, m_primary, m_secondary, sma, period_secondary)
        a += delta_a

        while abs(b) > abs(c):
            a = a - 2 * delta_a
            delta_a /= 10

    l2_secondary_distance = a - sma  # in meters
    print(l2_secondary_distance)

    l2_primary_distance = a  # in meters
    return l2_primary_distance


def compute_lagrage_three(sma, m_primary, m_secondary):
    delta_a_limit, m_primary, m_secondary, sma, period_secondary = lagrange(sma, m_primary, m_secondary)

    a = 1
    delta_a = 1000000000000

    while delta_a > delta_a_limit:
        b = acc(3, a, m_primary, m_secondary, sma, period_secondary)
        c = acc(3, a + delta_a, m_primary, m_secondary, sma, period_secondary)
        a += delta_a

        while abs(b) > abs(c):
            a = a - 2 * delta_a
            delta_a /= 10

    l3_secondary_distance = a + sma  # in meters
    print(l3_secondary_distance)

    l3_primary_distance = a  # in meters
    return l3_primary_distance


def compute_lagrage_four(sma):
    l4secondary_distance = sma  # in meters
    print(l4secondary_distance)

    l4primary_distance = sma  # in meters
    print(l4primary_distance)

    l4secondary_distance_x = sma * cos(pi / 3)  # in meters
    print(l4secondary_distance_x)

    l4primary_distance_x = sma * cos(pi / 3)  # in meters
    print(l4primary_distance_x)

    l4secondary_distance_y = sma * sin(pi / 3)  # in meters
    print(l4secondary_distance_y)

    l4primary_distance_y = sma * sin(pi / 3)  # in meters
    print(l4primary_distance_y)


def compute_lagrage_five(sma):
    l5secondary_distance = sma  # in meters
    print(l5secondary_distance)

    l5primary_distance = sma  # in meters
    print(l5primary_distance)

    l5secondary_distance_x = sma * cos(pi / 3)  # in meters
    print(l5secondary_distance_x)

    l5primary_distance_x = sma * cos(pi / 3)  # in meters
    print(l5primary_distance_x)

    l5secondary_distance_y = sma * sin(pi / 3)  # in meters
    print(l5secondary_distance_y)

    l5primary_distance_y = sma * sin(pi / 3)  # in meters
    print(l5primary_distance_y)


def compute_l1_velocity(sma, m_primary, m_secondary):
    l1_primary_distance = compute_lagrage_one(sma, m_primary, m_secondary)
    period_secondary = lagrange(sma, m_primary, m_secondary)[4]
    return 2 * pi * l1_primary_distance / period_secondary  # in m/s


def compute_l2_velocity(sma, m_primary, m_secondary):
    l2_primary_distance = compute_lagrage_two(sma, m_primary, m_secondary)
    period_secondary = lagrange(sma, m_primary, m_secondary)[4]
    return 2 * pi * l2_primary_distance / period_secondary  # in m/s


def compute_l3_velocity(sma, m_primary, m_secondary):
    l3_primary_distance = compute_lagrage_three(sma, m_primary, m_secondary)
    period_secondary = lagrange(sma, m_primary, m_secondary)[4]
    return 2 * pi * l3_primary_distance / period_secondary  # in m/s


def compute_l4_velocities(sma, m_primary, m_secondary):
    period_secondary = lagrange(sma, m_primary, m_secondary)[4]
    return 2 * pi * sma / period_secondary  # in m/s


def compute_l4_ycomponent(v_l4):
    return v_l4 * cos(pi / 3)


def compute_l4_xcomponent(v_l4):
    return v_l4 * sin(pi / 3)


def compute_l5_velocities(sma, m_primary, m_secondary):
    period_secondary = lagrange(sma, m_primary, m_secondary)[4]
    return 2 * pi * sma / period_secondary


def compute_l5_ycomponent(v_l5):
    return v_l5 * sin(pi / 3)


def compute_l5_xcomponent(v_l5):
    return v_l5 * cos(pi / 3)

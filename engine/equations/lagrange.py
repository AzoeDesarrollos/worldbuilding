from math import pi, pow, cos, sin
from engine import q, d

pi = d(pi)
# sma = semi major axis in AU
# m_primary = mass of the star in solar masses
# m_secondary = mass of the planet in earth masses


def _acc(option, d_lp, m_primary, m_secondary, sma, period_secondary):
    g = d(6.6725985e-11)
    bc = sma * m_secondary / (m_secondary + m_primary)

    if option == 3:
        v = d(2) * pi * (d_lp + bc) / period_secondary
        ac = v * v / (d_lp + bc)
    else:
        v = d(2) * pi * (d_lp - bc) / period_secondary
        ac = (v * v) / (d_lp - bc)

    if option == 1:
        ag = (g * m_primary / (d_lp * d_lp)) - (g * m_secondary / ((d_lp - sma) * (d_lp - sma)))

    elif option == 2:
        ag = (g * m_primary / (d_lp * d_lp)) + (g * m_secondary / ((d_lp - sma) * (d_lp - sma)))

    else:
        ag = (g * m_primary / (d_lp * d_lp)) + (g * m_secondary / ((d_lp + sma) * (d_lp + sma)))

    return ac - ag


def _lagrange(sma, m_primary, m_secondary):
    sma *= d(149597870691)
    m_primary *= d(1.98894729428839E+30)
    m_secondary *= d(5.97378250603408E+24)

    period_secondary = d(2) * pi * pow(sma * sma * sma / (d(6.6725985e-11) * (m_primary + m_secondary)), d(0.5))

    delta_a_limit = 1
    for i in reversed(range(15)):
        if sma > pow(10, i):
            delta_a_limit = pow(d('1/10'), (15 - i))
            break

    return d(delta_a_limit), d(m_primary), d(m_secondary), d(sma), d(period_secondary)


def lagrange_one(sma, m_primary, m_secondary, ref='primary'):
    delta_a_limit, m_primary, m_secondary, sma, period_secondary = _lagrange(sma, m_primary, m_secondary)
    a = d(1)
    delta_a = d(1000000000000)

    while delta_a > delta_a_limit:
        condition = True
        while condition:
            b = _acc(1, a, m_primary, m_secondary, sma, period_secondary)
            c = _acc(1, a + delta_a, m_primary, m_secondary, sma, period_secondary)
            a = a + delta_a
            condition = abs(b) > abs(c)
        a = a - d(2) * delta_a
        delta_a /= d(10)

    secondary_distance = -(sma - a)  # in meters
    primary_distance = a  # in meters
    assert ref == 'primary' or ref == 'secondary', 'Requested options are invalid'
    if ref == 'primary':
        return q(primary_distance, 'm')
    elif ref == 'secondary':
        return q(secondary_distance, 'm')


def lagrange_two(sma, m_primary, m_secondary, ref='primary'):
    delta_a_limit, m_primary, m_secondary, sma, period_secondary = _lagrange(sma, m_primary, m_secondary)

    a = sma + d(1)
    delta_a = d(1000000000000)

    while delta_a > delta_a_limit:
        condition = True
        while condition:
            b = _acc(2, a, m_primary, m_secondary, sma, period_secondary)
            c = _acc(2, a + delta_a, m_primary, m_secondary, sma, period_secondary)
            a = a + delta_a
            condition = abs(b) > abs(c)
        a = a - d(2) * delta_a
        delta_a /= d(10)

    secondary_distance = a - sma  # in meters
    primary_distance = a  # in meters
    assert ref == 'primary' or ref == 'secondary', 'Requested options are invalid'
    if ref == 'primary':
        return q(primary_distance, 'm')
    elif ref == 'secondary':
        return q(secondary_distance, 'm')


def lagrange_three(sma, m_primary, m_secondary, ref='primary'):
    delta_a_limit, m_primary, m_secondary, sma, period_secondary = _lagrange(sma, m_primary, m_secondary)

    a = d(1)
    delta_a = d(1000000000000)
    while delta_a > delta_a_limit:
        condition = True
        while condition:
            b = _acc(3, a, m_primary, m_secondary, sma, period_secondary)
            c = _acc(3, a + delta_a, m_primary, m_secondary, sma, period_secondary)
            a = a + delta_a
            condition = abs(b) > abs(c)
        a = a - d(2) * delta_a
        delta_a /= d(10)

    secondary_distance = -(a + sma)  # in meters
    primary_distance = a  # in meters
    assert ref == 'primary' or ref == 'secondary', 'Requested options are invalid'
    if ref == 'primary':
        return q(primary_distance, 'm')
    elif ref == 'secondary':
        return q(secondary_distance, 'm')


def lagrange_four(sma, m_primary, m_secondary, req='distance', ref='primary'):

    sma = _lagrange(sma, m_primary, m_secondary)[3]
    secondary_distance = sma  # in meters
    primary_distance = sma  # in meters
    secondary_distance_x = sma * cos(pi / d(3))  # in meters
    primary_distance_x = sma * cos(pi / d(3))  # in meters
    secondary_distance_y = sma * sin(pi / d(3))  # in meters
    primary_distance_y = sma * sin(pi / d(3))  # in meters

    error = 'Requested options are invalid'
    assert req == 'distance' or (req == 'position' and (ref == 'primary' or ref == 'secondary')), error
    if req == 'distance':
        if ref == 'primary':
            return q(primary_distance, 'm')
        elif ref == 'secondary':
            return q(secondary_distance, 'm')
    elif req == 'position':
        if ref == 'primary':
            return q(primary_distance_x, 'm'), q(primary_distance_y, 'm')
        elif ref == 'secondary':
            return q(secondary_distance_x, 'm'), q(secondary_distance_y, 'm')


def lagrange_five(sma, m_primary, m_secondary, req='distance', ref='primary'):

    sma = _lagrange(sma, m_primary, m_secondary)[3]
    secondary_distance = sma  # in meters
    primary_distance = sma  # in meters
    secondary_distance_x = sma * cos(pi / d(3))  # in meters
    primary_distance_x = sma * cos(pi / d(3))  # in meters
    secondary_distance_y = sma * sin(pi / d(3))  # in meters
    primary_distance_y = sma * sin(pi / d(3))  # in meters
    error = 'Requested options are invalid'
    assert req == 'distance' or (req == 'position' and (ref == 'primary' or ref == 'secondary')), error
    if req == 'distance':
        if ref == 'primary':
            return q(primary_distance, 'm')
        elif ref == 'secondary':
            return q(secondary_distance, 'm')
    elif req == 'position':
        if ref == 'primary':
            return q(primary_distance_x, 'm'), q(primary_distance_y, 'm')
        elif ref == 'secondary':
            return q(secondary_distance_x, 'm'), q(secondary_distance_y, 'm')


def compute_l1v(sma, m_primary, m_secondary):
    primary_distance = lagrange_one(sma, m_primary, m_secondary)[0].m
    period_secondary = _lagrange(sma, m_primary, m_secondary)[4]
    return q(d(2) * pi * primary_distance / period_secondary, 'm/s')


def compute_l2v(sma, m_primary, m_secondary):
    primary_distance = lagrange_two(sma, m_primary, m_secondary)[0].m
    period_secondary = _lagrange(sma, m_primary, m_secondary)[4]
    return q(d(2) * pi * primary_distance / period_secondary, 'm/s')


def compute_l3v(sma, m_primary, m_secondary):
    primary_distance = lagrange_three(sma, m_primary, m_secondary)[0].m
    period_secondary = _lagrange(sma, m_primary, m_secondary)[4]
    return q(d(2) * pi * primary_distance / period_secondary, 'm/s')


def compute_l4v(sma, m_primary, m_secondary):
    period_secondary = _lagrange(sma, m_primary, m_secondary)[4]
    return q(d(2) * pi * sma / period_secondary, 'm/s')


def compute_vl5(sma, m_primary, m_secondary):
    period_secondary = _lagrange(sma, m_primary, m_secondary)[4]
    return q(d(2) * pi * sma / period_secondary, 'm/s')


def compute_vl5_xy_components(sma, m_primary, m_secondary):
    v_l5 = compute_vl5(sma, m_primary, m_secondary)
    x_component = v_l5 * cos(pi / d(3))
    y_component = v_l5 * sin(pi / d(3))
    return x_component, y_component


def compute_vl4_xy_components(sma, m_primary, m_secondary):
    v_l4 = compute_l4v(sma, m_primary, m_secondary)
    x_component = v_l4 * sin(pi / d(3))
    y_component = v_l4 * cos(pi / d(3))
    return x_component, y_component


def get_lagrange_points(semi_major_axis, star_mass, body_mass):
    d = {'l1': lagrange_one(semi_major_axis, star_mass, body_mass, ref='secondary'),
         'l2': lagrange_two(semi_major_axis, star_mass, body_mass, ref='secondary'),
         'l3': lagrange_three(semi_major_axis, star_mass, body_mass, ref='secondary'),
         'l4': lagrange_four(semi_major_axis, star_mass, body_mass, req='distance', ref='secondary').to('au'),
         'l5': lagrange_five(semi_major_axis, star_mass, body_mass, req='distance', ref='secondary').to('au')}
    return d

def major_tides(object_diam, major_mass, major_sma):
    return (2230000 * major_mass * object_diam) / (major_sma ** 3)


def minor_tides(object_diam, stellar_mass, object_sma):
    return (0.46 * stellar_mass * object_diam) / (object_sma ** 3)


def is_tidally_locked(object_tides, system_age, parent_mass) -> bool:
    return ((object_tides * system_age) / parent_mass) >= 50


def moon_tides(moon_mass, planet_diam, moon_sma):
    return major_tides(planet_diam, moon_mass, moon_sma)

# the amount of time it takes for the "little correction cause of how the moon orbits" can be calculated by:
# time = day^2 / (month - day), where day is how long it takes your planet to rotate on its axis, and month
# is the lunar period. add that to your day length to get the total time it takes to rotate through 2 high
# tides and 2 low tides

# # double planet
# planet_b_mass = 1  # earth masses
# planet_b_diam = 1  # earth diameters
# planet_b_sma = 1  # earth diameters
#
# # tides on planet_b
# planet_b_tides = major_tides(planet_diam, planet_b_mass, planet_b_sma)
#
# std_high = planet_b_tides * 0.54  # meters
# std_low = -std_high
#
# spring_high = (planet_b_tides + solar_tides) * 0.54  # meters
# spring_low = -spring_high
#
# neap_high = (planet_b_tides - solar_tides) * 0.54  # meters
# neap_low = -neap_high
#
# planet_b_tidally_locked_to_planet_a = is_tidally_locked((planet_b_tides + solar_tides), system_age, planet_mass)
#
# # tides on planet_a
# planet_a_tides = (2230000 * planet_mass * planet_b_diam) / planet_b_sma ** 3
#
# std_high = planet_a_tides * 0.54  # meters
# std_low = -std_high
#
# spring_high = (planet_a_tides + solar_tides) * 0.54  # meters
# spring_low = -spring_high
#
# neap_high = (planet_a_tides - solar_tides) * 0.54  # meters
# neap_low = -neap_high
#
# planet_a_tidally_locked_to_planet_b = is_tidally_locked((planet_a_tides + solar_tides), system_age, planet_b_mass)
#

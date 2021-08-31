# single moon effect on planet
star_mass = 1  # solar masses
system_age = 1  # billions of years
planet_mass = 1  # earth masses
planet_diam = 1  # earth diameters
planet_sma = 1  # au
moon_mass = 1  # earth masses
moon_diam = 1  # earth diameters
moon_sma = 1  # earth diameters


def major_tides(object_diam, major_mass, major_sma):
    return (2230000 * major_mass * object_diam) / (major_sma ** 3)


def minor_tides(object_diam, stellar_mass, object_sma):
    return (0.46 * stellar_mass * object_diam) / (object_sma ** 3)


def is_tidally_locked(object_tides, system_age, parent_mass) -> bool:
    return object_tides * system_age / parent_mass >= 50


def moon_tides(moon_mass, planet_diam, moon_sma):
    return major_tides(planet_diam, moon_mass, moon_sma)


lunar_tides = major_tides(planet_diam, moon_mass, moon_diam)
solar_tides = minor_tides(planet_diam, star_mass, planet_sma)

std_high = lunar_tides * 0.54  # meters
std_low = -std_high

spring_high = (lunar_tides + solar_tides) * 0.54  # meters
spring_low = -spring_high

neap_high = (lunar_tides - solar_tides) * 0.54  # meters
neap_low = -neap_high

planet_tidally_locekd_to_moon = is_tidally_locked(lunar_tides, system_age, planet_mass)
planet_tidally_locekd_to_star = is_tidally_locked(solar_tides, system_age, star_mass)
moon_tidally_locekd_to_planet = is_tidally_locked(lunar_tides + solar_tides, system_age, moon_mass)

# # habitable moon
# planet_tides = major_tides(moon_diam, planet_mass, moon_sma)
# solar_tides = minor_tides(moon_sma, star_mass, planet_sma)
#
# std_high = planet_tides * 0.54  # meters
# std_low = -std_high
#
# spring_high = (planet_tides + solar_tides) * 0.54  # meters
# spring_low = -spring_high
#
# neap_high = (planet_tides - solar_tides) * 0.54  # meters
# neap_low = -neap_high
#
# habitable_moon_tidally_locekd_to_planet = is_tidally_locked((planet_tides + solar_tides), system_age, moon_mass)
#
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
# # multi star/moon systems
# star_b_mass = 1
#
# moon_a_mass = 1
# moon_a_diam = 1
# moon_a_sma = 1
#
# moon_b_mass = 1
# moon_b_diam = 1
# moon_b_sma = 1
#
# moon_c_mass = 1
# moon_c_diam = 1
# moon_c_sma = 1
#
# moon_d_mass = 1
# moon_d_diam = 1
# moon_d_sma = 1
#
# planet_mass = 1  # earth masses
# planet_diam = 1  # earth diameters
# planet_sma = 1  # au
#
# moon_a_tides = moon_tides(moon_a_mass, planet_diam, moon_a_sma)
# moon_b_tides = moon_tides(moon_b_mass, planet_diam, moon_b_sma)
# moon_c_tides = moon_tides(moon_c_mass, planet_diam, moon_c_sma)
# moon_d_tides = moon_tides(moon_d_mass, planet_diam, moon_d_sma)
#
# star_a_tides = (0.46 * star_mass * planet_diam) / planet_sma ** 3
# star_b_tides = (0.46 * star_b_mass * planet_diam) / planet_sma ** 3
#
# all_lunar_tides = sum(moon_a_tides, moon_b_tides, moon_c_tides, moon_d_tides)
#
# std_high = all_lunar_tides * 0.54
# std_low = -std_high
#
# spring_high = (all_lunar_tides + sum(star_a_tides, star_b_tides)) * 0.54  # meters
# spring_low = -spring_high
#
# neap_high = (all_lunar_tides - sum(star_a_tides, star_b_tides)) * 0.54  # meters
# neap_low = -neap_high
#
# planet_a_tidally_locked = (all_lunar_tides + sum(star_a_tides, star_b_tides)) * system_age / planet_mass >= 50
#
# moon_a_tidally_locked = is_tidally_locked(moon_a_tides, moon_a_mass, system_age)
# moon_b_tidally_locked = is_tidally_locked(moon_b_tides, moon_b_mass, system_age)
# moon_c_tidally_locked = is_tidally_locked(moon_c_tides, moon_c_mass, system_age)
# moon_d_tidally_locked = is_tidally_locked(moon_d_tides, moon_d_mass, system_age)

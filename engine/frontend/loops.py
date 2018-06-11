from .graph import graph_loop
from engine.equations import Planet, Star, Orbit
from engine.equations.planet import Terrestial, GasDwarf
from .subselector import subselector


def planet_loop():
    opciones = ['Terrestial',
                'Dwarf',
                'Gas Giant',
                'Puffy Giant',
                'Gas Dwarf'
                ]

    p = subselector('what type of planet? Pick one', opciones, 'Type')
    m, r = 0, 0
    name = ''
    if p == 'Terrestial':
        data = graph_loop(*Terrestial)
        m, r = data['mass'], data['radius']

    elif p == 'Gas Dwarf':
        data = graph_loop(*GasDwarf)
        m, r = data['mass'], data['radius']

    elif p == 'Gas Giant':
        name = input('Name: ')
        print('The mass range for gas giants is:')
        print('10 earth masses to 13 jupiter masses')
        print('\nIndicate the scale after the number')
        print('"# e" (for earth scale)', '"# j" (for jupiter scale)', sep='\n')

        # mass = input('mass: ')
        # value,scale = mass.split()
        # if scale == 'e'

    planet = Planet(name, mass=m, radius=r)
    return planet.export()


def star_loop():
    name = input('\nName: ')
    mass = input('Mass: ')
    s = Star(name, float(mass))
    return s.export()


def orbit_loop():
    name = input('\nName: ')
    star_mass = float(input('Star mass: '))
    a = float(input('Semi-major axis:'))
    e = float(input('Eccentricity: '))
    i = float(input('Inclination: '))

    o = Orbit(star_mass, a, e, i, name)
    return o.export()

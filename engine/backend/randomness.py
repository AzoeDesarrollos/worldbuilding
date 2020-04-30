from random import seed, random, uniform, choice
from datetime import datetime
from .util import abrir_json, guardar_json
from os import getcwd, path

file = path.join(getcwd(), 'data', 'seed.json')
if path.exists(file):
    key = abrir_json(file)
else:
    key = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])
    guardar_json(file, key)

seed(key)

__all__ = [
    'roll',
    'choice',
    'random_mass'
]


def roll(a: float = 0.0, b: float = 0.0):
    """Base function to generate random float values"""
    if a != 0.0 and b != 0.0:
        return uniform(a, b)
    else:
        return random()


def random_m():
    """Returns a value for the mass of an M-Star"""
    return roll(0.08, 0.45)


def random_k():
    """Returns a value for the mass of an K-Star"""
    return roll(0.45, 0.8)


def random_g():
    """Returns a value for the mass of an G-Star"""
    return roll(0.8, 1.04)


def random_f():
    """Returns a value for the mass of an F-Star"""
    return roll(1.04, 1.4)


def random_a():
    """Returns a value for the mass of an A-Star"""
    return roll(1.4, 2.1)


def random_b():
    """Returns a value for the mass of an B-Star"""
    return roll(2.1, 16.0)


def random_o():
    """Returns a value for the mass of an O-Star"""
    return roll(16.0, 50.0)


def random_mass(cls: str = 'G'):
    """Returns the mass of a star of the given classification"""
    if cls == 'O':
        return random_o()
    elif cls == 'B':
        return random_b()
    elif cls == 'A':
        return random_a()
    elif cls == 'F':
        return random_f()
    elif cls == 'G':
        return random_g()
    elif cls == 'K':
        return random_k()
    elif cls == 'M':
        return random_m()
    else:
        raise ValueError('Invalid Star Classification')

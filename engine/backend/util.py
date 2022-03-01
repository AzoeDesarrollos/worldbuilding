from math import trunc, ceil, floor, sqrt
from .eventhandler import EventHandler
from random import random, uniform
from datetime import datetime
from pint import UnitRegistry
from os import getcwd, path
from pygame import quit
from sys import exit
import json


def roll(a: float = 0.0, b: float = 0.0):
    """Base function to generate random float values"""
    if a != 0.0 or b != 0.0:
        return uniform(a, b)
    else:
        return random()


def decimal_round(number: float):
    """
    :rtype: int
    """
    entero = trunc(number)
    decimal = number - entero
    assert type(number) is float
    if decimal >= 0.5:
        return int(ceil(number))
    else:
        return int(floor(number))


def add_decimal(text: str):
    if text.startswith('-'):
        negative = True
    else:
        negative = False
    if not float(text) > 1000:
        if 'e' in text:
            return float(text)
        else:
            return str(round(float(text), 3))

    text = str(abs(float(text)))
    if 'e' in text:
        txt = '{:0.3e}'.format(float(text))
    else:
        txt = text

    decimal = []
    count = 0
    p_idx = txt.find('.')
    if p_idx > 1:
        last_p = 0

        for i in reversed(range(len(txt[0:p_idx]))):
            count += 1
            if count == 3:
                if i > last_p:
                    decimal.append(txt[i:])
                    last_p = i
                else:
                    decimal.append(txt[i:count + i])
                count = 0
        else:
            if count > 0:
                # noinspection PyUnboundLocalVariable
                decimal.append(txt[i:count + i])

        decimal.reverse()
        return ','.join(decimal) if negative is False else '-' + ','.join(decimal)

    else:
        return txt


def guardar_json(ruta, datos, encoding='utf-8'):
    with open(ruta, mode='w', encoding=encoding) as file:
        json.dump(datos, file, ensure_ascii=False, indent=2, separators=(',', ':'), sort_keys=True)


def abrir_json(ruta, encoding='utf-8'):
    with open(ruta, encoding=encoding) as file:
        return json.load(file)


def salir_handler(event):
    data = event.data.get('mensaje', '')
    print('Saliendo...\nStatus: ' + data)
    quit()
    exit()


def generate_id():
    now = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])
    now = now[0:-5] + '-' + now[-5:]
    return now


def interpolate(x, x1, x2, y1, y2):
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    return a * x + b


def small_angle_aproximation(body, distance):
    d = body.radius.to('km').m * 2
    sma = q(d / distance, 'radian').to('degree')
    decimals = 1
    while round(sma, decimals) == 0:
        decimals += 1
    return round(sma, decimals)


def eucledian_distance(p1, p2):
    if len(p1) == 3:
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        d = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    elif len(p1) == 2:
        x1, y1 = p1
        x2, y2 = p2
        d = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    else:
        x1 = p1
        x2 = p2
        d = x2 - x1
    return d


EventHandler.register(salir_handler, 'salir')

if path.exists(path.join(getcwd(), "lib")):
    filepath = path.join(getcwd(), 'lib', 'engine')
else:
    filepath = path.join(getcwd(), 'engine')

ureg = UnitRegistry()
ureg.load_definitions(path.join(filepath, 'unit_definitions.txt'))
q = ureg.Quantity

material_densities = abrir_json(path.join(filepath, 'material_densities.json'))
molecular_weight = abrir_json(path.join(filepath, 'molecular_weight.json'))
recomendation = abrir_json(path.join(filepath, 'recomendation.json'))
albedos = abrir_json(path.join(filepath, 'albedo_values.json'))

__all__ = [
    'generate_id',
    'roll',
    'guardar_json',
    'abrir_json',
    'decimal_round',
    'add_decimal',
    'interpolate',
    'small_angle_aproximation',
    "material_densities",
    "molecular_weight",
    "recomendation",
    "albedos",
    "q",
    "eucledian_distance"
]

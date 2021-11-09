from .eventhandler import EventHandler
from math import trunc, ceil, floor
from random import random, uniform
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


EventHandler.register(salir_handler, 'salir')

__all__ = [
    'roll',
    'guardar_json',
    'abrir_json',
    'decimal_round',
    'add_decimal'
]

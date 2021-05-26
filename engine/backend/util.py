from .eventhandler import EventHandler
from os.path import exists, join
from pygame import quit
from os import getcwd
from sys import exit
import json


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
        return ','.join(decimal) if negative is False else '-'+','.join(decimal)

    else:
        return txt


def prime_factors(n):
    """Returns all the prime factors of a positive integer"""

    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n:
            if n > 1:
                factors.append(n)
            break
    return factors


def collapse_factor_lists(a: list, b: list):
    """Multiplies all the common factors in the
    two lists, and returns them as a pair of
    integers."""

    def collapse(factors):
        n = factors[0]
        for factor in factors[1:]:
            n *= factor
        return n

    for i in list(set(a).intersection(b)):
        a.remove(i)
        b.remove(i)

    return collapse(a), collapse(b)


def guardar_json(nombre, datos, encoding='utf-8'):
    with open(nombre, mode='w', encoding=encoding) as file:
        json.dump(datos, file, ensure_ascii=False, indent=2, separators=(',', ':'), sort_keys=True)


def abrir_json(archivo, encoding='utf-8'):
    with open(archivo, encoding=encoding) as file:
        return json.load(file)


def load_from_data(body, filename):
    return body(abrir_json(filename))


def salir_handler(event):
    data = event.data.get('mensaje', '')
    print('Saliendo...\nStatus: ' + data)
    quit()
    exit()


route = join(getcwd(), 'data', 'savedata.json')
if not exists(route):
    guardar_json(route, {})

EventHandler.register(salir_handler, 'salir')

__all__ = [
    'guardar_json',
    'abrir_json',
    'load_from_data',
    'add_decimal',
    'collapse_factor_lists',
    'prime_factors'
]

from .eventhandler import EventHandler
import csv
import json
from math import trunc, ceil, floor
from os.path import exists, join
from os import getcwd


def decimal_round(number: float):
    """
    :rtype: int
    """
    entero = trunc(number)
    decimal = number-entero
    assert type(number) is float
    if decimal >= 0.5:
        return int(ceil(number))
    else:
        return int(floor(number))


class MyCSV(csv.excel):
    delimiter = ';'


def read_csv(ruta):
    """Lee archivos CSV y los devuelve como una lista."""

    table = []
    with open(ruta, encoding='windows-1252') as file:
        data = csv.reader(file, dialect=MyCSV)
        for row in data:
            for i, value in enumerate(row[1:], 1):
                # noinspection PyTypeChecker
                row[i] = float(row[i])
            table.append(row)

    return table


def open_float_list_txt(ruta):
    lines = []
    with open(ruta, mode='rt', encoding='utf-8') as file:
        for line in file.readlines():
            lines.append(float(line.rstrip('\n')))
        return lines


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


ruta = join(getcwd(), 'data', 'savedata.json')
if not exists(ruta):
    guardar_json(ruta, {})


EventHandler.register(salir_handler, 'salir')

__all__ = [
    'read_csv',
    'open_float_list_txt',
    'guardar_json',
    'abrir_json',
    'load_from_data',
    'decimal_round'
]

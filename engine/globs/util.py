import json


def guardar_json(nombre, datos, encoding='utf-8'):
    with open(nombre, mode='w', encoding=encoding) as file:
        json.dump(datos, file, ensure_ascii=False, indent=2, separators=(',', ':'), sort_keys=True)


def abrir_json(archivo, encoding='utf-8'):
    with open(archivo, encoding=encoding) as file:
        return json.load(file)


def load_from_data(body, filename):
    return body(abrir_json(filename))

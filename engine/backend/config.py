from .util import guardar_json, abrir_json
from os import path, getcwd


class Config:
    _default = {
        'mode': 0
    }
    _data = None
    _ruta = path.join(getcwd(), 'data', 'config.json')

    @classmethod
    def init(cls):
        if not path.exists(cls._ruta):
            guardar_json(cls._ruta, cls._default)
            cls._data = cls._default.copy()
        else:
            cls._data = abrir_json(cls._ruta)

    @classmethod
    def get(cls, key):
        if key in cls._data:
            return cls._data[key]
        else:
            raise KeyError(f'The key {key} was not found')

    @classmethod
    def set(cls, key, dato):
        if key in cls._data:
            cls._data[key] = dato
            cls._save_interal()
        else:
            raise KeyError(f"The key {key} doesn't exists")

    @classmethod
    def _save_interal(cls):
        guardar_json(cls._ruta, cls._data)


Config.init()

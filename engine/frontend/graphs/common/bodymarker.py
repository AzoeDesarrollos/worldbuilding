from engine.backend.eventhandler import EventHandler
from pygame import Surface, SRCALPHA
from pygame.sprite import Sprite


class BodyMarker(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self.crear('black')
        self.rect = self.image.get_rect(center=(x, y))

    @staticmethod
    def crear(color):
        graph = [
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ]
        image = Surface([len(graph)] * 2, SRCALPHA)
        for y, line in enumerate(graph):
            for x, j in enumerate(line):
                if j:
                    image.set_at((x, y), color)

        return image


class MarkersManager:
    _dict = None
    _initialized = False
    _active = None
    _current = None

    @classmethod
    def init(cls):
        cls._dict = {}
        cls._initialized = True
        EventHandler.register(cls.dissolve_system, 'DissolveSystem')

    @classmethod
    def populate_graphs(cls, star_id):
        if not cls._initialized:
            cls.init()

        cls._dict[star_id] = {
            'graph': [],
            'gasgraph': [],
            'dwarfgraph': [],
        }

    @classmethod
    def dissolve_system(cls, event):
        for star in event.data['system'].composition():
            if star.parent.id in cls._dict:
                star_id = star.parent.id
                cls.unpopulate(star_id)

    @classmethod
    def unpopulate(cls, star_id):
        cls._active = None
        cls._current = None
        cls.clear_key(star_id)

    @classmethod
    def graph_markers(cls, star_id):
        cls._active = 'graph'
        cls._current = star_id
        return cls._dict[star_id]['graph']

    @classmethod
    def gas_markers(cls, star_id):
        cls._active = 'gasgraph'
        cls._current = star_id
        return cls._dict[star_id]['gasgraph']

    @classmethod
    def dwarf_markers(cls, star_id):
        cls._active = 'dwarfgraph'
        cls._current = star_id
        return cls._dict[star_id]['dwarfgraph']

    @classmethod
    def set_marker(cls, marker):
        cls._dict[cls._current][cls._active].append(marker)

    @classmethod
    def clear_key(cls, star_id):
        if star_id in cls._dict:
            del cls._dict[star_id]

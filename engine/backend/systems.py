from . import EventHandler


class Systems:
    _systems = None
    loose_stars = None
    save_data = {
        'Galaxies': {},
        'Neighbourhoods': {},
        'Asteroids': {},
        'Planets': {},
        'Satellites': {},
        'Stars': {},
        'Single Systems': {},
        'Binary Systems': {},
        'Planetary Orbits': {},
        'Stellar Orbits': {},
        'Compact Objects': {},
    }

    @classmethod
    def get_system_by_id(cls, id_number):
        systems = [s for s in cls._systems if s.id == id_number]
        if len(systems) == 1:
            return systems[0]
        else:
            return None

    @classmethod
    def compound_save_data(cls, event):
        for key in event.data:
            if len(event.data[key]):
                if key == 'Single Systems':
                    if len(cls.save_data[key]) == 0:
                        cls.save_data[key] = {}
                    for key_id in event.data[key]:
                        cls.save_data[key][key_id] = event.data[key][key_id]
                cls.save_data[key].update(event.data[key])

        if not EventHandler.is_quequed('SaveDataFile'):
            EventHandler.trigger('SaveDataFile', 'EngineData', cls.save_data)

    @classmethod
    def load_data(cls, event):
        empty = []
        for key in cls.save_data:
            if cls.save_data[key] == {}:
                empty.append(True)
            else:
                empty.append(False)
        if any(empty):
            cls.save_data.update(event.data)
        else:
            EventHandler.allowed = False


EventHandler.register(Systems.compound_save_data, 'SaveData')

from . import EventHandler, guardar_json, abrir_json
from os.path import join, exists
from itertools import cycle
from .config import Config
from os import getcwd


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
    _current = None
    _system_cycler = None

    bodies_markers = {}

    restricted_mode = True

    rogue = None
    planetary = None
    universe = None

    just_stars = None
    # the difference between just_stars and loose_stars is that loose_stars changes when the stars form a system,
    # whereas just_stars is just the stars (duh), regardless if they are part of a system or not, and thus is more
    # static.

    _rogue_planets_warning_issued = False

    @classmethod
    def import_clases(cls, rogues=None, planetary=None, universe=None):
        # this method exists to avert a circular import.
        if rogues is not None:
            cls.rogue = rogues
        if planetary is not None:
            cls.planetary = planetary
        if universe is not None:
            cls.universe = universe

    @classmethod
    def init(cls):
        cls._systems = [cls.rogue]
        cls.loose_stars = []
        cls.just_stars = []
        cls._system_cycler = cycle(cls._systems)
        cls._current = next(cls._system_cycler)

        EventHandler.register(cls.save, "SaveDataFile")
        EventHandler.register(cls.compound_save_data, "SaveData")
        EventHandler.register(cls.load_data, 'LoadData')

        ruta = join(getcwd(), 'data', 'savedata.json')
        if not exists(ruta):
            guardar_json(ruta, cls.save_data)

    @classmethod
    def set_mode(cls, mode):
        if mode == 'restricted':
            cls.restricted_mode = True
        elif mode == 'unrestricted':
            cls.restricted_mode = False

    @classmethod
    def set_planetary_system(cls, star):
        if star in cls.loose_stars:
            cls.loose_stars.remove(star)
        if star.letter == 'S':
            for sub in star:
                for system in cls._systems:
                    if system.star_system == sub:
                        system.update()
                cls.set_planetary_system(sub)
        else:
            system = cls.planetary(star)
            if system not in cls._systems:
                cls.populate(star.id)
                cls._systems.append(system)
                if len(cls._systems) == 1:
                    cls._current = next(cls._system_cycler)

    @classmethod
    def populate(cls, star_id):
        cls.bodies_markers[star_id] = {
            'graph': [],
            'gasgraph': [],
            'dwarfgraph': [],
        }

    @classmethod
    def unpopulate(cls, star_id):
        if star_id in cls.bodies_markers:
            del cls.bodies_markers[star_id]

    @classmethod
    def unset_system(cls, star):
        system = cls.get_system_by_star(star)
        if star.letter is not None:
            if star.letter == system.star_system.primary:
                cls.loose_stars.append(system.star_system.secondary)
            elif star == system.star_system.secondary:
                cls.loose_stars.append(system.star_system.primary)
        else:
            cls.loose_stars.append(star)
        cls._systems.remove(system)
        cls.unpopulate(system.id)

    @classmethod
    def dissolve_system(cls, system):
        planetary_system = None
        if system.letter is None:
            cls.loose_stars.append(system)
            planetary_system = cls.get_system_by_star(system)
        else:
            for star in system:
                if star.letter is not None:
                    cls.dissolve_system(star)
                else:
                    cls.loose_stars.append(star)

        if planetary_system is None:
            planetary_system = cls.get_system_by_star(system)
        if planetary_system in cls._systems:
            cls._systems.remove(planetary_system)
            cls.unpopulate(planetary_system.id)
            system.flag()
            for astro in planetary_system.astro_bodies:
                astro.flag()
            if planetary_system == cls._current:
                cls.cycle_systems()

    @classmethod
    def get_system_by_id(cls, id_number):
        systems = [s for s in cls._systems if s.id == id_number]
        if len(systems) == 1:
            return systems[0]
        else:
            return None

    @classmethod
    def get_star_by_id(cls, id_number):
        for star in cls.loose_stars:
            if star.id == id_number:
                return star
        for system in cls._systems:
            if system is not cls.rogue:
                if id_number == system.id:
                    return system.star_system
                else:
                    for star in system:
                        if star.id == id_number:
                            return star

    @classmethod
    def get_system_by_star(cls, star):
        if star is not None:
            star = cls.find_parent(star)
            for system in cls._systems:
                if hasattr(system, 'letter') and system.letter is not None:
                    if any([body == star for body in system.star_system.composition()]):
                        return system
                elif system.star_system == star:
                    return system

    @classmethod
    def find_parent(cls, body):
        if body.parent is None:
            return body
        else:
            return cls.find_parent(body.parent)

    @classmethod
    def cycle_systems(cls, panel_name=None):
        warning = 'Rogue Planets, by definition, do not have orbits, so they are unable to exist in this panel.'
        if len(cls._systems):
            system = next(cls._system_cycler)
            if panel_name == 'Orbit' and not system.is_a_system:
                if Config.get('repeat warnings') is True or not cls._rogue_planets_warning_issued:
                    cls._rogue_planets_warning_issued = True
                    raise AssertionError(warning)
                system = next(cls._system_cycler)
            cls._current = system

    @classmethod
    def get_current(cls):
        if cls._current is not None:
            return cls._current

    @classmethod
    def get_current_star(cls):
        if cls._current is not None:
            if cls._current is cls.rogue:
                return cls.rogue
            else:
                return cls._current.star_system

    @classmethod
    def get_current_id(cls, instance):
        system = cls.get_current()
        if system is not None:
            idx = system.id
        else:
            idx = instance.last_idx
        return idx

    @classmethod
    def get_planetary_systems(cls):
        if len(cls._systems):
            return cls._systems
        else:
            return []

    @classmethod
    def get_stars_and_systems(cls):
        everything = [i for i in cls.loose_stars + cls._systems]
        everything.remove(cls.rogue)
        return everything

    @classmethod
    def get_only_stars(cls):
        stars = cls.loose_stars.copy()
        systems = cls._systems.copy()
        systems.remove(cls.rogue)
        for system in systems:
            stars.append(system.star_system)

        return stars

    @classmethod
    def add_star(cls, star):
        if star not in cls.loose_stars:
            cls.loose_stars.append(star)
        if star not in cls.just_stars:
            cls.just_stars.append(star)
        astro_bodies = [i for i in cls.universe.astro_bodies if i.celestial_type != 'star']
        for body in astro_bodies:
            if body.orbit is not None:
                cls.universe.visibility_of_stars(body)

    @classmethod
    def remove_star(cls, star):
        if cls.universe.contains(star):
            cls.universe.remove_astro_obj(star)

        if star in cls.loose_stars:
            cls.loose_stars.remove(star)
        else:
            system = cls.get_system_by_star(star)
            if system is not None:
                for astrobody in system.astro_bodies:
                    astrobody.flag()
                star = system.star_system
                cls.unset_system(star)

        if not len(cls.loose_stars) and not len(cls._systems):
            cls._current = None

    @classmethod
    def save(cls, event):
        ruta = join(getcwd(), 'data', 'savedata.json')
        data = abrir_json(ruta)
        read_data = abrir_json(ruta)
        keys = 'Galaxies,Neighbourhoods,Stars,Single Systems,Binary Systems,Stellar Orbits,'
        keys += 'Planetary Orbits,Asteroids,Planets,Satellites,Compact Objects'
        for key in keys.split(','):
            new_data = event.data.get(key, [])
            for item_id in new_data:
                item_data = new_data[item_id]
                if item_id in read_data[key] and type(data[key][item_id]) is dict:
                    data[key][item_id].update(item_data)
                else:
                    data[key][item_id] = item_data

        copy_data = data.copy()
        delete = {}
        for key in keys.split(','):
            if key not in ('Galaxies', 'Neighbourhoods', 'Compact Objects'):
                for idx in copy_data[key]:
                    datos = copy_data[key][idx]
                    if 'system' in datos:
                        system = cls.get_system_by_id(datos['system'])
                    elif 'star_id' in copy_data[key][idx]:
                        star = cls.get_star_by_id(datos['star_id'])
                        system = cls.get_system_by_star(star)
                    else:
                        star = cls.get_star_by_id(idx)
                        system = cls.get_system_by_star(star)

                    if system is not None:
                        body = system.get_astrobody_by(idx, tag_type='id')
                        if body is not False and body.flagged:
                            if key not in delete:
                                delete[key] = [data[key][idx]]
                            else:
                                delete[key].append(data[key][idx])

        else:
            for key in delete:
                for idx in delete[key]:
                    del data[key][idx]

            guardar_json(ruta, data)

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

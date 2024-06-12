from engine.backend import q, generate_id, roll, turn_into_roman, EventHandler
from engine.frontend.graphs.common import MarkersManager
from .orbit import GalacticNeighbourhoodOrbit
from .planetary_system import PlanetarySystem
from .system_single import SingleSystem
from itertools import cycle


class DefinedNeighbourhood:
    idx = None

    pre_processed_system_positions = None

    proto_stars = None

    quantities = None

    nei_seed = None

    orbit = None

    proto_systems = None

    flagged = False

    def __init__(self, idx, data):
        self.idx = idx
        self.id = data['id'] if 'id' in data else generate_id()
        self.nei_seed = data['seed'] if 'seed' in data else self._roll_seed()
        self.location = data['location']
        self.radius = data['radius']
        self.density = data['density']
        self.other = data['other']
        self.proto_stars = []
        self.proto_systems = []
        self.pre_processed_system_positions = {
            "Single": [],
            "Binary": [],
            "Triple": [],
            "Multiple": []
        }
        self.quantities = {
            "Single": 0,
            "Binary": 0,
            "Triple": 0,
            "Multiple": 0
        }
        self.orbit = GalacticNeighbourhoodOrbit(self.location)
        self.true_systems = []
        self.planetary_systems = []
        self.system_cycler = cycle(self.planetary_systems)
        self._current_planetary = None

        EventHandler.register(self.del_true_system, 'DissolveSystem')

    def set_quantity(self, key, quantity):
        self.quantities[key] = quantity

    def add_true_system(self, system):
        if system not in self.true_systems:
            self.true_systems.append(system)

    def del_true_system(self, event):
        system = event.data['system']
        if system in self.true_systems:
            system.flag()
            self.true_systems.remove(system)
            if hasattr(system, 'planetary'):
                if system.planetary == self._current_planetary:
                    self.cycle_systems()
                self.planetary_systems.remove(system.planetary)

    def add_proto_system(self, system):
        if system not in self.proto_systems:
            self.proto_systems.append(system)

    def remove_proto_system(self, system):
        if system in self.proto_systems:
            self.proto_systems.remove(system)

    def get_system(self, id):
        for system in self.true_systems:
            if system.id == id:
                return system

    def __repr__(self):
        idx = self.id.split('-')[1]
        return f'{idx}'

    def process_data(self, data):
        for tag in 'Single Systems', 'Binary Systems':
            tag_name = tag.split()[0]
            for system_id in data[tag]:
                if data[tag][system_id]['neighbourhood_id'] == self.id:
                    system_data = data[tag][system_id]
                    if 'position' in system_data:
                        x = system_data['position']['x']
                        y = system_data['position']['y']
                        z = system_data['position']['z']
                        self.pre_processed_system_positions[tag_name].append((x, y, z))

    def add_proto_stars(self, list_of_dicts):
        for data in list_of_dicts:
            data.update({'neighbourhood_idx': self.idx - 1})
            star = ProtoStar(data)
            self.proto_stars.append(star)

    def __eq__(self, other):
        equal = self.id == other.id
        equal = equal and self.location == other.location
        equal = equal and self.radius == other.radius
        equal = equal and self.density == other.density
        return equal

    @staticmethod
    def _roll_seed():
        rolled = roll(1.0, 2 * 10 ** 8)
        return int(rolled)

    def cycle_systems(self):
        self._current_planetary = next(self.system_cycler)
        return self._current_planetary

    def get_current(self):
        return self._current_planetary

    def systems(self):
        return self.planetary_systems

    def set_planetary_systems(self):
        for system in self.true_systems:
            if system.letter == 'P' or system.letter is None:  # Single and P-Type Systems
                self.set_planetary_system(system)
            elif system.letter == 'S':
                for star in system:
                    if hasattr(star, 'compact_subtype'):  # compact objects, such as brown dwarfs
                        single = SingleSystem(star, neighbourhood_id=self.id)
                        single.cartesian = system.cartesian
                        self.set_planetary_system(single)
                    elif star.celestial_type == 'star':  # M Stars companions, tipically
                        single = SingleSystem(star, neighbourhood_id=self.id)
                        single.cartesian = system.cartesian
                        self.set_planetary_system(single)
                    elif star.celestial_type == 'system' and star.letter == 'P':  # Triple System's Primary
                        self.set_planetary_system(star)
                        star.cartesian = system.cartesian

    def set_planetary_system(self, star):
        system = PlanetarySystem(star)
        self.planetary_systems.append(system)

        MarkersManager.populate_graphs(star.id)
        if len(self.planetary_systems) == 1:
            self._current_planetary = next(self.system_cycler)

    @property
    def current_planetary(self):
        return self._current_planetary

    def flag(self):
        self.flagged = True


class ProtoSystem:
    celestial_type = 'system'
    name = None

    orbit = None

    neighbourhood_id = None

    def __init__(self, data):
        self.composition = data['composition']
        self.location = data['location']
        self.idx = data['idx']
        self.id = data['id'] if 'id' in data else generate_id()
        self.neighbourhood_id = data['neighbourhood_id']

    def __repr__(self):
        return f'{self.composition.title()} ProtoSystem'


class ProtoStar:
    celestial_type = 'star'

    def __init__(self, data):
        self.cls = data['class']
        self.id = generate_id()
        self.idx = data['idx']
        self.neighbourhood_idx = data['neighbourhood_idx']

        m_min, m_max, mass = 0, 0, 0
        b = self.idx + self.neighbourhood_idx
        if self.cls.startswith('O'):
            mass += 16.0 + b / 10
            m_min, m_max = 16, None
        elif self.cls.startswith('B'):
            mass += 2.1 + b / 10
            m_min, m_max = 2.1, 16
        elif self.cls.startswith('A'):
            mass += 1.4 + b / 10
            m_min, m_max = 1.4, 2.1
        elif self.cls.startswith('F'):
            mass += 1.04 + b / 10
            m_min, m_max = 1.04, 1.4
        elif self.cls.startswith('G'):
            mass += 0.8 + b / 10
            m_min, m_max = 0.8, 1.04
        elif self.cls.startswith('K'):
            mass += 0.45 + b / 10
            m_min, m_max = 0.45, 0.8
        elif self.cls.startswith('M'):
            mass += 0.08 + b / 100
            m_min, m_max = 0.08, 0.45

        self.min_mass = m_min
        self.max_mass = m_max
        self.mass = q(mass, 'sol_mass')

    def __str__(self):
        return f'{self.cls}{turn_into_roman(self.idx + 1)}'

    def __repr__(self):
        return f"ProtoStar {self.cls} #{self.idx}"

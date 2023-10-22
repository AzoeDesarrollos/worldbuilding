from engine.backend import EventHandler, Systems
from .orbit import NeighbourhoodSystemOrbit
from engine.equations.space import Universe


class SingleSystem:
    star = None
    _orbit = None
    _cartesian = None
    letter = None
    celestial_type = None

    parent = None
    shared_mass = None
    age = None

    def __init__(self, star=None, neighbourhood_id=None):
        self.star = star
        self.age = star.age
        self.id = star.id
        self.neighbourhood = neighbourhood_id
        EventHandler.register(self.save_single_systems, 'Save')

    @property
    def cartesian(self):
        return self._cartesian

    @cartesian.setter
    def cartesian(self, values):
        x, y, z = 0, 0, 0
        if type(values) is dict:
            x, y, z = list(values.values())
        elif type(values) in (list, tuple):
            x, y, z = values

        self._cartesian = x, y, z
        self.star.cartesian = x, y, z

    def set_orbit(self, offset):
        self._orbit = NeighbourhoodSystemOrbit(*self._cartesian, offset)

    def composition(self):
        return [self]

    def save_single_systems(self, event):
        data = {
            self.id: {
                "star": self.star.id,
                "position": dict(zip(['x', 'y', 'z'], self.cartesian)),
                "neighbourhood_id": self.neighbourhood
            }
        }

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Single Systems': data})

    def __repr__(self):
        return f'System of {str(self.star)}'


def load_single_systems(event):
    data = event.data['Single Systems']
    for id in data:
        system_data = event.data['Single Systems'][id]
        star_id = system_data['star']
        neighbourhood_id = system_data['neighbourhood_id']

        star = Universe.get_astrobody_by(star_id, 'id')
        proto_systems = [system for system in Universe.systems if system.composition == 'single']
        position = list(system_data['position'].values())
        for proto in proto_systems:
            if proto.location == position:
                Universe.systems.remove(proto)
                break

        Systems.set_planetary_system(star)
        neighbourhood = Universe.current_galaxy.get_neighbourhood(neighbourhood_id)

        system = SingleSystem(star, neighbourhood.id)
        system.cartesian = system_data['position']
        neighbourhood.add_true_system(system)

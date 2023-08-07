from engine.backend import EventHandler, generate_id
from .orbit import NeighbourhoodSystemOrbit
from engine.equations.space import Universe
from time import sleep


class SingleSystem:
    _star = None
    _orbit = None
    _cartesian = None
    letter = None
    celestial_type = None

    def __init__(self, star=None, neighbourhood_id=None):
        self._star = star
        # ID values make each star unique, even if they have the same mass and name.
        self.id = generate_id()
        sleep(0.01)
        self.neighbourhood = neighbourhood_id
        EventHandler.register(self.save_single_systems, 'Save')

    @property
    def cartesian(self):
        return self._cartesian

    @cartesian.setter
    def cartesian(self, values):
        self._cartesian = values

    def set_orbit(self, offset):
        self._orbit = NeighbourhoodSystemOrbit(*self._cartesian,offset)

    def composition(self):
        return [self]

    def save_single_systems(self, event):
        data = {
            self.id:{
                "star":self._star.id,
                "position": dict(zip(['x', 'y', 'z'], self.cartesian)),
                "neighbourhood_id": self.neighbourhood
            }
        }

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Single Systems': data})

    def __repr__(self):
        return f'System of {str(self._star)}'


def load_single_systems(event):
    data = event.data['Single Systems']
    for id in data:
        system_data = event.data['Single Systems'][id]
        star_id = system_data['star']
        neighbourhood_id = system_data['neighbourhood_id']

        star = Universe.get_astrobody_by(star_id,'id')
        neighbourhood = Universe.current_galaxy.get_neighbourhood(neighbourhood_id)

        system = SingleSystem(star, neighbourhood.id)
        system.cartesian = system_data['position']
        neighbourhood.add_true_system(system)

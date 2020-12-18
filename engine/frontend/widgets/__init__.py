from .panels.planet_panel import PlanetPanel
from .panels.star_panel import StarPanel
from .panels.satellite_panel import SatellitePanel
from .panels.stellar_orbit_panel import OrbitPanel
from .panels.atmosphere_panel import AtmospherePanel
from .panels.star_system_panel import StarSystemPanel
from .panels.asteroid_panel import AsteroidPanel
from .panels.planetary_orbit_panel import PlanetaryOrbitPanel
from .basewidget import BaseWidget

panels = [
    StarPanel,
    StarSystemPanel,
    PlanetPanel,
    OrbitPanel,
    SatellitePanel,
    AsteroidPanel,
    PlanetaryOrbitPanel,
    AtmospherePanel,
]

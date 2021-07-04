from .planet_panel import PlanetPanel
from .star_panel import StarPanel
from .satellite_panel import SatellitePanel
from .stellar_orbit_panel import OrbitPanel
from .atmosphere_panel import AtmospherePanel
from .star_system_panel import StarSystemPanel
from .asteroid_panel import AsteroidPanel
from .planetary_orbit_panel import PlanetaryOrbitPanel
from .naming_panel import NamingPanel

panels = [
    StarPanel,
    StarSystemPanel,
    PlanetPanel,
    SatellitePanel,
    AsteroidPanel,
    OrbitPanel,
    PlanetaryOrbitPanel,
    AtmospherePanel,
    NamingPanel
]

from .planet_panel import PlanetPanel
from .star_panel import StarPanel
from .satellite_panel import SatellitePanel
from .stellar_orbit_panel import OrbitPanel
from .atmosphere_panel import AtmospherePanel
from .star_system_panel import StarSystemPanel
from .asteroid_panel import AsteroidPanel
from .planetary_orbit_panel import PlanetaryOrbitPanel
from .naming_panel import NamingPanel
from .info_panel import InformationPanel
from .multiple_stars_panel import MultipleStarsPanel
from .albedo_panel import AlbedoPanel
from .start_panel import StartPanel
from .double_planets_panel import DoublePlanetsPanel
from .neighbourhood_panel import NeighbourhoodPanel
from .compact_objects_panel import CompactObjectsPanel
from .calendar_panel import CalendarPanel

panels = [
    StartPanel,
    NeighbourhoodPanel,
    StarPanel,
    CompactObjectsPanel,
    StarSystemPanel,
    MultipleStarsPanel,
    PlanetPanel,
    DoublePlanetsPanel,
    SatellitePanel,
    AsteroidPanel,
    AlbedoPanel,
    OrbitPanel,
    PlanetaryOrbitPanel,
    CalendarPanel,
    InformationPanel,
    AtmospherePanel,
    NamingPanel
]

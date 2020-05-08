from pygame.sprite import LayeredUpdates
from .basewidget import BaseWidget
from .star_panel import StarPanel
from .planet_panel import PlanetPanel


class LayoutPanel(BaseWidget):
    def __init__(self):
        super().__init__()
        self.panels = LayeredUpdates()
        self.panel_star = StarPanel()
        self.panel_planet = PlanetPanel()

        self.panels.add(self.panel_star)
        self.panels.add(self.panel_planet)

        self.current = self.panel_star
        self.current.show()

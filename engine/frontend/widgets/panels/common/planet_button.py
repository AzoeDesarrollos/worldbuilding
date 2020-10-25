from engine.frontend.globales import COLOR_TEXTO, COLOR_TERRESTIAL, COLOR_GASDWARF
from engine.frontend.globales import COLOR_GASGIANT, COLOR_PUFFYGIANT, COLOR_DWARFPLANET
from engine.equations.planetary_system import Systems
from .listed_body import ListedBody


class PlanetButton(ListedBody):
    enabled = True

    def __init__(self, parent, planet, x, y):
        name = ''
        color = COLOR_TEXTO
        if planet.clase == 'Terrestial Planet':
            name = 'Terrestial'
            color = COLOR_TERRESTIAL
        elif planet.clase == 'Gas Giant':
            name = 'Giant'
            color = COLOR_GASGIANT
        elif planet.clase == 'Puffy Giant':
            name = 'Puffy'
            color = COLOR_PUFFYGIANT
        elif planet.clase == 'Gas Dwarf':
            name = 'Gas Dwarf'
            color = COLOR_GASDWARF
        elif planet.clase == 'Dwarf Planet':
            name = 'Dwarf'
            color = COLOR_DWARFPLANET
        super().__init__(parent, planet, name, x, y, fg_color=color)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.planet = self.object_data
            Systems.get_current().set_current_planet(self.object_data)
            self.parent.has_values = True
            self.parent.fill()
            self.parent.toggle_habitable()

    def move(self, x, y):
        self.rect.topleft = x, y

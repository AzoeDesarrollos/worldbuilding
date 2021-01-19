from engine.frontend.globales import COLOR_TEXTO, COLOR_TERRESTIAL, COLOR_GASDWARF, COLOR_HABITABLE
from engine.frontend.globales import COLOR_GASGIANT, COLOR_PUFFYGIANT, COLOR_DWARFPLANET
from .listed_body import ListedBody


class PlanetButton(ListedBody):
    def __init__(self, parent, planet, x, y):
        name = ''
        color = COLOR_TEXTO
        if planet.clase == 'Terrestial Planet':
            name = 'Terrestial'
            if planet.habitable:
                color = COLOR_HABITABLE
            else:
                color = COLOR_TERRESTIAL
        elif planet.clase in ('Gas Giant', 'Super Jupiter'):
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
        raise NotImplementedError()

    def move(self, x, y):
        self.rect.topleft = x, y

from engine.frontend.globales import COLOR_TEXTO, COLOR_TERRESTIAL, COLOR_GASDWARF, COLOR_HABITABLE
from engine.frontend.globales import COLOR_GASGIANT, COLOR_PUFFYGIANT, COLOR_DWARFPLANET
from engine.frontend.globales import COLOR_ROCKYMOON, COLOR_ICYMOON, COLOR_IRONMOON
from .listed_body import ListedBody


class PlanetButton(ListedBody):
    def __init__(self, parent, astro, x, y):
        color = COLOR_TEXTO
        if astro.clase == 'Terrestial Planet':
            if astro.habitable:
                color = COLOR_HABITABLE
            else:
                color = COLOR_TERRESTIAL
        elif astro.clase in ('Gas Giant', 'Super Jupiter'):
            color = COLOR_GASGIANT
        elif astro.clase == 'Puffy Giant':
            color = COLOR_PUFFYGIANT
        elif astro.clase == 'Gas Dwarf':
            color = COLOR_GASDWARF
        elif astro.clase == 'Dwarf Planet':
            color = COLOR_DWARFPLANET
        elif astro.comp == 'Rocky':
            color = COLOR_ROCKYMOON
        elif astro.comp == 'Icy':
            color = COLOR_ICYMOON
        elif astro.comp == 'Iron':
            color = COLOR_IRONMOON

        if astro.has_name:
            name = astro.name
        else:
            name = str(astro)

        super().__init__(parent, astro, name, x, y, fg_color=color)

    def on_mousebuttondown(self, event):
        raise NotImplementedError()

    def move(self, x, y):
        self.rect.topleft = x, y

    def __repr__(self):
        return 'Button of '+str(self.object_data)

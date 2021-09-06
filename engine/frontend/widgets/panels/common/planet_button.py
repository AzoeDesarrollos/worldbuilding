from engine.frontend.globales import COLOR_TEXTO, COLOR_TERRESTIAL, COLOR_GASDWARF, COLOR_HABITABLE
from engine.frontend.globales import COLOR_GASGIANT, COLOR_PUFFYGIANT, COLOR_DWARFPLANET
from engine.frontend.globales import COLOR_ROCKYMOON, COLOR_ICYMOON, COLOR_IRONMOON
from .listed_body import ListedBody


class PlanetButton(ListedBody):
    def __init__(self, parent, astro, x, y):
        name = ''
        color = COLOR_TEXTO
        if astro.clase == 'Terrestial Planet':
            name = 'Terrestial'
            if astro.habitable:
                color = COLOR_HABITABLE
            else:
                color = COLOR_TERRESTIAL
        elif astro.clase in ('Gas Giant', 'Super Jupiter'):
            name = 'Giant'
            color = COLOR_GASGIANT
        elif astro.clase == 'Puffy Giant':
            name = 'Puffy'
            color = COLOR_PUFFYGIANT
        elif astro.clase == 'Gas Dwarf':
            name = 'Gas Dwarf'
            color = COLOR_GASDWARF
        elif astro.clase == 'Dwarf Planet':
            name = 'Dwarf'
            color = COLOR_DWARFPLANET
        elif astro.comp == 'Rocky':
            name = "{} #{}".format(astro.title, astro.idx)
            color = COLOR_ROCKYMOON
        elif astro.comp == 'Icy':
            name = "{} #{}".format(astro.title, astro.idx)
            color = COLOR_ICYMOON
        elif astro.comp == 'Iron':
            name = "{} #{}".format(astro.title, astro.idx)
            color = COLOR_IRONMOON

        if astro.has_name:
            name = astro.name

        super().__init__(parent, astro, name, x, y, fg_color=color)

    def on_mousebuttondown(self, event):
        raise NotImplementedError()

    def move(self, x, y):
        self.rect.topleft = x, y

    def __repr__(self):
        return 'Button of '+str(self.object_data)

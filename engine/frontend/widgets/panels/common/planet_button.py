from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, COLOR_TERRESTIAL, COLOR_GASDWARF
from engine.frontend.globales import COLOR_GASGIANT, COLOR_PUFFYGIANT, COLOR_DWARFPLANET
from engine.equations.planetary_system import system
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import font
from .meta import Meta


class PlanetButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, planet, x, y):
        super().__init__(parent)
        self.planet_data = planet
        self.f1 = font.SysFont('Verdana', 13)
        self.f2 = font.SysFont('Verdana', 13, bold=True)
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

        self.img_uns = self.f1.render(name, True, color, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, color, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.current = self.planet_data
            system.set_current(self.planet_data)
            self.parent.has_values = True
            self.parent.fill()
            self.parent.toggle_habitable()

    def update(self):
        super().update()
        if self.parent.parent.is_visible:
            self.show()
        else:
            self.hide()

    def move(self, x, y):
        self.rect.topleft = x, y

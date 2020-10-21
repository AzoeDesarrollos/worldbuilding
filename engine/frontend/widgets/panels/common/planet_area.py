from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, WidgetGroup
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, font


class PlanetArea(BaseWidget):

    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)
        self.image = Surface((w, h))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.listed_planets = WidgetGroup()

        self.f = font.SysFont('Verdana', 14)
        self.f.set_underline(True)
        self.write('Astronomical Objects', self.f, midtop=(self.rect.w / 2, 0))

    def write(self, text, fuente, **kwargs):
        render = fuente.render(text, True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(**kwargs)
        self.image.blit(render, render_rect)

    def hide(self):
        for listed in self.listed_planets.widgets():
            listed.hide()
        super().hide()

    def delete_planet(self, planet):
        for listed in self.listed_planets.widgets():
            if listed.planet_data == planet:
                listed.kill()
        self.sort()

    def sort(self):
        for i, planet in enumerate(self.listed_planets.widgets()):
            planet.rect.y = i * 16 + self.rect.y + 21

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))

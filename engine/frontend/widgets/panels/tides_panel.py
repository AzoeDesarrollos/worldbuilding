from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup
from ..basewidget import BaseWidget
from pygame import Surface
from .common import AvailableObjects, AvailablePlanet
from engine.equations.planetary_system import Systems


class TidesPanel(BaseWidget):
    skippable = False

    current = None

    def __init__(self, parent):
        self.name = 'Tides'
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.properties.add(self.planet_area, layer=2)

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()


class Astrobody(AvailablePlanet):

    def on_mousebuttondown(self, event):
        pass


class AvailablePlanets(AvailableObjects):
    listed_type = Astrobody

    def show(self):
        system = Systems.get_current()
        if system is not None:
            bodies = [body for body in system.astro_bodies]
            if not len(self.listed_objects.get_widgets_from_layer(Systems.get_current_idx())):
                self.populate(bodies)
        super().show()

    # def on_mousebuttondown(self, event):
    #     super().on_mousebuttondown(event)
        # if self.parent.visible_markers:
        #     self.parent.hide_markers()
        # self.parent.current = None

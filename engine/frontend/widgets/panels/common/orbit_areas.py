from engine.frontend.globales import COLOR_AREA, COLOR_DISABLED, COLOR_TEXTO
from engine.equations.planetary_system import Systems
from engine.frontend.widgets.meta import Meta
from . import ListedArea, PlanetButton


class ToggleableButton(Meta):
    enabled = True

    def __init__(self, parent, text, method, x, y):
        super().__init__(parent)
        f1 = self.crear_fuente(14)
        f2 = self.crear_fuente(14, bold=True)
        self.img_uns = f1.render(text, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = f2.render(text, True, COLOR_TEXTO, COLOR_AREA)
        self.img_dis = f1.render(text, True, COLOR_DISABLED, COLOR_AREA)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))
        self.method = method

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            self.method()


class AvailablePlanet(PlanetButton):
    def __init__(self, parent, astro, x, y):
        super().__init__(parent, astro, x, y)
        self.object_data = astro

    def on_mousebuttondown(self, event):
        raise NotImplementedError()


class AvailableObjects(ListedArea):
    listed_type = AvailablePlanet

    def populate(self, population):
        listed = []
        self.listed_objects.empty()
        for i, obj in enumerate(population):
            x = self.rect.x + 3
            y = i * 18 + self.rect.y + 21
            listed.append(self.listed_type(self, obj, x, y))

        self.listed_objects.add(*listed, layer=Systems.get_current_idx())

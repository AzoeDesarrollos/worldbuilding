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
    def __init__(self, parent, planet, x, y):
        super().__init__(parent, planet, x, y)
        self.object_data = planet

    def on_mousebuttondown(self, event):
        raise NotImplementedError()


class AvailableObjects(ListedArea):
    listed_type = AvailablePlanet

    def populate(self, population):
        listed = []
        for i, obj in enumerate(population):
            x = self.rect.x + 3
            y = i * 16 + self.rect.y + 21
            if obj.celestial_type == 'planet':
                listed.append(self.listed_type(self, obj, x, y))

            elif obj.celestial_type == 'satellite':
                pass

        self.listed_objects.add(*listed, layer=Systems.get_current_idx())

    def show(self):
        system = Systems.get_current()
        if system is not None:
            planets = [i for i in system.planets if i.orbit is None]
            if not len(self.listed_objects.get_widgets_from_layer(Systems.get_current_idx())):
                self.populate(planets)
        super().show()

    def show_current(self, idx):
        for listed in self.listed_objects.widgets():
            listed.hide()
        self.show()
        for listed in self.listed_objects.get_widgets_from_layer(idx):
            listed.show()

    def update(self):
        super().update()
        self.show_current(Systems.get_current_idx())

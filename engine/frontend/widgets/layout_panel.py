from pygame.sprite import LayeredUpdates
from .basewidget import BaseWidget
from .star_panel import StarPanel
from .planet_panel import PlanetPanel
from engine.frontend.globales import ALTO, ANCHO
from pygame import Surface, draw, transform, SRCALPHA
from engine.frontend.globales import Renderer, WidgetHandler
from itertools import cycle


class LayoutPanel(BaseWidget):
    def __init__(self):
        super().__init__()
        self.image = Surface((ANCHO, ALTO))
        self.image.fill((125, 125, 125))
        self.rect = self.image.get_rect()
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

        self.panels = LayeredUpdates()
        self.properties = LayeredUpdates()
        self.panel_star = StarPanel()
        self.panel_planet = PlanetPanel()

        self.panels.add(self.panel_star)
        self.panels.add(self.panel_planet)

        self.cycler = cycle(self.panels)
        self.current = next(self.cycler)
        self.current.show()

        a = Arrow(self, 180, self.rect.left+16, self.rect.bottom)
        b = Arrow(self, 0, self.rect.right-16, self.rect.bottom)
        self.properties.add(a, b)
        Renderer.add_widget(a)
        Renderer.add_widget(b)

    def cycle(self):
        self.current.hide()
        self.current = next(self.cycler)
        self.current.show()


class Arrow(BaseWidget):
    selected = False

    def __init__(self, parent, angulo, centerx, y):
        super().__init__(parent)
        rojo = (255, 0, 0, 255)
        azul = (0, 0, 255, 255)
        WidgetHandler.add_widget(self)

        img1 = Surface((32, 32), SRCALPHA)
        draw.polygon(img1, rojo, [[1, 13], [20, 13], [20, 5], [30, 14], [20, 26], [20, 18], [1, 17]])
        self.img1 = transform.rotate(img1, angulo)

        img2 = Surface((32, 32), SRCALPHA)
        draw.polygon(img2, azul, [[1, 13], [20, 13], [20, 5], [30, 14], [20, 26], [20, 18], [1, 17]])
        self.img2 = transform.rotate(img2, angulo)

        self.image = self.img1
        self.rect = self.image.get_rect(centerx=centerx, bottom=y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.parent.cycle()

    def on_mouseover(self):
        self.select()

    def select(self):
        self.selected = True

    def update(self):
        if self.selected:
            self.image = self.img2
        else:
            self.image = self.img1
        self.selected = False

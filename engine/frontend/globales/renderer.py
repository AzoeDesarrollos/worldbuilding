from pygame import display, init, SCALED, image, event
from pygame.sprite import LayeredUpdates
from .constantes import ALTO, ANCHO, COLOR_FONDO
import os


class Renderer:
    contents = None

    @classmethod
    def init(cls):
        init()
        cls.reset()
        cls.contents = LayeredUpdates()

    @classmethod
    def reset(cls):
        display.quit()
        os.environ['SDL_VIDEO_CENTERED'] = "{!s},{!s}".format(0, 0)
        display.set_icon(image.load(os.path.join(os.getcwd(), 'data', 'favicon.png')))
        display.set_caption("WorldBuilding")
        display.set_mode((ANCHO, ALTO), SCALED)
        event.clear()

    @classmethod
    def add_widget(cls, widget, layer=1):
        if hasattr(widget, 'layer'):
            layer = widget.layer
        if widget not in cls.contents:
            cls.contents.add(widget, layer=layer)

    @classmethod
    def del_widget(cls, widget):
        cls.contents.remove(widget)

    @classmethod
    def update(cls):
        fondo = display.get_surface()
        fondo.fill(COLOR_FONDO)
        cls.contents.draw(fondo)
        display.update()


Renderer.init()

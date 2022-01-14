from .constantes import ALTO, ANCHO, COLOR_FONDO, HEIGHT, WIDTH
from pygame import display, init, SCALED, image, event, Rect
from engine.backend.eventhandler import EventHandler
from pygame.sprite import LayeredUpdates
import os


class Renderer:
    contents = None

    color = COLOR_FONDO
    rect = None
    mode = 1
    panels = None
    views = None

    @classmethod
    def init(cls):
        init()
        cls.panels = LayeredUpdates()
        cls.views = LayeredUpdates()

        cls.set_view_mode()
        cls.rect = Rect(0, 0, WIDTH, HEIGHT)
        EventHandler.register(cls.switch_mode, 'SwitchMode')

    @staticmethod
    def reset(ancho, alto):
        display.quit()
        os.environ['SDL_VIDEO_CENTERED'] = "{!s},{!s}".format(0, 0)
        display.set_icon(image.load(os.path.join(os.getcwd(), 'data', 'favicon.png')))
        display.set_caption("WorldBuilding")
        display.set_mode((ancho, alto), SCALED)
        event.clear()

    @classmethod
    def set_view_mode(cls):
        if cls.mode == 1:
            cls.reset(ANCHO, ALTO)
            cls.color = COLOR_FONDO
            cls.contents = cls.panels

        else:
            cls.reset(WIDTH, HEIGHT)
            cls.color = 'black'
            cls.contents = cls.views
            display.get_surface().fill('black')

    @classmethod
    def contains(cls, item):
        return cls.rect.colliderect(item.rect)

    @classmethod
    def switch_mode(cls, evento):
        cls.mode = evento.data['mode']
        cls.set_view_mode()

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
        fondo.fill(cls.color)
        rect = cls.contents.draw(fondo)
        display.update(rect)


Renderer.init()

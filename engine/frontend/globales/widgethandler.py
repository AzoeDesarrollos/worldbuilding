from pygame import event, QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame import K_ESCAPE, time
from engine.backend.eventhandler import EventHandler
from pygame.sprite import LayeredUpdates


class WidgetHandler:
    contents = None
    active = None
    clock = None

    @classmethod
    def init(cls):
        cls.contents = LayeredUpdates()
        cls.clock = time.Clock()

    @classmethod
    def add_widget(cls, widget, layer=1):
        cls.contents.add(widget, layer=layer)

    @classmethod
    def del_widget(cls, widget):
        cls.contents.remove(widget)

    @classmethod
    def set_active(cls, widget):
        for wdg in cls.contents:
            wdg.deactivate()
        # no se activa al widget per se adrede.
        # de esta manera Entry se comporta como debería.
        cls.active = widget

    @classmethod
    def update(cls):
        cls.clock.tick(60)
        events = event.get([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT])
        event.clear()
        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                EventHandler.trigger('salir', 'engine', {'mensaje': 'normal'})

            elif e.type == KEYDOWN:
                pass

            elif e.type == MOUSEBUTTONDOWN:
                pass

            elif e.type == MOUSEBUTTONUP:
                pass

        cls.contents.update()


WidgetHandler.init()

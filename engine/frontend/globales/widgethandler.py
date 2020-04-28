from pygame import event, QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame import K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9, K_KP0
from pygame import K_ESCAPE, time, mouse
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
        cls.active = widget

    @classmethod
    def update(cls):
        cls.clock.tick(60)
        events = event.get([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, MOUSEMOTION])
        event.clear()
        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                EventHandler.trigger('salir', 'engine', {'mensaje': 'normal'})

            elif e.type == KEYDOWN:
                numbers = [K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9]
                if e.key in numbers:
                    digit = numbers.index(e.key)

            elif e.type == MOUSEBUTTONDOWN:
                widgets = [i for i in cls.contents.sprites() if i.rect.collidepoint(e.pos)]
                for w in widgets:
                    w.on_mousebuttondown(e.button)

            elif e.type == MOUSEBUTTONUP:
                widgets = [i for i in cls.contents.sprites() if i.rect.collidepoint(e.pos)]
                for w in widgets:
                    w.on_mousebuttonup(e.button)

            elif e.type == MOUSEMOTION:
                x, y = e.pos
                for widget in cls.contents.sprites():
                    if widget.rect.collidepoint((x, y)):
                        widget.on_mousemotion(e.rel)

        x, y = mouse.get_pos()
        for widget in cls.contents.sprites():
            if widget.rect.collidepoint((x, y)):
                widget.on_mouseover()

        cls.contents.update()


WidgetHandler.init()

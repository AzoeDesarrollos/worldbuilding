from pygame import event, QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, K_KP_ENTER, K_BACKSPACE
from pygame import K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9, K_KP0, K_KP_PERIOD, K_KP_EQUALS
from pygame import K_UP, K_DOWN
from pygame import K_ESCAPE, time, mouse
from engine.backend.eventhandler import EventHandler
from pygame.sprite import LayeredUpdates


class WidgetHandler:
    contents = None
    active = None
    clock = None
    origin = 'engine'

    locked = False
    the_one = None

    @classmethod
    def init(cls):
        cls.contents = LayeredUpdates()
        cls.clock = time.Clock()

    @classmethod
    def add_widget(cls, widget, layer=1):
        if widget not in cls.contents:
            cls.contents.add(widget, layer=layer)

    @classmethod
    def del_widget(cls, widget):
        cls.contents.remove(widget)

    @classmethod
    def lock_and_set(cls, the_one):
        cls.locked = True
        cls.the_one = the_one

    @classmethod
    def unlock(cls):
        cls.locked = False

    @classmethod
    def update(cls):
        cls.clock.tick(60)
        events = event.get([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, MOUSEMOTION])
        event.clear()
        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                EventHandler.trigger('salir', 'engine', {'mensaje': 'normal'})

            elif e.type == KEYDOWN and not cls.locked:
                numbers = [K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9]
                if e.key in numbers:
                    digit = numbers.index(e.key)
                    EventHandler.trigger('Key', cls.origin, {'value': str(digit)})
                elif e.key == K_KP_PERIOD:
                    EventHandler.trigger('Key', cls.origin, {'value': '.'})
                elif e.key in (K_KP_ENTER, K_KP_EQUALS):
                    EventHandler.trigger('Fin', cls.origin)
                elif e.key == K_BACKSPACE:
                    EventHandler.trigger('BackSpace', cls.origin)
                elif e.key == K_UP:
                    EventHandler.trigger('Arrow', cls.origin, {'word': 'arriba', 'delta': -1})
                elif e.key == K_DOWN:
                    EventHandler.trigger('Arrow', cls.origin, {'word': 'abajo', 'delta': +1})

            elif e.type == MOUSEBUTTONDOWN:
                widgets = [i for i in cls.contents.sprites() if i.rect.collidepoint(e.pos)]
                widgets.sort(key=lambda o: o.layer, reverse=True)
                if not cls.locked or widgets[0] is cls.the_one:
                    cls.origin = widgets[0].on_mousebuttondown(e)
                else:
                    cls.the_one.blink()

            elif e.type == MOUSEBUTTONUP:
                widgets = [i for i in cls.contents.sprites() if i.rect.collidepoint(e.pos)]
                widgets.sort(key=lambda o: o.layer, reverse=True)
                widgets[0].on_mousebuttonup(e)

            elif e.type == MOUSEMOTION:
                x, y = e.pos
                for widget in cls.contents.sprites():
                    if widget.rect.collidepoint((x, y)):
                        widget.on_mousemotion(e.rel)

        x, y = mouse.get_pos()
        for widget in cls.contents.sprites():
            if widget.rect.collidepoint((x, y)) and (not cls.locked or widget is cls.the_one):
                widget.on_mouseover()

        cls.contents.update()


WidgetHandler.init()

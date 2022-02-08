from pygame import event, QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, K_KP_ENTER, K_BACKSPACE
from pygame import K_KP_EQUALS, K_UP, K_DOWN, K_ESCAPE, time, mouse, key
from pygame import KMOD_RSHIFT, KMOD_LSHIFT
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
    def set_origin(cls, widget):
        if widget is not None:
            cls.origin = widget

    @classmethod
    def update(cls):
        cls.clock.tick(60)
        events = event.get([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, MOUSEMOTION])
        event.clear()
        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                EventHandler.trigger('salir', 'engine', {'mensaje': 'normal'})

            elif e.type == KEYDOWN and not cls.locked:
                if e.key in (K_KP_ENTER, K_KP_EQUALS):
                    EventHandler.trigger('Fin', cls.origin)
                elif e.key == K_BACKSPACE:
                    EventHandler.trigger('BackSpace', cls.origin)
                elif e.key == K_UP:
                    EventHandler.trigger('Arrow', cls.origin, {'word': 'arriba', 'delta': -1})
                elif e.key == K_DOWN:
                    EventHandler.trigger('Arrow', cls.origin, {'word': 'abajo', 'delta': +1})
                else:
                    name = key.name(e.key).strip('[]')
                    if len(name) == 1:  # single character, excludes "space" and things like that.
                        if name == '.':  # bc there's not other way to identifying it.
                            EventHandler.trigger('Key', cls.origin, {'value': '.'})
                        elif name.isdigit():
                            EventHandler.trigger('Key', cls.origin, {'value': name})
                        elif name.isalpha():
                            if e.mod & KMOD_LSHIFT or e.mod & KMOD_RSHIFT:
                                name = name.capitalize()
                            EventHandler.trigger('Typed', cls.origin, {'value': name})
                    elif name == 'space':
                        EventHandler.trigger('Typed', cls.origin, {'value': ' '})

            elif e.type == MOUSEBUTTONDOWN:
                widgets = [i for i in cls.contents.sprites() if i.rect.collidepoint(e.pos)]
                widgets.sort(key=lambda o: o.layer, reverse=True)
                if not cls.locked or widgets[0] is cls.the_one:
                    cls.set_origin(widgets[0].on_mousebuttondown(e))
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

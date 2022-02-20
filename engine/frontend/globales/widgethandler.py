from pygame import event, QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, K_BACKSPACE
from pygame import K_UP, K_DOWN, K_ESCAPE, time, mouse, key
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

    mode = 1

    @classmethod
    def init(cls):
        cls.contents = LayeredUpdates()
        cls.clock = time.Clock()
        EventHandler.register(cls.switch_mode, 'SwitchMode')

    @classmethod
    def add_widget(cls, widget):
        if widget not in cls.contents:
            cls.contents.add(widget, layer=cls.mode)

    @classmethod
    def del_widget(cls, widget):
        if widget in cls.contents.get_sprites_from_layer(cls.mode):
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
    def cap(cls, n):
        if n != 0:
            val = abs(n)
            sign = n / n
            if val >= 500:
                n = 500 * sign
        return n

    @classmethod
    def switch_mode(cls, evento):
        cls.mode = evento.data['mode']

    @classmethod
    def update(cls):
        cls.clock.tick(60)
        events = event.get([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, MOUSEMOTION])
        event.clear()
        dx, dy = 0, 0
        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                EventHandler.trigger('salir', 'engine', {'mensaje': 'normal'})

            elif e.type == KEYDOWN and not cls.locked:
                if key.name(e.key) in ('enter', 'return'):
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
                if cls.mode == 1:
                    x, y = e.pos
                    for widget in cls.contents.sprites():
                        if widget.rect.collidepoint((x, y)):
                            widget.on_mousemotion(e.rel)

                elif cls.mode == 2:
                    if any(e.buttons):
                        dx, dy = e.rel
                        dx = cls.cap(dx)
                        dy = cls.cap(dy)

        if cls.mode == 2:
            if dx or dy:
                for widget in cls.contents.get_sprites_from_layer(cls.mode):
                    widget.move(dx, dy)

        elif cls.mode == 1:
            x, y = mouse.get_pos()
            for widget in cls.contents.sprites():
                if widget.rect.collidepoint((x, y)) and (not cls.locked or widget is cls.the_one):
                    widget.on_mouseover()

        cls.contents.update()


WidgetHandler.init()

from engine.frontend.globales import WidgetHandler, Renderer, COLOR_BOX, COLOR_TEXTO, render_textrect, NUEVA_LINEA
from engine.backend.eventhandler import EventHandler
from pygame.sprite import Sprite
from pygame import font, Rect


class BaseWidget(Sprite):
    active = False
    enabled = False
    selected = False
    is_visible = False
    layer = 0

    curr_x = 3
    curr_y = 440

    default_spacing = 5
    area_buttons = None

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        if self.parent is not None:
            self.layer = self.parent.layer + 1
        EventHandler.register(self.on_mousebuttondown, 'onMouseButtonDown')
        EventHandler.register(self.on_mousebuttonup, 'onMouseButtonUp')

    @staticmethod
    def crear_fuente(size, underline=False, bold=False):
        f = font.SysFont('Verdana', size, bold=bold)
        f.set_underline(underline)
        return f

    def on_keydown(self, key):
        pass

    def on_keyup(self, key):
        pass

    def on_mousebuttondown(self, event):
        pass

    def on_mousebuttonup(self, event):
        pass

    def on_mousemotion(self, rel):
        pass

    def on_mouseover(self):
        pass

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def update(self):
        pass

    def show(self):
        self.is_visible = True
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def hide(self):
        self.is_visible = False
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)

    def kill(self) -> None:
        self.hide()
        super().kill()

    def write(self, text, fuente, bg=COLOR_BOX, **kwargs):
        render = fuente.render(text, True, COLOR_TEXTO, bg)
        render_rect = render.get_rect(**kwargs)
        return self.image.blit(render, render_rect)

    def write2(self, text, fuente, width, bg=COLOR_BOX, **kwargs):
        j = kwargs.pop('j') if 'j' in kwargs else 0
        render = render_textrect(text, fuente, width, COLOR_TEXTO, bg, justification=j)
        render_rect = render.get_rect(**kwargs)
        return self.image.blit(render, render_rect)

    @staticmethod
    def write3(text, fuente, width, bg=COLOR_BOX, j=0):
        render = render_textrect(text, fuente, width, COLOR_TEXTO, bg, justification=j)
        return render

    def show_no_system_error(self):
        f = self.crear_fuente(16)
        text = 'There is no star system set. Go back to the Star Panel and set a star first.'
        rect = Rect(50, 100, 220, 100)
        render = render_textrect(text, f, rect.w, (0, 0, 0), COLOR_BOX)
        self.image.blit(render, rect)

    def sort_buttons(self, buttons, overriden=False, x=3, y=437):
        for i, bt in enumerate(buttons):
            a = bt.max_w + x + self.default_spacing
            b = bt.max_w + x
            if a < self.area_buttons.right or b < self.area_buttons.right:
                bt.move(x, y)
            else:
                y += NUEVA_LINEA
                x = 3
                bt.move(x, y)
            x += bt.max_w
            if self.area_buttons.contains(bt.rect):
                bt.show()
            else:
                bt.hide()

        if len(buttons) and not buttons[-1].is_visible and not overriden:
            self.curr_y -= 32
            self.sort_buttons(buttons, y=self.curr_y)

from engine.frontend.globales import WidgetHandler, Renderer, COLOR_BOX, COLOR_TEXTO
from engine.backend.textrect import render_textrect
from pygame.sprite import Sprite
from pygame import font, Rect


class BaseWidget(Sprite):
    active = False
    enabled = False
    selected = False
    is_visible = False
    layer = 0

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        if self.parent is not None:
            self.layer = self.parent.layer + 1

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
        super().kill()
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)

    def write(self, text, fuente, bg=COLOR_BOX, **kwargs):
        render = fuente.render(text, True, COLOR_TEXTO, bg)
        render_rect = render.get_rect(**kwargs)
        return self.image.blit(render, render_rect)

    def write2(self, text, fuente, witdh, bg=COLOR_BOX, **kwargs):
        render = render_textrect(text, fuente, witdh, COLOR_TEXTO, bg)
        render_rect = render.get_rect(**kwargs)
        return self.image.blit(render, render_rect)

    def show_no_system_error(self):
        f = self.crear_fuente(16)
        text = 'There is no star system set. Go back to the Star Panel and set a star first.'
        rect = Rect(50, 100, 220, 100)
        render = render_textrect(text, f, rect.w, (0, 0, 0), COLOR_BOX)
        self.image.blit(render, rect)

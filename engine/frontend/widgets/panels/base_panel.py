from engine.frontend.globales import ANCHO, ALTO, Renderer, WidgetHandler
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, font, transform


class BasePanel(BaseWidget):
    current = None
    relative_mode = True

    def __init__(self, name, parent):
        super().__init__(parent)
        bg = 125, 125, 125
        fg = 0, 0, 0
        self.name = name
        self.image = Surface((ANCHO, ALTO-32))
        self.rect = self.image.get_rect()

        self.f = font.SysFont('Verdana', 16)
        self.f.set_underline(True)

        f2 = font.SysFont('Verdana', 16)
        self.rt1_uns = transform.rotate(f2.render('Relative Values', 1, fg, bg), 90)
        self.rt1_sel = transform.rotate(f2.render('Absolute Values', 1, fg, bg), 90)
        rt1_rect = self.rt1_uns.get_rect(x=12, y=70)
        self.relative_text = self.rt1_uns
        self.relative_text_area = rt1_rect.inflate(10, 10)

        rt2 = transform.rotate(f2.render('Absolute Values', 1, fg, bg), 90)
        rt2_rect = rt2.get_rect(x=6, y=220)

        render = self.f.render(name+' Panel', 1, fg, bg)
        render_rect = render.get_rect(centerx=self.rect.centerx, y=0)

        self.image.fill(bg)
        self.image.blit(render, render_rect)
        self.image.blit(self.relative_text, self.relative_text_area)
        self.image.blit(rt2, rt2_rect)

    def on_mousebuttondown(self, event):
        bg = 125, 125, 125
        if event.button == 1:
            if self.relative_text_area.collidepoint(event.pos):
                self.image.fill(bg, self.relative_text_area)
                if self.relative_mode:
                    self.relative_text = self.rt1_sel
                    self.relative_mode = False
                else:
                    self.relative_text = self.rt1_uns
                    self.relative_mode = True

                if self.current.has_values:
                    self.current.fill()
                self.image.blit(self.relative_text, self.relative_text_area)

    def show(self):
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)
        self.current.show()

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
        self.current.hide()

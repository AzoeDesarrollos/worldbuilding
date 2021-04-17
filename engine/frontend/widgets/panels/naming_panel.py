from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup, render_textrect, WidgetHandler
from engine.equations.planetary_system import Systems
from engine.frontend.widgets.values import ValueText
from engine.frontend.widgets import BaseWidget
from pygame import Surface, Rect


class NamingPanel(BaseWidget):
    skippable = False
    last_idx = -1

    curr_idx = 0
    current = None

    def __init__(self, parent):
        self.name = 'Naming'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.unnamed = WidgetGroup()
        self.dummy = DummyType(self)

    def show(self):
        super().show()
        self.add_current()

    def add_current(self):
        idx = Systems.get_current_idx()
        system = Systems.get_current()
        if system is not None:
            for i, astrobody in enumerate(system.get_unnamed()):
                if astrobody.celestial_type == 'system':
                    name = astrobody.letter + '-Type System #{}'.format(astrobody.idx)
                else:  # stars and planets
                    name = str(astrobody)

                vt = ValueText(self.dummy, name, 3, 55 + i * 13 * 2, kind='letters')
                vt.enable()
                if vt not in self.unnamed:
                    self.unnamed.add(vt, layer=idx)
        else:
            f = self.crear_fuente(16)
            text = 'There is no system nor there are astronomical bodies to name.'
            rect = Rect(0, 0, 200, 100)
            rect.center = self.rect.center
            render = render_textrect(text, f, rect.w, (0, 0, 0), COLOR_BOX, 1)
            self.image.blit(render, rect)

    def show_current(self, idx):
        for button in self.unnamed.widgets():
            button.hide()

        if not len(self.unnamed.get_widgets_from_layer(idx)):
            self.add_current()

        for button in self.unnamed.get_widgets_from_layer(idx):
            button.show()

    def update(self):
        idx = Systems.get_current_idx()
        if idx != self.last_idx:
            self.show_current(idx)
            self.last_idx = idx

    def cycle(self, delta):
        for elm in self.unnamed.widgets():
            elm.deselect()
            elm.active = False
            elm.disable()
            elm.text_area.disable()
        if 0 <= self.curr_idx + delta < len(self.unnamed.widgets()):
            self.curr_idx += delta
        else:
            self.curr_idx = 0

        self.current = self.unnamed.widgets()[self.curr_idx]
        self.current.select()
        self.current.enable()
        self.current.active = True
        self.current.text_area.enable()
        WidgetHandler.origin = self.current.text_area.name


class DummyType(BaseWidget):
    has_values = False

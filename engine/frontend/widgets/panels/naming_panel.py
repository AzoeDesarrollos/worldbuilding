from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup, render_textrect, WidgetHandler
from engine.equations.planetary_system import Systems
from engine.frontend.widgets.values import ValueText
from engine.backend.eventhandler import EventHandler
from engine.frontend.widgets import BaseWidget
from pygame import Surface, Rect


class NamingPanel(BaseWidget):
    skippable = False
    last_idx = -1

    curr_idx = 0
    current = None

    no_system_error = False
    all_named_error = False

    def __init__(self, parent):
        self.name = 'Naming'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.unnamed = WidgetGroup()
        self.objects = []
        self.dummy = DummyType(self)

    def hide(self):
        super().hide()
        self.last_idx = -1
        for item in self.unnamed.widgets():
            item.hide()

    def add_current(self):
        idx = Systems.get_current_idx()
        system = Systems.get_current()
        if system is not None:
            objects = system.get_unnamed()
            if len(objects):
                for i, astrobody in enumerate(objects):
                    if not astrobody.flagged:
                        if astrobody.celestial_type == 'system':
                            name = astrobody.letter + '-Type System #{}'.format(astrobody.idx)
                        else:  # stars and planets
                            name = str(astrobody)

                        vt = ValueText(self.dummy, name, 3, 55 + i * 13 * 2, kind='letters')
                        vt.enable()
                        if astrobody not in self.objects:
                            self.unnamed.add(vt, layer=idx)
                            self.objects.append(astrobody)
                        self.all_named_error = False
                        self.no_system_error = False
            else:
                self.all_named_error = True
        else:
            self.no_system_error = True

    def render_text(self, text):
        f = self.crear_fuente(16)

        rect = Rect(0, 0, 200, 100)
        rect.center = self.rect.center
        render = render_textrect(text, f, rect.w, (0, 0, 0), COLOR_BOX, 1)
        self.image.blit(render, rect)

    def sort(self):
        for i, listed in enumerate([i for i in self.unnamed.widgets() if i.is_visible]):
            listed.rect.y = 55 + i * 13 * 2

    def show_current(self, idx):
        flagged = [i for i in self.objects if i.flagged]
        for obj in flagged:
            idxs = obj.idx
            button = self.unnamed.get_widget(idxs)
            self.unnamed.remove(button)

        for button in self.unnamed.widgets():
            button.hide()

        # if not len(self.unnamed.get_widgets_from_layer(idx)):
        self.add_current()

        self.sort()
        for button in self.unnamed.get_widgets_from_layer(idx):
            button.show()

    def update(self):
        idx = Systems.get_current_idx()
        if idx != self.last_idx and idx >= 0:
            self.show_current(idx)
            self.last_idx = idx
        elif self.no_system_error:
            text = "There are no more astronomical bodies to name for this system."
            self.render_text(text)
        elif self.all_named_error or idx == -1:
            text = 'There is no system nor there are astronomical bodies to name.'
            self.render_text(text)

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

    def set_current(self, current):
        self.current = current
        self.curr_idx = self.unnamed.widgets().index(current)

    def name_objects(self):
        text = self.current.text_area.value
        idx = self.unnamed.widgets().index(self.current)
        obj = self.objects[idx]
        EventHandler.trigger('NameObject', self, {'object': obj, 'name': text})


class DummyType(BaseWidget):
    has_values = False

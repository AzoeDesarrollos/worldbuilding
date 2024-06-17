from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, render_textrect, WidgetHandler, Group
from engine.frontend.widgets.values import ValueText
from engine.frontend.widgets import BaseWidget
from engine.equations.space import Universe
from engine.backend import EventHandler
from pygame import Surface, Rect


class NamingPanel(BaseWidget):
    skippable = False
    skip = False
    last_id = -1

    curr_idx = 0
    current = None

    no_system_error = False
    all_named_error = False

    show_swap_system_button = True

    def __init__(self, parent):
        self.name = 'Naming'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.unnamed = Group()
        self.objects = {}
        self.dummy = DummyType(self)
        EventHandler.register(self.export_data, 'ExportData')

    def hide(self):
        super().hide()
        self.last_id = -1
        for item in self.unnamed.widgets():
            item.hide()

    def add_current(self):
        system = Universe.nei().get_current()
        idx = system.id
        self.unnamed.empty()
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
                        if vt not in self.unnamed.get_widgets_from_layer(idx):
                            self.unnamed.add(vt, layer=idx)
                        if astrobody.id not in self.objects:
                            self.objects[astrobody.id] = [vt, astrobody]
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
        objects = [self.objects[i][1] for i in self.objects]
        flagged = [obj for obj in objects if obj.flagged]
        for obj in flagged:
            button = self.unnamed.get_widget(obj.id)
            self.unnamed.remove(button)

        for button in self.unnamed.widgets():
            button.hide()

        # if not len(self.unnamed.get_widgets_from_layer(idx)):
        self.add_current()

        for button in self.unnamed.get_widgets_from_layer(idx):
            button.show()
        self.sort()

    def update(self):
        if Universe.current_galaxy is not None:
            idx = Universe.current_planetary().id
        else:
            idx = self.last_id

        if idx != self.last_id:
            self.image.fill(COLOR_BOX, [0, 20, self.rect.w, self.rect.h - 52])
            self.show_current(idx)
            self.last_id = idx
        elif self.no_system_error:
            text = "There are no more astronomical bodies to name for this system."
            self.render_text(text)
        elif self.all_named_error or idx == -1:
            text = 'There is no system nor there are astronomical bodies to name.'
            self.render_text(text)

    def cycle(self, delta):
        for elm in self.unnamed.widgets():
            elm.deselect()
            elm._active = False
            elm.disable()
            elm.text_area.disable()
        if 0 <= self.curr_idx + delta < len(self.unnamed.widgets()):
            self.curr_idx += delta
        else:
            self.curr_idx = 0

        self.current = self.unnamed.widgets()[self.curr_idx]
        self.current.select()
        self.current.enable()
        self.current._active = True
        self.current.text_area.enable()
        WidgetHandler.origin = self.current.text_area.name

    def set_current(self, current):
        self.current = current
        self.curr_idx = self.unnamed.widgets().index(current)

    def check(self):
        done = all([obj.text_area.value != '' for obj in self.unnamed.widgets()])
        if done:
            for item in self.unnamed.widgets():
                item.hide()
            self.no_system_error = True
            self.update()

    def name_objects(self):
        obj, text = None, None
        for idx in self.objects:
            vt, obj = self.objects[idx]
            if self.current.compare(vt):
                text = vt.text_area.value
                break

        if obj is not None and text is not None:
            EventHandler.trigger('NameObject', self, {'object': obj, 'name': text})

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class DummyType(BaseWidget):
    has_values = False

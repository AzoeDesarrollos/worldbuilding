from engine.backend import EventHandler, q
from ..globales import Renderer, Group
from .basewidget import BaseWidget
from .values import ValueText


class ObjectType(BaseWidget):
    current = None
    has_values = False

    locked = False

    modifiable = True

    show_layers = None

    def __init__(self, parent, relative_names, absolute_names, relative_args, absolute_args):
        super().__init__(parent)
        self.show_layers = [1, 2]
        EventHandler.register(self.clear_selection, 'Clear')
        EventHandler.register(self.clear, 'ClearData')

        self.relative_args = relative_args
        self.absolute_args = absolute_args

        self.properties = Group()
        self.relatives = Group()
        self.absolutes = Group()
        for i, button in enumerate(relative_names+absolute_names):
            vt = ValueText(self, button, 50, 40 + i * 13 * 2)
            if button in relative_names:
                self.relatives.add(vt)
            elif button in absolute_names:
                self.absolutes.add(vt)
            self.properties.add(vt, layer=1)
            Renderer.update()

    def set_modifiables(self, group: str, *indexes):
        if group == 'relatives':
            group = self.relatives
        elif group == 'absolutes':
            group = self.absolutes

        for index in indexes:
            obj = group.get_widget(index)
            obj.modifiable = True

    def show(self):
        for layer in self.show_layers:
            for p in self.properties.get_widgets_from_layer(layer):
                p.show()

    def hide(self):
        for p in self.properties.widgets():
            p.hide()

    def clear_selection(self, event):
        if event.origin is not self:
            self.active = False

    def clear(self, event):
        return NotImplemented

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.active = True

    def on_mousebuttonup(self, event):
        if event.button == 1:
            EventHandler.trigger('Clear', self)

    def elevate_changes(self, key, new_value):
        arg = ''
        if key in self.relatives:
            idx = self.relatives.widgets().index(key)
            arg = self.relative_args[idx]
        elif key in self.absolutes:
            idx = self.absolutes.widgets().index(key)
            arg = self.absolute_args[idx]
        self.current.set_value(arg, new_value)

    def fill(self, tos):
        for i, elemento in enumerate(self.relatives.widgets()):
            arg = self.relative_args[i]
            if self.parent.mode == 0:
                got_attr = getattr(self.current, arg)
            else:
                got_attr = getattr(self.current, arg).to(tos[self.parent.mode][arg])
            attr = q(str(round(got_attr.m, 5)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            elemento.text_area.show()
            Renderer.update()

        for i, elemento in enumerate(self.absolutes.widgets()):
            arg = self.absolute_args[i]
            got_attr = getattr(self.current, arg)
            if self.parent.mode == 1 and arg in tos[self.parent.mode]:
                got_attr = got_attr.to(tos[self.parent.mode][arg])
            attr = q(str(round(got_attr.m, 3)), got_attr.u) if type(got_attr) is not str else got_attr
            elemento.value = attr
            elemento.text_area.show()
            Renderer.update()
        self.has_values = True

    def erase(self):
        self.has_values = False
        for elemento in self.relatives.widgets() + self.absolutes.widgets():
            elemento.text_area.clear()

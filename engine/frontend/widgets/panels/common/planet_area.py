from engine.frontend.globales import COLOR_AREA, WidgetGroup
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from pygame import Surface


class ListedArea(BaseWidget):
    name = 'Astronomical Objects'

    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)
        self.image = Surface((w, h))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.listed_objects = WidgetGroup()

        self.f = self.crear_fuente(14, underline=True)
        self.write(self.name, self.f, midtop=(self.rect.w / 2, 0), bg=COLOR_AREA)

    def populate(self, objects):
        return NotImplemented

    def hide(self):
        for listed in self.listed_objects.widgets():
            listed.hide()
        super().hide()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.deselect_all()

    def delete_objects(self, astronomical_object):
        for listed in self.listed_objects.widgets():
            if listed.object_data is astronomical_object:
                listed.kill()
                break
        self.sort()

    def sort(self):
        for i, listed in enumerate(self.listed_objects.widgets()):
            listed.rect.y = i * 16 + self.rect.y + 21

    def select_one(self, it):
        self.deselect_all()
        it.select()

    def deselect_all(self):
        self.image.fill(COLOR_AREA, [0, 21, self.rect.w, self.rect.h])
        for listed in self.listed_objects.widgets():
            listed.deselect()

    def objects(self):
        return [o.object_data for o in self.listed_objects.widgets()]

    def show_current(self, idx):
        for listed in self.listed_objects.widgets():
            listed.hide()
        for listed in self.listed_objects.get_widgets_from_layer(idx):
            listed.show()

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
        idx = Systems.get_current_idx()
        if idx > 0:
            self.show_current(idx)

    def __len__(self):
        return len(self.listed_objects)

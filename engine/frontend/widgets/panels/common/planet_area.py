from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.frontend.globales import COLOR_AREA
from pygame import Surface, Rect
from .group import Group


class ListedArea(BaseWidget):
    name = 'Astronomical Objects'

    last_idx = None

    listed_type = None

    offset = 0

    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)
        self.image = Surface((w, h))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.shown_area = Rect(self.rect.x, self.rect.y + 10, self.rect.w, self.rect.h - 10)
        self.listed_objects = Group()

        self.f = self.crear_fuente(14, underline=True)
        self.write(self.name, self.f, midtop=(self.rect.w / 2, 0), bg=COLOR_AREA)

    def populate(self, population, layer=None):
        listed = []
        for listed_ob in self.listed_objects.widgets():
            listed_ob.kill()
        self.listed_objects.empty()
        for i, obj in enumerate(population):
            x = self.rect.x + 3
            y = i * 18 + self.rect.y + 21
            listed.append(self.listed_type(self, obj, str(obj), x, y))

        if layer is None:
            layer = Systems.get_current().id

        self.listed_objects.add(*listed, layer=layer)
        self.sort()

    def hide(self):
        for listed in self.listed_objects.widgets():
            listed.hide()
        super().hide()

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.deselect_all()
        else:
            buttons = self.listed_objects.widgets()
            last_is_hidden = not buttons[-1].is_visible
            first_is_hidden = not buttons[0].is_visible
            if event.button == 4 and first_is_hidden:
                self.offset += 16
            elif event.button == 5 and last_is_hidden:
                self.offset -= 16

    def delete_objects(self, astronomical_object):
        listed = [i for i in self.listed_objects.widgets() if i.object_data is astronomical_object]
        if len(listed):
            listed[0].kill()
            self.listed_objects.remove(listed[0])
        self.sort()

    def sort(self):
        by_mass = sorted(self.listed_objects.widgets(), key=lambda b: b.object_data.mass.to('earth_mass').m, reverse=1)
        for i, listed in enumerate(by_mass):
            listed.rect.y = i * 16 + self.rect.y + self.offset + 21

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
        self.sort()
        for listed in self.listed_objects.widgets():
            listed.hide()
        for listed in self.listed_objects.get_widgets_from_layer(idx):
            if self.shown_area.contains(listed):
                listed.show()

    def remove_listed(self, listed):
        self.listed_objects.remove(listed)

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
        idx = Systems.get_current_id(self)
        if idx != self.last_idx:
            self.last_idx = idx
        self.show_current(idx)

    def __len__(self):
        return len(self.listed_objects)

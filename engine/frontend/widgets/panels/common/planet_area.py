from engine.frontend.widgets.basewidget import BaseWidget
from engine.frontend.globales import COLOR_AREA, Group
from engine.equations.space import Universe
from pygame import Surface, Rect


class ListedArea(BaseWidget):
    name = 'Astronomical Objects'

    last_id = None

    listed_type = None

    offset = 0

    stored_objects = None

    current = None

    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)
        self.image = Surface((w, h))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.shown_area = Rect(self.rect.x, self.rect.y + 10, self.rect.w, self.rect.h - 10)
        self.listed_objects = Group()
        self.stored_objects = {}

        self.f = self.crear_fuente(14, underline=True)
        self.write(self.name, self.f, midtop=(self.rect.w / 2, 0), bg=COLOR_AREA)

    def populate(self, population, layer):
        if layer not in self.stored_objects:
            self.stored_objects[layer] = {}

            for i, obj in enumerate(population):
                x = self.rect.x + 3
                y = i * 18 + self.rect.y + 21
                listed_obj = self.listed_type(self, obj, str(obj), x, y)
                if obj.id not in self.stored_objects[layer]:
                    self.stored_objects[layer][obj.id] = listed_obj

        for listed in [self.stored_objects[layer][idx] for idx in self.stored_objects[layer]]:
            if listed not in self.listed_objects.get_widgets_from_layer(layer):
                self.listed_objects.add(listed, layer=layer)

        if self.last_id is None and layer is not None:
            self.last_id = layer
        self.sort()

    def hide(self):
        for listed in self.listed_objects.widgets():
            listed.hide()
        super().hide()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if event.data['button'] == 1:
                self.deselect_all()
            elif len(self.listed_objects.widgets()):
                buttons = self.listed_objects.get_widgets_from_layer(self.last_id)
                by_mass = sorted(buttons, key=lambda b: b.object_data.mass.to('earth_mass').m, reverse=1)
                last_is_hidden = not by_mass[-1].is_visible
                first_is_hidden = not by_mass[0].is_visible
                if event.data['button'] == 4 and first_is_hidden:
                    self.offset += 16
                elif event.data['button'] == 5 and last_is_hidden:
                    self.offset -= 16

    def reset_offset(self):
        self.offset = 0

    def delete_objects(self, astronomical_object):
        layer = self.last_id
        widgets = self.listed_objects.get_widgets_from_layer(layer)
        listed = [i for i in widgets if i.object_data is astronomical_object]
        if len(listed):
            listed[0].kill()
            self.listed_objects.remove(listed[0])
        self.sort(layer)

    def sort(self, _layer=None):
        layer = self.last_id if _layer is None else _layer
        widgets = self.listed_objects.get_widgets_from_layer(layer)
        by_mass = sorted(widgets, key=lambda b: b.object_data.mass.to('earth_mass').m, reverse=1)
        for i, listed in enumerate(by_mass):
            listed.rect.y = i * 16 + self.rect.y + self.offset + 21

    def select_one(self, it):
        self.deselect_all()
        self.current = it
        it.select()

    def clear(self):
        self.listed_objects.clear()
        self.stored_objects.clear()

    def deselect_all(self):
        self.image.fill(COLOR_AREA, [0, 21, self.rect.w, self.rect.h])
        self.current = None
        for listed in self.listed_objects.get_widgets_from_layer(self.last_id):
            listed.deselect()

    def disable_by_type(self, selected_type):
        for listed in self.listed_objects.get_widgets_from_layer(self.last_id):
            if listed.object_data.celestial_type == selected_type:
                listed.disable()

    def enable_all(self):
        for listed in self.listed_objects.get_widgets_from_layer(self.last_id):
            listed.enable()

    def disable_object(self, selected_object):
        for listed in self.listed_objects.get_widgets_from_layer(self.last_id):
            if listed.object_data == selected_object:
                listed.disable()

    def objects(self):
        return [o.object_data for o in self.listed_objects.get_widgets_from_layer(self.last_id)]

    def show_current(self, idx):
        self.sort()
        for listed in self.listed_objects.widgets():
            listed.hide()
        for listed in self.listed_objects.get_widgets_from_layer(idx):
            if self.shown_area.contains(listed):
                listed.show()

    def remove_listed(self, listed):
        self.listed_objects.remove(listed)
        self.sort(listed.object_data.neighbourhood_id)

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
        if Universe.current_galaxy is not None:
            idx = Universe.current_planetary().id
        else:
            idx = self.last_id

        if idx != self.last_id:
            self.last_id = idx
        self.show_current(idx)

    def lock(self):
        for listed in self.listed_objects.widgets():
            listed.disable()

    def unlock(self):
        for listed in self.listed_objects.widgets():
            listed.enable()

    def __len__(self):
        return len(self.listed_objects)

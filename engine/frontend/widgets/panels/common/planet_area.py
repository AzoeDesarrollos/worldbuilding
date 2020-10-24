from engine.frontend.globales import COLOR_AREA, COLOR_TEXTO, WidgetGroup
from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface


class ListedArea(BaseWidget):

    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)
        self.image = Surface((w, h))
        self.image.fill(COLOR_AREA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.listed_objects = WidgetGroup()

        self.f = self.crear_fuente(14, underline=True)
        self.write('Astronomical Objects', self.f, midtop=(self.rect.w / 2, 0))

    def write(self, text, fuente, **kwargs):
        render = fuente.render(text, True, COLOR_TEXTO, COLOR_AREA)
        render_rect = render.get_rect(**kwargs)
        self.image.blit(render, render_rect)

    def populate(self, objects):
        return NotImplemented

    def hide(self):
        for listed in self.listed_objects.widgets():
            listed.hide()
        super().hide()

    def delete_objects(self, astronomical_object):
        for listed in self.listed_objects.widgets():
            if listed.object_data is astronomical_object:
                listed.kill()
        self.sort()

    def sort(self):
        for i, listed in enumerate(self.listed_objects.widgets()):
            listed.rect.y = i * 16 + self.rect.y + 21

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))

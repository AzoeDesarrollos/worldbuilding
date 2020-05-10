from engine.frontend.globales import Renderer, WidgetHandler, ANCHO, ALTO, COLOR_TEXTO, COLOR_BOX, COLOR_AREA
from engine.frontend.widgets.basewidget import BaseWidget
from pygame.sprite import LayeredUpdates
from pygame import Surface, font
from .planet_panel import Meta


class OrbitPanel(BaseWidget):
    current = None

    curr_x = 0
    curr_y = 440

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])

        self.f = font.SysFont('Verdana', 16)
        self.f.set_underline(True)
        render = self.f.render(self.name + ' Panel', 1, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(centerx=self.rect.centerx, y=0)
        self.image.blit(render, render_rect)

        f2 = font.SysFont('Verdana', 14)
        f2.set_underline(True)
        r = f2.render('Orbits', 1, COLOR_TEXTO, COLOR_AREA)
        rr = r.get_rect(topleft=(0, 420))
        self.image.blit(r, rr)

        self.orbits = LayeredUpdates()
        self.orbit_buttons = LayeredUpdates()
        self.properties = LayeredUpdates()

    def populate(self):
        self.parent.system.add_orbits()
        for orbit in self.parent.system.raw_orbits:
            button = OrbitButton(self, orbit, self.curr_x, self.curr_y)
            self.orbits.add(OrbitType(self, orbit))
            if self.curr_x + button.w + 10 < self.rect.w - button.w + 10:
                self.curr_x += button.w + 10
            else:
                self.curr_x = 0
                self.curr_y += 32
            self.orbit_buttons.add(button)
            button.enable()

    def match(self, button):
        # print(self.parent.system.planets)
        self.image.fill(COLOR_BOX, [0, 64, 100, 100])
        for orbit in self.orbits:
            orbit.hide()
            if orbit.data == button.data:
                self.current = orbit

        for btn in self.orbit_buttons:
            btn.unlock()
        button.lock()
        self.current.show()

    def show(self):
        if not len(self.orbits):
            self.populate()
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)
        for b in self.orbit_buttons:
            b.show()

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
        for b in self.orbit_buttons:
            b.hide()


class OrbitType(BaseWidget):
    def __init__(self, parent, orbit):
        super().__init__(parent)
        self.data = orbit
        self.properties = LayeredUpdates()
        for i, prop in enumerate(['semi_major_axis', 'temperature']):
            value = getattr(orbit, prop)
            if not type(value) is str:
                # noinspection PyStringFormat
                value = '{:~,g}'.format((round(value, 3)))
            p = ' '.join(prop.capitalize().split('_'))
            self.properties.add(OrbitalProperty(self, 0, 64 + i * 21, p, value))

    def show(self):
        for p in self.properties:
            p.show()

    def hide(self):
        for p in self.properties:
            p.hide()


class OrbitalProperty(BaseWidget):
    def __init__(self, parent, x, y, name, value):
        super().__init__(parent)
        text = name + ': ' + str(value)
        f = font.SysFont('Verdana', 16)
        self.image = f.render(text, 1, COLOR_TEXTO, COLOR_BOX)
        self.rect = self.image.get_rect(topleft=(x, y))

    def show(self):
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)

    def hide(self):
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)


class OrbitButton(Meta, BaseWidget):
    locked = False

    def __init__(self, parent, orbit, x, y):
        super().__init__(parent)
        self.data = orbit
        self.f1 = font.SysFont('Verdana', 14)
        self.f2 = font.SysFont('Verdana', 14, bold=True)
        self.img_uns = self.f1.render(str(orbit), 1, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(str(orbit), 1, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.match(self)

    def update(self):
        if self.enabled:
            if self.selected:
                self.image = self.img_sel
            else:
                self.image = self.img_uns

            if not self.locked:
                self.selected = False

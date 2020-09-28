from engine.frontend.globales import Renderer, WidgetHandler, ANCHO, ALTO, COLOR_TEXTO, COLOR_BOX, COLOR_AREA
from engine.frontend.widgets.basewidget import BaseWidget
from engine.frontend.globales.group import WidgetGroup
from engine.equations.planetary_system import system
from pygame import Surface, font
from ..values import ValueText
from .planet_panel import Meta
from engine import q


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
        render = self.f.render(self.name + ' Panel', True, COLOR_TEXTO, COLOR_BOX)
        render_rect = render.get_rect(centerx=self.rect.centerx, y=0)
        self.image.blit(render, render_rect)

        f2 = font.SysFont('Verdana', 14)
        f2.set_underline(True)
        r = f2.render('Orbits', True, COLOR_TEXTO, COLOR_AREA)
        rr = r.get_rect(topleft=(0, 420))
        self.image.blit(r, rr)

        self.f3 = font.SysFont('Verdana', 16)
        self.orbits = WidgetGroup()
        self.orbit_buttons = WidgetGroup()
        self.properties = WidgetGroup()

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
        self.image.fill(COLOR_BOX, [0, 64, 100, 100])
        for orbit in self.orbits.widgets():
            orbit.hide()
            if orbit.data == button.data:
                self.current = orbit

        for btn in self.orbit_buttons.widgets():
            btn.unlock()
        button.lock()
        self.current.clear()
        self.current.show()
        self.ask()

    def reverse_match(self, orbit):
        for button in self.orbit_buttons.widgets():
            if button.data == orbit:
                button.create(orbit)
                break

    def ask(self):
        p = self.parent.system.current
        if p is not None:
            o = self.current.data
            text = 'Put planet {a} at orbit {b}?'.format(a=p, b=str(o))
            question = self.f3.render(text, True, COLOR_TEXTO, COLOR_BOX)
            qrect = question.get_rect(centerx=self.rect.centerx, centery=self.rect.centerx - 50)
            self.image.blit(question, qrect)
            yes = ConfirmationButton(self, 'Yes', qrect.centerx - 50, qrect.bottom + 16, lambda: self.vinculate(p, o))
            no = ConfirmationButton(self, 'No', qrect.centerx + 45, qrect.bottom + 16, lambda: self.clear())
            # noinspection PyTypeChecker
            self.properties.add(yes, no, layer=40)
            yes.show()
            no.show()

    def organize_buttons(self):
        self.curr_x = 0
        self.curr_y = 440
        for button in [o for o in self.orbit_buttons.widgets() if not o.hidden]:
            button.rect.topleft = self.curr_x, self.curr_y
            if self.curr_x + button.w + 10 < self.rect.w - button.w + 10:
                self.curr_x += button.w + 10
            else:
                self.curr_x = 0
                self.curr_y += 32

    def vinculate(self, planet, orbit):
        self.clear()
        orb = self.parent.system.put_in_star_orbit(planet, orbit)
        self.current.data = orb
        self.current.create()
        self.organize_buttons()
        self.parent.system.clear()

    def clear(self):
        self.current.hide()
        self.image.fill(COLOR_BOX, [0, 50, self.rect.w, 300])
        for sprite in self.properties.get_widgets_from_layer(40):
            sprite.hide()
        for btn in self.orbit_buttons.widgets():
            btn.unlock()

    def show(self):
        if system is not None:
            self.populate()
        if self.current is not None:
            self.current.show()
        Renderer.add_widget(self)
        WidgetHandler.add_widget(self)
        for b in self.orbit_buttons.widgets():
            b.show()

    def hide(self):
        if self.current is not None:
            self.current.hide()
        Renderer.del_widget(self)
        WidgetHandler.del_widget(self)
        for b in self.orbit_buttons.widgets():
            b.hide()

    def __repr__(self):
        return 'Orbit Panel'


class OrbitType(BaseWidget):
    def __init__(self, parent, orbit):
        super().__init__(parent)
        self.data = orbit
        self.properties = WidgetGroup()
        self.create()

    def create(self):
        props = ['semi_major_axis', 'semi_minor_axis', 'eccentricity', 'inclination',
                 'periapsis', 'apoapsis', 'motion', 'temperature']
        for i, prop in enumerate([j for j in props if hasattr(self.data, j)]):
            _value = getattr(self.data, prop)
            vt = ValueText(self, prop, 0, 64 + i * 21, COLOR_TEXTO, COLOR_BOX)
            value = _value
            if not type(_value) is str:
                value = str(round(_value, 3))
            vt.text_area.value = value
            vt.text_area.inner_value = _value if type(_value) is not str else None
            vt.text_area.update()
            self.properties.add(vt)

    def fill(self):
        for elemento in self.properties.widgets():
            if elemento.text not in ['motion', 'temperature']:
                value = q(*elemento.text_area.value.split(' '))
            else:
                value = str(elemento.text_area.value)
            setattr(self.data, elemento.text.lower(), value)
            self.parent.reverse_match(self.data)
            elemento.text_area.value = value
            elemento.text_area.update_inner_value(value)
            elemento.text_area.update()
            elemento.text_area.show()

    def clear(self):
        self.properties.empty()

    def show(self):
        if not len(self.properties):
            self.create()

        for p in self.properties.widgets():
            p.show()

    def hide(self):
        for p in self.properties.widgets():
            p.text_area.hide()
            p.hide()


class OrbitButton(Meta, BaseWidget):
    locked = False
    hidden = False

    def __init__(self, parent, orbit, x, y):
        super().__init__(parent)
        self.data = orbit
        self.f1 = font.SysFont('Verdana', 14)
        self.f2 = font.SysFont('Verdana', 14, bold=True)
        self.create(orbit)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def create(self, orbit):
        self.img_uns = self.f1.render(str(orbit), True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(str(orbit), True, COLOR_TEXTO, COLOR_AREA)
        self.img_dis = self.f1.render(str(orbit), True, (200, 200, 200), COLOR_AREA)

    def show(self):
        super().show()
        self.hidden = False

    def hide(self):
        super().hide()
        self.hidden = True

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


class ConfirmationButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, texto, x, y, function):
        super().__init__(parent)
        self.function = function
        f1 = font.SysFont('Verdana', 16)
        f2 = font.SysFont('Verdana', 16, bold=True)
        self.img_uns = f1.render(texto, True, COLOR_TEXTO, COLOR_BOX)
        self.img_sel = f2.render(texto, True, COLOR_TEXTO, COLOR_BOX)
        self.image = self.img_uns
        self.rect = self.image.get_rect(center=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.function()

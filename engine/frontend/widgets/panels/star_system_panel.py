from engine.frontend.globales import WidgetGroup, ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_TEXTO
from engine.frontend.widgets.panels.common import ListedArea, ListedBody, TextButton, Meta
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.equations.binary import system_type
from ..values import ValueText
from pygame import Surface


class StarSystemPanel(BaseWidget):
    selected = None
    curr_x = 0
    curr_y = 440

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Star System'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.f2 = self.crear_fuente(14, underline=True)
        self.write('Star Systems', self.f2, COLOR_AREA, x=3, y=420)
        self.properties = WidgetGroup()
        self.f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', self.f1, centerx=(ANCHO//4)*1.5, y=0)
        self.stars_area = AvailableStars(self, ANCHO - 200, 32, 200, 350)
        self.properties.add(self.stars_area)
        self.current = SystemType(self)
        self.properties.add(self.current)
        self.systems = []
        self.setup_button = SetupButton(self, 490, 416)
        self.properties.add(self.setup_button)
        self.system_buttons = WidgetGroup()

    def set_current(self, system_data):
        self.current.reset(system_data)

    def create_button(self, system_data):
        button = SystemButton(self, system_data, self.curr_x, self.curr_y)
        self.systems.append(system_data)
        self.system_buttons.add(button)
        self.properties.add(button)
        self.sort_buttons()

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.system_buttons.widgets():
            bt.move(x, y)
            if not self.area_buttons.contains(bt.rect):
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()
        if len(self.systems) or len(self.stars_area):
            for s in self.systems+self.stars_area.objects():
                Systems.set_system(s)

        self.systems.clear()


class SystemType(BaseWidget):
    locked = False
    has_values = False
    current = None

    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.primary = None
        self.secondary = None
        self.separation = None
        self.ecc_p = None
        self.ecc_s = None
        self.create()
        EventHandler.register(self.clear, 'ClearData')

    def create(self):
        props = [
            'Primary Star', 'Secondary Star', 'Average Separation', 'Eccentriciy (primary)', 'Eccentricty (secondary)',
            'Barycenter', 'Maximun Separation', 'Minimun Separation', 'Forbbiden Zone Inner edge',
            'Forbbiden Zone Outer edge', 'System Type']

        for i, prop in enumerate([j for j in props]):
            self.properties.add(ValueText(self, prop, 3, 64 + i * 25, COLOR_TEXTO, COLOR_BOX))

        attrs = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        for idx, attr in enumerate(attrs):
            setattr(self, attr, self.properties.get_sprite(idx))

    def set_star(self, star):
        if str(self.primary.value) == '':
            self.primary.value = star
        else:
            self.secondary.value = star

    def get_determinants(self):
        names = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        dets = [self.primary.value, self.secondary.value]
        return dets + [float(getattr(self, name).value) for name in names if name not in ('primary', 'secondary')]

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:4]]):
            self.current = system_type(self.separation.value)(*self.get_determinants())
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep',
                     'min_sep', 'inner_forbbiden_zone', 'outer_forbbiden_zone', 'system_name']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            self.parent.setup_button.enable()

    def reset(self, system_data):
        primary = system_data.primary
        secondary = system_data.secondary
        self.set_star(primary)
        self.set_star(secondary)
        self.separation.value = system_data.average_separation
        self.ecc_p.value = system_data.ecc_p
        self.ecc_s.value = system_data.ecc_s
        self.fill()

    def clear(self, event):
        if event.data['panel'] is self.parent:
            self.erase()

    def erase(self):
        for button in self.properties.widgets():
            button.text_area.clear()
        self.has_values = False
        self.current = None

    def show(self):
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        for prop in self.properties.widgets():
            prop.hide()


class AvailableStars(ListedArea):
    def populate(self, stars):
        for i, star in enumerate(stars):
            listed = ListedStar(self, star, i, self.rect.x + 3, i * 16 + self.rect.y + 21)
            self.listed_objects.add(listed)

    def __len__(self):
        return len(self.listed_objects)

    def objects(self):
        return [o.object_data for o in self.listed_objects.widgets()]

    def show(self):
        super().show()
        self.populate(Systems.loose_stars)
        for listed in self.listed_objects.widgets():
            listed.show()


class ListedStar(ListedBody):
    enabled = True

    def __init__(self, parent, star, idx, x, y):
        name = star.classification + ' #{}'.format(idx)
        super().__init__(parent, star, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.parent.current.set_star(self.object_data)
            Systems.del_star(self.object_data)
            self.kill()
            self.parent.sort()

    def move(self, x, y):
        self.rect.topleft = x, y


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1:
            sistema = self.parent.current.current
            self.parent.create_button(sistema)
            self.parent.current.erase()
            self.disable()


class SystemButton(Meta, BaseWidget):
    enabled = True

    def __init__(self, parent, system_data, x, y):
        super().__init__(parent)
        self.system_data = system_data
        name = system_data.letter+'-Type'
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.show_current(self.system_data)

    def move(self, x, y):
        self.rect.topleft = x, y

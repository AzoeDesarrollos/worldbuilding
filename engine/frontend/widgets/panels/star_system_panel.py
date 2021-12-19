from engine.frontend.globales import WidgetGroup, ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_TEXTO
from .common import ListedArea, ColoredBody, TextButton, Group
from engine.frontend.widgets.basewidget import BaseWidget
from engine.equations.planetary_system import Systems
from engine.backend.eventhandler import EventHandler
from engine.equations.binary import system_type
from engine.frontend.widgets.meta import Meta
from ..values import ValueText
from pygame import Surface


class StarSystemPanel(BaseWidget):
    selected = None
    curr_x = 0
    curr_y = 440
    skip = False
    skippable = True

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
        self.write(self.name + ' Panel', self.f1, centerx=(ANCHO // 4) * 1.5, y=0)
        self.stars_area = AvailableStars(self, ANCHO - 200, 32, 200, 340)

        self.current = SystemType(self)

        self.systems = []
        self.setup_button = SetupButton(self, 484, 416)
        self.dissolve_button = DissolveButton(self, 334, 416)
        self.undo_button = UndoButton(self, 234, 416)
        self.properties.add(self.setup_button, self.dissolve_button, self.undo_button, self.stars_area, self.current)
        self.system_buttons = Group()
        EventHandler.register(self.save_systems, 'Save')
        EventHandler.register(self.load_systems, 'LoadData')
        EventHandler.register(self.name_current, 'NameObject')

    def name_current(self, event):
        if event.data['object'] in self.systems:
            system = event.data['object']
            system.set_name(event.data['name'])

    def set_current(self, system_data):
        self.current.reset(system_data)

    def show_current(self, star):
        self.current.erase()
        self.current.current = star
        self.current.reset(star)

    def create_button(self, system_data):
        if system_data not in self.systems:
            idx = len([s for s in self.systems if system_data.compare(s) is True])
            button = SystemButton(self, system_data, idx, self.curr_x, self.curr_y)
            self.systems.append(system_data)
            self.system_buttons.add(button)
            self.properties.add(button)
            self.sort_buttons()
            Systems.set_system(system_data)
            self.current.enable()
            return button

    def sort_buttons(self):
        x, y = self.curr_x, self.curr_y
        for bt in self.system_buttons.widgets():
            bt.move(x, y)
            if not self.area_buttons.contains(bt.rect) or not self.is_visible:
                bt.hide()
            else:
                bt.show()
            if x + bt.rect.w + 10 < self.rect.w - bt.rect.w + 10:
                x += bt.rect.w + 10
            else:
                x = 3
                y += 32

    def save_systems(self, event):
        data = {}
        for button in self.system_buttons.widgets():
            current = button.object_data
            if current.celestial_type == 'system':
                d = {
                    'primary': current.primary.id,
                    'secondary': current.secondary.id,
                    'avg_s': current.average_separation.m,
                    'ecc_p': current.ecc_p.m,
                    "ecc_s": current.ecc_s.m,
                    "name": current.name,
                    'pos': dict(zip(['x', 'y', 'z'], current.position))
                }
                data[current.id] = d

        EventHandler.trigger(event.tipo + 'Data', 'Systems', {'Binary Systems': data})

    def load_systems(self, event):
        for id in event.data['Binary Systems']:
            system_data = event.data['Binary Systems'][id]
            avg_s = system_data['avg_s']
            ecc_p = system_data['ecc_p']
            ecc_s = system_data['ecc_s']
            prim = Systems.get_star_by_id(system_data['primary'])
            scnd = Systems.get_star_by_id(system_data['secondary'])
            name = system_data['name']
            pos = system_data['pos']

            system = system_type(avg_s)(prim, scnd, avg_s, ecc_p, ecc_s, pos, id=id, name=name)
            button = self.create_button(system)
            button.hide()
            # Systems.set_system(system)
        self.sort_buttons()

    def select_one(self, btn):
        for button in self.system_buttons.widgets():
            button.deselect()
        btn.select()

    def del_button(self, system):
        button = [i for i in self.system_buttons.widgets() if i.object_data == system][0]
        self.systems.remove(system)
        self.system_buttons.remove(button)
        self.sort_buttons()
        self.properties.remove(button)
        self.dissolve_button.disable()
        if system in self.systems:
            Systems.dissolve_system(system)

    def show(self):
        for system in Systems.get_systems():
            self.create_button(system.star_system)
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()
        for star_widget in self.stars_area.listed_objects.widgets():
            star = star_widget.object_data
            Systems.set_system(star)


class SystemType(BaseWidget):
    locked = False
    has_values = False
    current = None

    primary = None
    secondary = None
    separation = None
    ecc_p = None
    ecc_s = None

    def __init__(self, parent, props=None):
        super().__init__(parent)
        self.properties = WidgetGroup()

        if props is None:
            props = [
                'Primary Star', 'Secondary Star', 'Average Separation',
                'Eccentriciy (primary)', 'Eccentricty (secondary)',
                'Barycenter', 'Maximun Separation', 'Minimun Separation',
                'Forbbiden Zone Inner edge', 'Forbbiden Zone Outer edge',
                'System Type', 'System Name']

        self.create(props)
        EventHandler.register(self.clear, 'ClearData')

    def create(self, props):
        for i, prop in enumerate([j for j in props]):
            vt = ValueText(self, prop, 3, 64 + i * 25, COLOR_TEXTO, COLOR_BOX)
            self.properties.add(vt, layer=2)
            if i in [2, 3, 4]:
                vt.modifiable = True
            if i in [0, 1]:
                vt.enable()

        attrs = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        for idx, attr in enumerate(attrs):
            setattr(self, attr, self.properties.get_sprite(idx))

    def set_star(self, star):
        if str(self.primary.value) == '':
            self.primary.value = star
            self.has_values = True
        else:
            self.secondary.value = star
            self.parent.undo_button.enable()
            self.has_values = True

        if self.primary.value != '' and self.secondary.value != '':
            for obj in self.properties.get_widgets_from_layer(2):
                obj.enable()

    def unset_stars(self):
        self.parent.stars_area.populate(Systems.loose_stars)
        self.erase()

    def get_determinants(self):
        names = ['primary', 'secondary', 'separation', 'ecc_p', 'ecc_s']
        dets = [self.primary.value, self.secondary.value]
        return dets + [float(getattr(self, name).value) for name in names if name not in ('primary', 'secondary')]

    def fill(self):
        if all([str(vt.value) != '' for vt in self.properties.widgets()[0:5]]):
            if self.current is None:
                self.current = system_type(self.separation.value)(*self.get_determinants())
            props = ['average_separation', 'ecc_p', 'ecc_s', 'barycenter', 'max_sep',
                     'min_sep', 'inner_forbbiden_zone', 'outer_forbbiden_zone', 'system_name', 'name']
            for i, attr in enumerate(props, start=2):
                value = getattr(self.current, attr)
                pr = self.properties.get_widget(i)
                pr.value = value
            self.parent.setup_button.enable()

    def reset(self, system_data):
        self.set_star(system_data.primary)
        self.set_star(system_data.secondary)
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

    def destroy(self):
        self.parent.del_button(self.current)
        self.erase()

    def show(self):
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        for prop in self.properties.widgets():
            prop.hide()

    def enable(self):
        super().enable()
        for arg in self.properties.widgets():
            arg.enable()


class ListedStar(ColoredBody):
    enabled = True

    def on_mousebuttondown(self, event):
        if event.button == 1:
            self.parent.parent.current.set_star(self.object_data)
            self.parent.remove_listed(self)
            self.kill()
            self.parent.sort()

    def move(self, x, y):
        self.rect.topleft = x, y

    def __repr__(self):
        return f'Listed: {str(self.object_data)}'


class AvailableStars(ListedArea):
    name = 'Stars'
    listed_type = ListedStar

    def show(self):
        self.populate(Systems.loose_stars, layer=0)
        super().show()

    def update(self):
        self.image.fill(COLOR_AREA, (0, 17, self.rect.w, self.rect.h - 17))
        self.show_current(0)


class SetupButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Add System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            sistema = self.parent.current.current
            self.parent.create_button(sistema)
            self.parent.current.erase()
            self.disable()


class DissolveButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Dissolve System'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        if event.button == 1 and self.enabled:
            system = self.parent.current.current
            Systems.dissolve_system(system)
            self.parent.stars_area.show()
            self.parent.current.destroy()


class SystemButton(Meta):
    enabled = True

    def __init__(self, parent, system_data, idx, x, y):
        super().__init__(parent)
        system_data.idx = idx
        self.object_data = system_data
        name = str(system_data)
        self.f1 = self.crear_fuente(13)
        self.f2 = self.crear_fuente(13, bold=True)
        self.img_uns = self.f1.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.img_sel = self.f2.render(name, True, COLOR_TEXTO, COLOR_AREA)
        self.w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if self.object_data.letter is not None:
                self.parent.show_current(self.object_data)
            else:
                self.parent.current.current = self.object_data
            self.parent.setup_button.disable()
            self.parent.select_one(self)
            self.parent.dissolve_button.enable()

    def move(self, x, y):
        self.rect.topleft = x, y


class UndoButton(TextButton):
    enabled = False

    def __init__(self, parent, x, y):
        name = 'Undo'
        super().__init__(parent, name, x, y)

    def on_mousebuttondown(self, event):
        self.parent.current.unset_stars()
        self.disable()

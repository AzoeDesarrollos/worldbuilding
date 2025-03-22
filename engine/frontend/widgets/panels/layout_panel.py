from engine.frontend.widgets.basewidget import BaseWidget
from pygame import Surface, draw, transform, SRCALPHA
from engine.frontend.globales.constantes import *
from engine.frontend.globales.group import Group
from engine.frontend.widgets.meta import Meta
from engine.equations.space import Universe
from engine.backend.util import abrir_json
from engine.backend.config import Config
from engine.backend import EventHandler
from os.path import exists, join
from os import getcwd
from . import panels


class LayoutPanel(BaseWidget):
    curr_idx = 0

    def __init__(self):
        super().__init__()
        self.image = Surface((ANCHO, ALTO))
        self.image.fill(COLOR_SELECTED)
        self.rect = self.image.get_rect()
        self.name = 'Layout'

        self.properties = Group()

        self.panels = []
        for panel in panels:
            self.panels.append(panel(self))

        self.current = self.panels[self.curr_idx]
        self.current.show()

        a = Arrow(self, 'backward', 180, self.rect.left + 16, self.rect.bottom)
        b = Arrow(self, 'forward', 0, self.rect.right - 16, self.rect.bottom)

        e = NewButton(self, 100, ALTO - 28)
        d = LoadButton(self, 210, ALTO - 27)
        c = SaveButton(self, 340, ALTO - 27)
        j = ExportButton(self, 470, ALTO + -28)

        f = SwapSystem(self, ANCHO - 220, 2, 'System')
        g = SwapGalaxy(self, 0, 2)
        h = SwapNeighbourhood(self, 150, 2, 'Neighbourhood')

        self.load_button = d
        self.swap_galaxy_button = g
        self.swap_neighbourhood_button = h

        self.properties.add(a, b, c, d, e, f, g, h, j, layer=1)

    def cycle(self, delta):
        if self.curr_idx + delta < 0:
            self.curr_idx = len(self.panels) - 1
        elif self.curr_idx + delta > len(self.panels) - 1:
            self.curr_idx = 0
        else:
            self.curr_idx += delta

        self.current.hide()
        self.current = self.panels[self.curr_idx]
        ignore_rules = Config.get('ignore skip-rules')
        start_rule = self.current.name == 'Start'
        if all([self.current.skippable, self.current.skip, [not ignore_rules or start_rule]]):
            self.cycle(delta)
            return  # si se saltea un panel, no hay que mostrar el panel siguiente 2 veces.
        self.current.show()

    def set_skippable(self, name, value):
        ignore_rules = Config.get('ignore skip-rules')
        if ignore_rules is False:
            panel = [i for i in self.panels if i.name == name][0]
            panel.skip = value

    def __repr__(self):
        return 'Layout Panel'

    def show(self):
        super().show()
        for widget in self.properties.get_widgets_from_layer(1):
            widget.show()

    def hide(self):
        super().hide()
        for widget in self.properties.get_widgets_from_layer(1):
            widget.hide()


class Arrow(Meta):
    enabled = True

    def __init__(self, parent, direccion, angulo, centerx, y):
        super().__init__(parent)
        self.direccion = direccion

        self.img_uns = self.create(COLOR_BOX, angulo)
        self.img_sel = self.create(COLOR_TEXTO, angulo)
        self.img_dis = self.create(COLOR_DISABLED, angulo)

        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=centerx, bottom=y)

    @staticmethod
    def create(color, angulo):
        img = Surface((32, 32), SRCALPHA)
        draw.polygon(img, color, [[1, 13], [20, 13], [20, 5], [30, 14], [20, 26], [20, 18], [1, 17]])
        image = transform.rotate(img, angulo)
        return image

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            if self.rect.collidepoint(event.data['pos']):
                if self.enabled:
                    if self.direccion == 'forward':
                        self.parent.cycle(+1)
                    elif self.direccion == 'backward':
                        self.parent.cycle(-1)

    def __repr__(self):
        return 'Arrow ({})'.format(self.direccion)


class BaseButton(Meta):
    enabled = True

    def __init__(self, parent, x, y, text):
        super().__init__(parent)
        f1 = self.crear_fuente(16)
        f2 = self.crear_fuente(16, bold=True)
        self.img_uns = f1.render(text, True, COLOR_TEXTO, COLOR_SELECTED)
        self.img_sel = f2.render(text, True, COLOR_TEXTO, COLOR_SELECTED)
        self.img_dis = f1.render(text, True, COLOR_DISABLED, COLOR_SELECTED)
        self.image = self.img_uns
        self.rect = self.image.get_rect(centerx=x, y=y)


class SaveButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Save')

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            EventHandler.trigger('Save', 'SaveButton', {})
            self.parent.load_button.reset()


class LoadButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Load')
        if self.check_data() is None:
            self.disable()

    @staticmethod
    def check_data():
        ruta = join(getcwd(), 'data', 'savedata.json')
        if exists(ruta):
            data = abrir_json(ruta)
            if any([data[item] for item in data]):
                return data

    def reload(self):
        idx = self.parent.curr_idx
        for x in range(idx):
            panel = self.parent.panels[x]
            panel.hide()

    def reset(self):
        if self.check_data() is not None:
            self.enable()

    def on_mousebuttondown(self, event):
        if event.origin == self and self.enabled:
            data = self.check_data()
            keys = 'Galaxies,Neighbourhoods,Stars,Compact,Binary,Single,Planets,'
            keys += 'Satellites,Asteroids,Stellar Orbits,Planetary Orbits,Calendars'
            self.disable()
            for body in keys.split(','):
                EventHandler.trigger(f'Load{body}', 'LoadButton', data)
                EventHandler.process()
            self.reload()


class NewButton(BaseButton):

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'New')

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            EventHandler.trigger('ClearData', 'NewButton', {'panel': self.parent.current})


class SwapSystem(Meta):
    enabled = False
    system_image = None
    current = None

    def __init__(self, parent, x, y, name):
        super().__init__(parent)
        self.layer = 7
        self.f1 = self.crear_fuente(13, bold=True)
        self.f2 = self.crear_fuente(13)
        self.img_sel = self.f1.render(f'{name}: ', True, COLOR_TEXTO, COLOR_BOX)
        self.img_uns = self.f2.render(f'{name}: ', True, COLOR_TEXTO, COLOR_BOX)
        self.img_dis = self.f1.render(f'{name}: ', True, COLOR_DISABLED, COLOR_BOX)
        self.image = self.img_dis
        self.rect = self.image.get_rect(topleft=(x, y))
        self.create_img()

    def create_img(self):
        self.system_image = SystemName(self, left=self.rect.right + 6, y=2)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            self.current = Universe.nei().cycle_systems()
            self.system_image.render_name()

    def update(self):
        super().update()
        current = Universe.nei()
        if current is not None:
            if not self.enabled and self.parent.current.show_swap_system_button is True:
                self.enable()
                self.current = current.get_current()
                self.system_image.enable()

    def show(self):
        super().show()
        if self.system_image is not None:
            self.system_image.show()

    def hide(self):
        super().hide()
        if self.system_image is not None:
            self.system_image.hide()


class SwapGalaxy(SwapSystem):
    current = None

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Galaxy')
        EventHandler.register(self.clear, 'ClearGalaxy')

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            galaxy = Universe.cycle_galaxies()
            self.current = galaxy
            EventHandler.trigger('SwitchGalaxy', 'SwapGalaxyButton', {'current': galaxy})

    def create_img(self):
        self.system_image = GalaxyName(self, left=self.rect.right + 6, y=2)

    def update(self):
        if all([not self.has_mouseover, not self.selected, self.enabled]):
            self.image = self.img_uns
        self.has_mouseover = False

    def enable(self):
        super().enable()
        self.current = Universe.current_galaxy
        self.system_image.render_name()

    def clear(self, event):
        self.current = event.data['current']  # None
        self.system_image.render_name()


class SwapNeighbourhood(SwapSystem):
    current = None
    locked = False

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            if Universe.current_galaxy is not None:
                neighbourhood = Universe.current_galaxy.cycle_neighbourhoods()
                self.current = neighbourhood
                self.system_image.render_name()
                EventHandler.trigger('SwitchNeighbourhood', 'SwapNeighbourhoodButton', {'current': neighbourhood})

    def set_current(self):
        if Universe.current_galaxy is not None:
            self.current = Universe.current_galaxy.current_neighbourhood
            self.system_image.render_name()

    def lock(self):
        self.locked = True
        self.disable()

    def unlock(self):
        self.locked = False
        self.enable()

    def disable(self):
        super().disable()
        self.system_image.color = COLOR_DISABLED

    def enable(self):
        super().enable()
        self.system_image.render_name()

    def create_img(self):
        self.system_image = NeighbourhoodName(self, left=self.rect.right + 6, y=2)

    def update(self):
        if all([not self.has_mouseover, not self.selected, self.enabled]):
            self.image = self.img_uns
        self.has_mouseover = False


class SystemName(BaseWidget):
    color = COLOR_DISABLED
    image = None

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.f = self.crear_fuente(13)

        self.render_name()
        self._rect = self.image.get_rect(**kwargs)
        self.rect = self._rect.copy()

    def render_name(self):
        name = None
        if self.parent.parent.current.show_swap_system_button is not False:
            current = self.parent.current
            if current is not None:
                name = str(current.parent)

        if name is None:
            self.color = COLOR_DISABLED
            name = '-'
        else:
            self.color = COLOR_TEXTO

        self.image = self.f.render(name, True, self.color, COLOR_BOX)

    def enable(self):
        super().enable()
        self.render_name()


class GalaxyName(SystemName):
    def render_name(self):
        if self.parent.current is not None:
            name = self.parent.current.id.split('-')[1]
            self.color = COLOR_TEXTO

        else:
            name = '-'

        self.image = self.f.render(name, True, self.color, COLOR_BOX)


class NeighbourhoodName(SystemName):
    named = None

    def render_name(self):
        name = str(self.parent.current)
        self.named = name
        if self.parent.enabled:
            self.color = COLOR_TEXTO

        elif self.parent.locked:
            name = self.named
        else:
            name = '-'

        self.image = self.f.render(name, True, self.color, COLOR_BOX)
        # self.rect = self.image.get_rect(topleft=self._rect.topleft)


class ExportButton(BaseButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, 'Export')

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            EventHandler.trigger('ExportData', 'ExportButton', {'panel': self.parent.current})

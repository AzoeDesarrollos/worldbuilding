from engine.equations.tides import major_tides, minor_tides, is_tidally_locked
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup
from .common import AvailableObjects, AvailablePlanet
from engine.equations.planetary_system import Systems
from ..basewidget import BaseWidget
from pygame import Surface, Rect
from engine import q


class InformationPanel(BaseWidget):
    skippable = False

    current = None

    render = None
    render_rect = None

    selection = None

    def __init__(self, parent):
        self.name = 'Information'
        super().__init__(parent)
        self.properties = WidgetGroup()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.f1 = self.crear_fuente(16, underline=True)
        self.f2 = self.crear_fuente(14)
        self.f3 = self.crear_fuente(16)
        self.write(self.name + ' Panel', self.f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.properties.add(self.planet_area, layer=2)
        self.perceptions_rect = Rect(3, 250, 380, self.rect.h - 252)

    def on_mousebuttondown(self, event):
        if event.button == 4:
            if self.render_rect.top + 12 <= 250:
                self.render_rect.move_ip(0, +12)
        elif event.button == 5:
            if self.render_rect.bottom - 12 >= 589:
                self.render_rect.move_ip(0, -12)

    def show_name(self, astrobody):
        self.image.fill(COLOR_BOX, (0, 21, self.rect.w, 16))
        self.image.fill(COLOR_BOX, (3, 50, self.rect.w, 200))
        text = 'Information about ' + str(astrobody)
        self.write(text, self.f2, centerx=(ANCHO // 4) * 1.5, y=21)

        self.current = astrobody
        if self.selection is None:
            self.render = None
        self.show_selected()

    def clear(self):
        self.image.fill(COLOR_BOX)

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()

    def hide(self):
        self.clear()
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def show_selected(self):
        system = Systems.get_current()
        astrobody = self.current
        self.selection = astrobody
        diameter = astrobody.radius.to('earth_radius').m * 2

        if system.star_system.letter == 'S':
            star = system.star_system.primary
            stellar_tides = minor_tides(diameter, star.mass.m, astrobody.orbit.a.m)
        else:
            combined_mass = sum([star.mass.m for star in system.star_system])
            stellar_tides = minor_tides(diameter, combined_mass, astrobody.orbit.a.m)

        if astrobody.celestial_type == 'planet':
            lunar_tides = 0
            primary = 'moon'
            for satellite in astrobody.satellites:
                if satellite.celestial_type == 'satellite':
                    lunar_tides += major_tides(diameter, satellite.mass.m, satellite.orbit.a.to('earth_diameter').m)
        else:
            primary = 'planet'
            lunar_tides = major_tides(diameter, astrobody.orbit.star.mass.m, astrobody.orbit.a.to('earth_diameter').m)

        if stellar_tides > lunar_tides:
            primary = 'star'
        std_high = q(lunar_tides * 0.54, 'm')
        std_low = -std_high

        spring_high = q((lunar_tides + stellar_tides) * 0.54, 'm')  # meters
        spring_low = -spring_high

        neap_high = q((lunar_tides - stellar_tides) * 0.54, 'm')  # meters
        neap_low = -neap_high

        resolution = 4
        rect = self.write(f'Tides on {str(astrobody)}:', self.f3, x=3, y=50)
        rect = self.write('Standard high: {}'.format(round(std_high, resolution)), self.f2, x=3, y=rect.bottom + 4)
        rect = self.write('Standard low: {}'.format(round(std_low, resolution)), self.f2, x=3, y=rect.bottom + 2)
        rect = self.write('Spring high: {}'.format(round(spring_high, resolution)), self.f2, x=3, y=rect.bottom + 12)
        rect = self.write('Spring low: {}'.format(round(spring_low, resolution)), self.f2, x=3, y=rect.bottom + 2)
        rect = self.write('Neap high: {}'.format(round(neap_high, resolution)), self.f2, x=3, y=rect.bottom + 12)
        rect = self.write('Neap low: {}'.format(round(neap_low, resolution)), self.f2, x=3, y=rect.bottom + 2)

        if is_tidally_locked(lunar_tides, system.age.m / 10 ** 9, self.current.orbit.star.mass.m):
            text = '{} is tidally locked to its {}'.format(str(self.current), primary)
        elif is_tidally_locked(stellar_tides, system.age.m / 10 ** 9, self.current.orbit.star.mass.m):
            text = '{} is tidally locked to its {}'.format(str(self.current), primary)
        else:
            text = '{} is not tidally locked'.format(str(self.current))

        self.write(text, self.f3, x=3, y=rect.bottom + 12)

        if self.render is None:
            self.extra_info(astrobody)

    def extra_info(self, astrobody):
        self.image.fill(COLOR_BOX, self.perceptions_rect)
        system = Systems.get_current()
        visibility = system.aparent_brightness[astrobody.id]
        sizes = system.relative_sizes[astrobody.id]
        distances = system.distances[astrobody.id]
        text_lines = []
        analyzed = []
        for idx, body_id in enumerate(visibility):
            body_visibility = visibility[body_id]
            body = system.get_astrobody_by(body_id, tag_type='id', silenty=True)
            if body is False:
                for sys in Systems.get_systems():
                    if sys != system and body_id not in analyzed:
                        body = sys.get_astrobody_by(body_id, tag_type='id', silenty=True)
                        if body is not False:
                            break

            analyzed.append(body.id)
            relative_size = sizes[body_id]
            distance = distances[body_id]
            if type(body_visibility) is q:
                v = body_visibility.to('W/m^2')
                if 'e' in str(v.m):
                    valor = f"{v.m:.2e} "
                    unidad = f"{v.u:P~}"
                    formato = valor + unidad
                else:
                    formato = f'of {v:~P}'
                text = f'The star {body}, at a distance of {distance:~P} '
                text += f'has an apparent brightness, as seen from {astrobody}, ' + formato
                text += f" and a relative size of {relative_size.m} degrees in it's sky."
            elif body_visibility == 'naked':
                text = f'{body} can be seen from {astrobody} with naked human eyes'
                text += f" with a relative size of {relative_size.m} degrees in it's sky."
            elif body_visibility == 'telescope':
                text = f'Humans from {astrobody} would need a telescope to view {body}.'
                text += f" It has a relative size of {relative_size.m} degrees in it's sky."
            else:
                text = f'It is unclear if {body} could be seen from {astrobody}.'

            text_lines.append(text)

        self.render = self.write3('\n'.join(text_lines), self.f2, 380)
        self.render_rect = self.render.get_rect(topleft=[3, 250])

    def update(self):
        self.clear()
        if self.render is not None:
            self.image.blit(self.render, self.render_rect)
        self.image.fill(COLOR_BOX, [0, 0, ANCHO, 64])
        self.write(self.name + ' Panel', self.f1, centerx=(ANCHO // 4) * 1.5, y=0)
        if self.selection is not None:
            self.show_name(self.selection)


class Astrobody(AvailablePlanet):

    def on_mousebuttondown(self, event):
        self.parent.select_one(self)
        self.parent.parent.selection = None
        self.parent.parent.show_name(self.object_data)


class AvailablePlanets(AvailableObjects):
    listed_type = Astrobody
    last_idx = None

    def show(self):
        system = Systems.get_current()
        if system is not None:
            bodies = [body for body in system.astro_bodies if body.orbit is not None]
            self.populate(bodies)
        else:
            self.parent.show_no_system_error()
        super().show()

    def on_mousebuttondown(self, event):
        super().on_mousebuttondown(event)
        self.parent.clear()

    def update(self):
        idx = Systems.get_current().id
        if idx != self.last_idx:
            self.show()
            self.show_current(idx)
            self.last_idx = idx

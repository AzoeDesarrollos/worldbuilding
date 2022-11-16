from engine.equations.tides import major_tides, minor_tides, is_tidally_locked
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group
from engine.equations.planetary_system import RoguePlanets
from .common import ListedArea, ColoredBody, TextButton
from engine.backend import generate_id, Systems, q
from engine.equations.space import Universe
from ..basewidget import BaseWidget
from pygame import Surface, Rect
import os


class InformationPanel(BaseWidget):
    skippable = False

    current = None

    render = None
    render_rect = None

    text = None

    show_swawp_system_button = True

    def __init__(self, parent):
        self.name = 'Information'
        super().__init__(parent)
        self.properties = Group()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.f1 = self.crear_fuente(16, underline=True)
        self.f2 = self.crear_fuente(14)
        self.f3 = self.crear_fuente(16)
        self.write(self.name + ' Panel', self.f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.print_button = PrintButton(self, *self.planet_area.rect.midbottom)
        self.properties.add(self.planet_area, self.print_button, layer=2)
        self.perceptions_rect = Rect(3, 250, 380, ALTO)
        self.info_rect = Rect(3, self.perceptions_rect.bottom, 380, ALTO - (self.perceptions_rect.h + 380 + 21))

    def on_mousebuttondown(self, event):
        if event.origin == self:
            self.image.fill(COLOR_BOX, self.render_rect)
            if event.data['button'] == 4:
                if self.render_rect.top + 12 <= 250:
                    self.render_rect.move_ip(0, +12)
            elif event.data['button'] == 5:
                if self.render_rect.bottom - 12 >= 589:
                    self.render_rect.move_ip(0, -12)
            self.image.blit(self.render, self.render_rect)

    def show_name(self, astrobody):
        self.image.fill(COLOR_BOX, (0, 21, self.rect.w, 16))
        self.image.fill(COLOR_BOX, (3, 50, self.rect.w, 200))
        text = 'Information about ' + str(astrobody)
        self.write(text, self.f2, centerx=(ANCHO // 4) * 1.5, y=21)

    def clear(self):
        # self.image.fill(COLOR_BOX)
        self.render = None

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()

    def hide(self):
        self.clear()
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def show_selected(self, astrobody):
        system = Systems.get_current()
        self.current = astrobody
        self.show_name(astrobody)
        diameter = astrobody.radius.to('earth_radius').m * 2

        if system is not RoguePlanets:
            if system.star_system.letter == 'S':
                star = system.star_system.primary
                stellar_tides = minor_tides(diameter, star.mass.m, astrobody.orbit.a.m)
            else:
                combined_mass = sum([star.mass.m for star in system.star_system])
                stellar_tides = minor_tides(diameter, combined_mass, astrobody.orbit.a.m)
        else:
            stellar_tides = q(0, 'meter')

        if astrobody.celestial_type == 'planet':
            lunar_tides = 0
            if astrobody.rogue or astrobody.parent.celestial_type == 'star':
                primary = 'moon'
                for satellite in astrobody.satellites:
                    if satellite.celestial_type == 'satellite':
                        lunar_tides += major_tides(diameter, satellite.mass.m, satellite.orbit.a.to('earth_diameter').m)
            else:
                primary = 'planet'
                lunar_tides += major_tides(diameter, astrobody.parent.mass.m, astrobody.orbit.a.to('earth_diameter').m)
        else:
            primary = 'planet'
            lunar_tides = major_tides(diameter, astrobody.orbit.star.mass.m, astrobody.orbit.a.to('earth_diameter').m)

        if stellar_tides > lunar_tides:
            primary = 'star'
        elif astrobody.rogue:
            primary = 'rogue'
        std_high = abs(q(lunar_tides * 0.54, 'm'))
        std_low = -std_high if std_high.m != 0 else abs(std_high)

        spring_high = abs(q((lunar_tides + stellar_tides) * 0.54, 'm'))  # meters
        spring_low = -spring_high if spring_high.m != 0 else abs(spring_high)

        neap_high = abs(q((lunar_tides - stellar_tides) * 0.54, 'm'))  # meters
        neap_low = -neap_high if neap_high.m != 0 else abs(neap_high)

        rect = self.write(f'Tides on {str(astrobody)}:', self.f3, x=3, y=50)
        tides = [
            {'name': 'Standard high', 'value': std_high, 'dy': 4},
            {'name': 'Standard low', 'value': std_low, 'dy': 2},
            {'name': 'Spring high', 'value': spring_high, 'dy': 12},
            {'name': 'Spring low', 'value': spring_low, 'dy': 2},
            {'name': 'Neap high', 'value': neap_high, 'dy': 12},
            {'name': 'Neap low', 'value': neap_low, 'dy': 2}
        ]
        for tide in tides:
            name = tide['name']
            v = tide['value']
            dy = tide['dy']
            if 'e' in str(v.m):
                valor = f"{v.m:.2e} "
                unidad = f"{v.u:P~}"
                formato = valor + unidad
            else:
                formato = f'{v:.2~P}'

            rect = self.write(f'{name}: {formato}', self.f2, x=3, y=rect.bottom + dy)

        mass = None
        if primary != 'rogue':
            star = self.current.orbit.star
            if star.celestial_type == 'star':
                if star.letter is None:
                    mass = star.mass.m
                else:
                    mass = star.shared_mass.m
            else:
                mass = star.mass.m

        if primary == 'rogue':
            text = f'{str(self.current)} is a rogue planet.'
        elif is_tidally_locked(lunar_tides, system.age.m / 10 ** 9, mass):
            text = f'{str(self.current)} is tidally locked to its {primary}.'
            self.current.rotation = 'Tidally locked'
            self.current.spin = 'Locked'
        elif is_tidally_locked(stellar_tides, system.age.m / 10 ** 9, mass):
            text = f'{str(self.current)} is tidally locked to its {primary}.'
            self.current.rotation = 'Tidally locked'
            self.current.spin = 'Locked'
        else:
            text = f'{str(self.current)} is not tidally locked.'

        self.write(text, self.f3, x=3, y=rect.bottom + 12)

        self.extra_info(astrobody)

    def extra_info(self, astrobody):
        self.image.fill(COLOR_BOX, self.perceptions_rect)
        system = Systems.get_current()
        visibility = Universe.aparent_brightness[astrobody.id]
        sizes = Universe.relative_sizes[astrobody.id]
        distances = Universe.distances[astrobody.id]
        text_lines = []
        analyzed = []
        for idx, body_id in enumerate(visibility):
            body_visibility = visibility[body_id]
            body = Universe.get_astrobody_by(body_id, tag_type='id', silenty=True)
            if body is False:
                for sys in Systems.get_systems():
                    if sys != system and body_id not in analyzed:
                        body = sys.get_astrobody_by(body_id, tag_type='id', silenty=True)
                        if body is not False:
                            break

            analyzed.append(body.id)
            relative_size = sizes[body_id]
            if 'e' in str(relative_size.m):
                valor = f"{relative_size.m:.2e}"
            else:
                valor = str(relative_size.m)
            formato1 = f'of {valor}°'

            distance = round(distances[body_id], 3)
            if type(body_visibility) is q:
                v = body_visibility.to('W/m^2')
                if 'e' in str(v.m):
                    valor = f"{v.m:.2e} "
                    unidad = f"{v.u:P~}"
                    formato2 = f'of {valor + unidad}'
                else:
                    formato2 = f'of {round(v, 3):~P}'
                text = f'* The {body.celestial_type} {body}, at a distance of {distance:~P} '
                text += f'has an apparent brightness, as seen from {astrobody}, ' + formato2
                text += f" and a relative size {formato1} in it's sky."
            elif body_visibility == 'naked':
                text = f'* {body} can be seen from {astrobody} with naked human eyes'
                text += f" with a relative size {formato1} in it's sky."
            elif body_visibility == 'telescope':
                text = f'* Humans from {astrobody} would need a telescope to view {body}.'
                text += f" It has a relative size {formato1} in it's sky."
            else:
                text = f'* It is unclear if {body} could be seen from {astrobody}.'

            text_lines.append(text)
        final_text = '\n'.join(text_lines)
        self.text = final_text
        self.render = self.write3(final_text, self.f2, 380)
        if self.render_rect is None:
            self.render_rect = self.render.get_rect(topleft=[3, 250])
        self.image.fill(COLOR_BOX, self.info_rect)
        self.image.blit(self.render, self.render_rect)
        self.print_button.enable()


class Astrobody(ColoredBody):

    def on_mousebuttondown(self, event):
        if event.origin == self:
            self.parent.select_one(self)
            self.parent.parent.show_selected(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = Astrobody

    def show(self):
        systems = Systems.get_systems()
        if len(systems):
            for system in systems:
                idx = system.id
                bodies = [body for body in system.astro_bodies]
                bodies = [body for body in bodies if body.orbit is not None or body.rogue is True]
                self.populate(bodies, layer=idx)
        else:
            self.parent.show_no_system_error()
        super().show()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            super().on_mousebuttondown(event)
            self.parent.clear()


class PrintButton(TextButton):

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Print Info', x, y)
        self.rect.midtop = x, y
        self.rect.y += 10

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            ruta = os.path.join(os.getcwd(), 'exports')
            if not os.path.exists(ruta):
                os.mkdir(ruta)
            with open(os.path.join(ruta, 'export_' + generate_id() + '.txt'), 'w+t', encoding='utf-8') as file:
                for line in self.parent.text.splitlines(keepends=True):
                    file.write(line)
            self.disable()

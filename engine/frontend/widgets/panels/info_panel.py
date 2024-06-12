from engine.equations.tides import major_tides, minor_tides, is_tidally_locked
from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, Group
from .common import ListedArea, ColoredBody, TextButton
from engine.backend.eventhandler import EventHandler
from engine.equations.space import Universe
from engine.backend import generate_id, q
from ..basewidget import BaseWidget
from pygame import Surface, Rect
import os


class InformationPanel(BaseWidget):
    skippable = False
    skip = False

    current = None

    render = None
    render_rect = None

    text_render = None
    exportable_text = ''

    show_swap_system_button = True

    def __init__(self, parent):
        self.name = 'Information'
        super().__init__(parent)
        self.properties = Group()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.f1 = self.crear_fuente(14)
        self.f2 = self.crear_fuente(16)
        text = 'Click on any Astronmical Object to get information about its tide interaction and distances to other'
        text += ' celestial bodies.'
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        offset = Rect(0, 0, self.rect.w - self.planet_area.rect.w, self.rect.h)
        self.write2(text, self.crear_fuente(14), fg=COLOR_AREA, width=300, centerx=offset.centerx, y=100, j=1)
        self.print_button = PrintButton(self, *self.planet_area.rect.midbottom)
        self.properties.add(self.planet_area, self.print_button, layer=2)
        self.perceptions_rect = Rect(3, 250, 380, ALTO)
        self.info_rect = Rect(3, self.perceptions_rect.bottom, 380, ALTO - (self.perceptions_rect.h + 380 + 21))
        EventHandler.register(self.export_data, 'ExportData')

    def on_mousebuttondown(self, event):
        if event.origin == self:
            if event.data['button'] == 4:  # abajo
                if self.render_rect.top + 12 <= 250:
                    self.render_rect.move_ip(0, +12)
            elif event.data['button'] == 5:  # arriba
                if self.render_rect.bottom - 12 >= 592:
                    self.render_rect.move_ip(0, -12)

            self.render_everything()

    def show_name(self, astrobody):
        self.image.fill(COLOR_BOX, (0, 21, self.rect.w, 16))
        self.image.fill(COLOR_BOX, (3, 50, self.rect.w, 200))
        text = 'Information about ' + str(astrobody)
        self.write(text, self.f1, centerx=(ANCHO // 4) * 1.5, y=21)

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
        system = Universe.current_planetary().parent
        self.current = astrobody
        self.show_name(astrobody)
        diameter = astrobody.radius.to('earth_radius').m * 2

        if system.letter == 'S':
            star = system.primary
            stellar_tides = minor_tides(diameter, star.mass.m, astrobody.orbit.a.m)
        else:
            combined_mass = sum([star.mass.m for star in system])
            stellar_tides = minor_tides(diameter, combined_mass, astrobody.orbit.a.m)

        planet_tides = 0
        if astrobody.celestial_type == 'planet':
            lunar_tides = 0
            if astrobody.rogue or astrobody.parent.celestial_type == 'star':
                primary = 'moon'
                for satellite in astrobody.satellites:
                    if satellite.celestial_type == 'satellite':
                        lunar_tides += major_tides(diameter, satellite.mass.m, satellite.orbit.a.to('earth_diameter').m)
            elif astrobody.orbit.subtype == 'PlanetaryBinary':
                if astrobody is astrobody.parent.primary:
                    other = astrobody.parent.secondary
                else:
                    other = astrobody.parent.primary
                primary = other
                diameter = other.radius.to('earth_radius').m * 2
                planet_tides = major_tides(diameter, astrobody.mass.m, other.orbit.a.to('earth_diameter').m)
            else:
                primary = astrobody.parent
                lunar_tides += major_tides(diameter, astrobody.parent.mass.m, astrobody.orbit.a.to('earth_diameter').m)
        else:
            primary = 'planet'
            lunar_tides = major_tides(diameter, astrobody.orbit.star.mass.m, astrobody.orbit.a.to('earth_diameter').m)

        # if stellar_tides > lunar_tides:
        #     primary = 'star'
        if astrobody.rogue:
            primary = 'rogue'
        std_high = abs(q((planet_tides + lunar_tides) * 0.54, 'm'))
        std_low = -std_high if std_high.m != 0 else abs(std_high)

        spring_high = abs(q((planet_tides + lunar_tides + stellar_tides) * 0.54, 'm'))  # meters
        spring_low = -spring_high if spring_high.m != 0 else abs(spring_high)

        neap_high = abs(q((planet_tides + lunar_tides - stellar_tides) * 0.54, 'm'))  # meters
        neap_low = -neap_high if neap_high.m != 0 else abs(neap_high)

        title = f'Tides on {str(astrobody)}:'
        tides = [
            {'name': '\nStandard high', 'value': std_high},
            {'name': '\nStandard low', 'value': std_low},
            {'name': '\n\nSpring high', 'value': spring_high},
            {'name': '\nSpring low', 'value': spring_low},
            {'name': '\n\nNeap high', 'value': neap_high},
            {'name': '\nNeap low', 'value': neap_low}
        ]
        texts = []
        for tide in tides:
            name = tide['name']
            v = tide['value']
            if 'e' in str(v.m):
                valor = f"{v.m:.2e} "
                unidad = f"{v.u:P~}"
                formato = valor + unidad
            else:
                formato = f'{v:.2~P}'

            texts.append(f'{name}: {formato}')

        tides_text = ''.join(texts)

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
            text = f'{str(self.current)} is a rogue {astrobody.celestial_type}.'
        elif is_tidally_locked(lunar_tides + planet_tides, system.age.m / 10 ** 9, mass):
            text = f'{str(self.current)} is tidally locked to {primary}.'
            self.current.rotation = 'Tidally locked'
            self.current.spin = 'Locked'
        elif is_tidally_locked(stellar_tides, system.age.m / 10 ** 9, mass):
            text = f'{str(self.current)} is tidally locked to {primary}.'
            self.current.rotation = 'Tidally locked'
            self.current.spin = 'Locked'
        else:
            text = f'{str(self.current)} is not tidally locked.'

        self.text_render = Surface((ANCHO - 200, 230))
        self.text_render.fill(COLOR_BOX)
        render1 = self.write3(title, self.f2, self.perceptions_rect.w, j=1)
        render2 = self.write3(tides_text, self.f1, self.perceptions_rect.w)
        render3 = self.write3(text, self.f2, self.perceptions_rect.w)

        r = self.text_render.blit(render1, (0, 3))
        r = self.text_render.blit(render2, (3, r.bottom))
        self.text_render.blit(render3, (3, r.bottom+15))

        # how other bodies are seen from this planet
        system = Universe.current_planetary()
        visibility = Universe.aparent_brightness[astrobody.id]
        sizes = Universe.relative_sizes[astrobody.id]
        distances = Universe.distances[astrobody.id]
        text_lines = []
        analyzed = []
        for idx, body_id in enumerate(visibility):
            body_visibility = visibility[body_id]
            body = Universe.get_astrobody_by(body_id, tag_type='id', silenty=True)
            if body is False:
                for sys in Universe.nei().systems():
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

            if astrobody.habitable:
                if astrobody.orbit.subtype == 'PlanetaryBinary':
                    inner, outer = self.check_apsis(astrobody.parent)
                else:
                    inner, outer = self.check_apsis(astrobody)
                if (inner and not outer) or (outer and not inner) or (not inner and not outer):
                    text += f" While {astrobody} is itself habitable, its orbit's "
                    if not inner:
                        text += "periapsis falls behind the star's inner habitable zone"
                    if not outer:
                        text += " and its apoapsis goes beyond the star's outer habitable zone"

                    text += '. This makes it uninhabitable.'

            text_lines.append(text)
        final_text = '\n'.join(text_lines)
        self.exportable_text = final_text
        self.render = self.write3(final_text, self.f1, 380)
        if self.render_rect is None:
            self.render_rect = self.render.get_rect(topleft=[3, 244])

        self.render.set_clip(Rect(3, 250, 380, 346))
        self.print_button.enable()
        self.render_everything()

    def render_everything(self):
        self.image.fill(COLOR_BOX)
        self.image.blit(self.render, self.render_rect)
        self.image.fill(COLOR_BOX, (0, 0, ANCHO, 32))
        self.image.blit(self.text_render, (3, 18))

    @staticmethod
    def check_apsis(astrobody):
        star_system = astrobody.find_topmost_parent()
        inner = astrobody.orbit.periapsis.to('au') >= star_system.habitable_inner.to('au')
        outer = astrobody.orbit.apoapsis.to('au') <= star_system.habitable_outer.to('au')
        return inner, outer

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class Astrobody(ColoredBody):

    def on_mousebuttondown(self, event):
        if event.origin == self:
            self.parent.select_one(self)
            self.parent.parent.show_selected(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = Astrobody

    def show(self):
        systems = Universe.nei().systems()
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
                for line in self.parent.exportable_text.splitlines(keepends=True):
                    file.write(line)
            self.disable()

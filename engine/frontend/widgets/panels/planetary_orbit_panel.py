from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, COLOR_AREA, COLOR_SELECTED, COLOR_TEXTO, Group
from .common import ColoredBody, ListedArea, ModifyArea, TextButton, ToggleableButton
from engine.equations.orbit import PseudoOrbit, RawOrbit, from_planetary_resonance
from engine.frontend.widgets.incremental_value import IncrementalValue
from engine.frontend.widgets.basewidget import BaseWidget
from .stellar_orbit_panel import OrbitType, RatioDigit
from engine.frontend.globales import WidgetHandler
from engine.backend import EventHandler, q, roll
from engine.frontend.widgets.meta import Meta
from engine.equations.space import Universe
from pygame import Surface, Rect
from itertools import cycle


class PlanetaryOrbitPanel(BaseWidget):
    skippable = True
    skip = False
    current = None
    markers = None
    satellites = None

    curr_digit = 0
    selected_marker = None

    added = None
    visible_markers = True

    show_swap_system_button = True

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'Planetary Orbit'
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = Group()
        self.buttons = Group()
        self.orbit_descriptions = Group()
        self._markers = {}
        self.markers = []
        self.added = []
        self.objects = []
        self.satellites = {}
        text = "Here you can link your natural satellites to your planets."
        text += "\n\nClick first on the parent body on the right and then,"
        text += " click on the satellite you want to link at the bottom."
        text += "\n\n A random orbit will apear for it. Click on the orbit to start modifiying it."
        f = self.crear_fuente(14)
        self.erase_text_area = self.write2(text, f, fg=COLOR_AREA, width=300, centerx=200, y=100, j=1)
        self.area_buttons = self.image.fill(COLOR_AREA, [0, 420, self.rect.w, 200])
        self.area_markers = Rect(3, 58, 380, 20 * 16)
        self.curr_x = self.area_buttons.x + 3
        self.curr_y = self.area_buttons.y + 21
        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.add_orbits_button = SetOrbitButton(self, ANCHO - 94, 394)
        self.area_modify = ModifyArea(self, ANCHO - 201, 374)
        self.show_markers_button = ToggleSatellitesButton(self, 'Satellites', None, 3, 421)
        self.show_markers_button.disable()
        self.resonances_button = AddResonanceButton(self, ANCHO - 150, 416)
        self.order_f = self.crear_fuente(14)
        self.digit_x = RatioDigit(self, 'x', self.resonances_button.rect.left - 55, self.resonances_button.rect.y)
        self.write(':', self.crear_fuente(16), topleft=[self.digit_x.rect.right + 1, self.resonances_button.rect.y - 1])
        self.digit_y = RatioDigit(self, 'y', self.digit_x.rect.right + 9, self.resonances_button.rect.y)
        self.ratios = [self.digit_x, self.digit_y]
        self.cycler = cycle(self.ratios)
        next(self.cycler)

        self.properties.add(self.area_modify, self.show_markers_button, self.digit_x, self.digit_y,
                            self.planet_area, self.add_orbits_button, self.resonances_button,
                            layer=2)

        EventHandler.register(self.save_orbits, 'Save')
        EventHandler.register(self.hold_loaded_bodies, 'LoadPlanetary Orbits')
        EventHandler.register(self.export_data, 'ExportData')
        self.held_data = {}

    def hold_loaded_bodies(self, event):
        if 'Planetary Orbits' in event.data and len(event.data['Planetary Orbits']):
            self.held_data.update(event.data['Planetary Orbits'])

    def load_orbits(self):
        bodies = []
        for idx in self.held_data:
            system_id = self.held_data[idx]['star_id']
            system = Universe.get_astrobody_by(system_id, tag_type='id').parent.parent.planetary
            bodies.append(system.get_astrobody_by(idx, tag_type='id'))

        bodies.sort(key=lambda b: b.mass, reverse=True)
        # sorting by mass may not be the best way to sort, but it is unlikely that a body orbits another body if the
        # parent body is less massive than the child one.
        for body in bodies:
            if body.id in self.held_data:
                orbit_data = self.held_data[body.id]
                a = q(orbit_data['a'], 'earth_radius')
                e = q(orbit_data['e'])
                i = q(orbit_data['i'], 'degree')
                loan = q(orbit_data.get('LoAN', 0), 'degree')
                aop = orbit_data['AoP']
                if aop != 'undefined':
                    aop = q(aop, 'degree')

                system = Universe.get_astrobody_by(orbit_data['star_id'], tag_type='id')
                if system is not None:
                    system = system.parent.parent.planetary
                    planet = system.get_astrobody_by(body.id, tag_type='id')
                    if planet.id not in self.satellites:
                        self.satellites[planet.id] = []

                    if planet.id not in self._markers:
                        self._markers[planet.id] = []
                    satellite = system.get_astrobody_by(orbit_data['astrobody'], tag_type='id')
                    self.satellites[planet.id].append(satellite)
                    satellite.set_orbit(planet, [a, e, i, loan, aop])
                    self.add_existing(satellite, planet)
        else:
            self.show_markers_button.enable()

        self.held_data.clear()

    def save_orbits(self, event):
        orbits = {}
        for planet_obj in self.planet_area.listed_objects.widgets():
            planet = planet_obj.object_data
            for marker in self._markers.get(planet.id, []):
                if marker.orbit is not None:
                    d = self.create_save_data(marker.orbit)
                    orbits[planet.id] = d

        EventHandler.trigger(event.tipo + 'Data', 'Orbit', {'Planetary Orbits': orbits})

    @staticmethod
    def create_save_data(orb):
        d = {}
        if hasattr(orb, 'semi_major_axis'):
            d['a'] = orb.semi_major_axis.m
        if hasattr(orb, 'inclination'):
            d['i'] = orb.inclination.m
        if hasattr(orb, 'eccentricity'):
            d['e'] = orb.eccentricity.m
        if hasattr(orb, 'astrobody'):
            d['astrobody'] = orb.astrobody.id
            d['star_id'] = orb.astrobody.parent.id
        if hasattr(orb, 'longitude_of_the_ascending_node'):
            d['LoAN'] = orb.longitude_of_the_ascending_node.m
        if hasattr(orb, 'argument_of_periapsis'):
            aop = orb.argument_of_periapsis
            d['AoP'] = aop.m if hasattr(aop, 'm') else aop
        d['flagged'] = orb.flagged
        return d

    def hide_orbit_types(self):
        for orbit_type in self.orbit_descriptions.widgets():
            orbit_type.hide()
        for orbit_button in self.buttons.widgets():
            orbit_button.enable()

    def populate(self):
        planet = self.current
        names = []
        for marker in self.markers:
            names.append(marker.name)
            if marker not in self.properties.widgets():
                self.properties.add(marker, layer=3)
            marker.show()

        if "Hill Sphere" not in names:
            self.create_hill_marker(planet)

    def add_objects(self):
        if Universe.current_galaxy is not None:
            system = Universe.current_planetary()
            if system is not None:
                self.image.fill(COLOR_BOX, [0, 32, self.rect.w, 380])
                planets = [p for p in system.planets if p.relative_size != 'Giant']
                for obj in system.satellites + system.asteroids + planets:
                    btn = ObjectButton(self, obj)
                    if btn not in self.buttons:
                        if obj not in self.objects:
                            self.objects.append(obj)

                        if obj.orbit is not None and obj.orbit.star.celestial_type == 'planet':
                            markers = self._markers[obj.orbit.star.id]
                            marker_idx = [i for i in range(len(markers)) if markers[i].obj == obj][0]
                            marker = markers[marker_idx]
                            btn.link_marker(marker)
                            btn.update_text(obj.orbit.a)

                        if btn is not None and (obj.orbit is None or btn.completed):
                            self.buttons.add(btn, layer=system.id)
                            self.properties.add(btn, layer=4)

                bodies = self.buttons.get_widgets_from_layer(system.id)
                self.sort_buttons(bodies)

    def show(self):
        super().show()
        self.load_orbits()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.show()
        self.add_objects()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def select_planet(self, planet, force=False):
        if planet is not self.current or force:
            if force:
                self.planet_area.select_by_data(planet)
            self.hide_everything()
            self.set_current(planet)
            self.populate()
            if planet.id not in self.satellites:
                self.satellites[planet.id] = []
        for button in self.buttons.widgets():
            button.enable()
            button.deselect()

        self.visible_markers = True
        sats = self.satellites[planet.id]
        names = [marker.name for marker in self.markers]
        densest = sorted(sats, key=lambda i: i.density.to('earth_density').m, reverse=True)
        if len(densest) and "Roche's Limit" not in names:
            self.create_roches_marker(densest[0])
        self.add_orbits_button.disable()
        self.sort_markers()

    def set_current(self, planet):
        self.current = planet
        if planet.id not in self._markers:
            self._markers[planet.id] = []
        self.markers = self._markers[planet.id]

    def select_one(self, button):
        for bttn in self.buttons.widgets():
            bttn.deselect()
        button.select()

    def anchor_maker(self, marker):
        self.deselect_markers(marker)
        self.area_modify.link(marker)
        self.area_modify.visible_markers = True
        self.add_orbits_button.link(marker)
        self.add_orbits_button.enable()
        self.selected_marker = marker

    def deselect_markers(self, m):
        for marker in self.markers:
            marker.deselect()
            marker.enable()
        m.select()

    def sort_markers(self):
        self.markers.sort(key=lambda m: m.value.m)
        for i, marker in enumerate(self.markers, start=1):
            marker.rect.y = i * 2 * 10 + 38
            if not self.area_markers.contains(marker.rect):
                marker.hide()
            else:
                marker.show()

    def create_roches_marker(self, obj):
        obj_density = obj.density.to('earth_density').m
        roches = self.current.set_roche(obj_density)
        roches_marker = Marker(self, "Roche's Limit", roches, lock=True)
        marker = None
        for m in self.markers:
            if m.name == "Roche's Limit":
                self.properties.remove(m)
                marker = m
                break

        if marker is not None:
            idx = self.markers.index(marker)
            self.markers[idx] = roches_marker
        else:
            self.markers.append(roches_marker)
        self.properties.add(roches_marker, layer=3)
        self.replace_ring()

        return roches

    def create_hill_marker(self, planet):
        x = Marker(self, 'Hill Sphere', planet.hill_sphere)
        x.locked = True
        last = None if not len(self.markers) else self.markers[-1]
        if last is not None and last.name == 'Hill Sphere':
            self.properties.remove(last)
            self.markers[-1] = x
        else:
            self.markers.append(x)
        self.properties.add(x, layer=3)

    def create_ring_markers(self, ring):
        self.add_orbits_button.disable()
        x = Marker(self, "Ring's inner edge", ring.inner.to('earth_radius'), lock=True)
        y = Marker(self, "Ring's outer edge", ring.outer.to('earth_radius'), lock=True)
        for z in [x, y]:
            self.markers.append(z)
            self.properties.add(z, layer=3)

    def replace_ring(self):
        ring_makers = [marker for marker in self.markers if 'Ring' in marker.name]
        if len(ring_makers):
            new_ring = self.current.ring.recreate()
            for marker in ring_makers:
                self.markers.remove(marker)
                self.properties.remove(marker)
            self.create_ring_markers(new_ring)

    def on_button_press(self, body):
        self.hide_everything()
        self.current = body.parent
        self.planet_area.select_by_data(body.parent)
        self.show_markers_button.enable()

    def add_new(self, obj):
        if obj not in self.added:
            self.added.append(obj)
        if hasattr(obj, 'cls'):
            cls = obj.cls
        else:
            cls = obj.clase
        obj_name = '{} #{}'.format(cls, obj.idx)
        pln_habitable = Universe.current_planetary().is_habitable(self.current)
        pln_hill = self.current.hill_sphere.m
        obj_type = obj.celestial_type

        text = "A satellite's mass must be less than or equal to the\nmass of its host."
        text += '\n\nConsider using a less massive satellite for this host.'
        if self.current.mass.to('earth_mass').m < obj.mass.to('earth_mass').m:
            self.added.remove(obj)
            raise AssertionError(text)

        roches = self.create_roches_marker(obj)
        pos = q(round(roll(self.current.roches_limit.m, self.current.hill_sphere.m / 2), 3), 'earth_radius')
        orbit = RawOrbit(Universe.current_planetary().parent.star, pos)
        obj_marker = Marker(self, obj_name, pos, color=COLOR_SELECTED, lock=False)

        max_value = pln_hill
        if pln_habitable and obj_type != 'asteroid':
            max_value /= 2
        obj_marker.set_max_value(max_value)
        obj_marker.set_min_value(roches.m)
        obj_marker.links(orbit, obj)

        self.markers.append(obj_marker)
        self.properties.add(obj_marker, layer=3)
        self.sort_markers()

        return orbit, obj_marker

    def add_existing(self, obj, planet):
        if obj not in self.added:
            self.added.append(obj)
        if hasattr(obj, 'cls'):
            cls = obj.cls
        else:
            cls = obj.clase
        obj_name = '{} #{}'.format(cls, obj.idx)
        orbit = obj.orbit
        pos = orbit.a
        obj_marker = Marker(self, obj_name, pos, color=COLOR_SELECTED, lock=False)
        obj_marker.links(orbit, obj)
        obj_density = obj.density.to('earth_density').m
        roches = planet.set_roche(obj_density)
        min_value = roches.m
        max_value = planet.hill_sphere.m
        if hasattr(planet, 'habitable') and planet.habitable and obj.celestial_type != 'asteroid':
            max_value /= 2
        obj_marker.set_max_value(max_value)
        obj_marker.set_min_value(min_value)
        self._markers[planet.id].append(obj_marker)

    def remove_marker(self, marker):
        self.markers.remove(marker)
        marker.linked_button.kill()
        marker.unlink()
        marker.kill()
        bodies = self.buttons.get_widgets_from_layer(self.current.orbit.star.id)
        self.sort_buttons(bodies)

    def hide_markers(self):
        for marker in self.markers:
            marker.hide()

        if len(self.markers):
            self.show_markers_button.enable()

    def hide_everything(self):
        for marker in self.markers:
            if marker.linked_button is not None:
                marker.linked_button.hide_info()
            marker.hide()
        self.visible_markers = False
        self.show_markers_button.disable()
        self.hide_orbit_types()

    def is_added(self, obj):
        return obj in self.added

    def get_raw_orbit_markers(self):
        raws = [m for m in self.markers if ((not m.locked) and (type(m.orbit) is RawOrbit))]
        return raws

    def link_satellite_to_planet(self, marker):
        marker._orbit = PseudoOrbit(marker.orbit)
        button = marker.linked_button
        self.hide_everything()
        button.update_text(marker.orbit.a)
        button.info.link_marker(marker)
        button.info.locked = False
        button.info.show()

    def notify(self):
        if not self.visible_markers:
            self.show_markers_button.enable()
            for button in self.buttons.widgets():
                button.disable()

    def set_current_digit(self, idx):
        self.curr_digit = self.ratios.index(idx)

    def cycle(self):
        has_values = False
        for ratio in self.ratios:
            ratio.deselect()
            has_values = ratio.value != ''

        valid = has_values and self.selected_marker is not None

        if valid:
            self.resonances_button.enable()
        else:
            ratio = next(self.cycler)
            ratio.select()
            WidgetHandler.set_origin(ratio)

    def ratios_to_string(self):
        x = int(self.digit_x.value)
        y = int(self.digit_y.value)
        diff = y - x if y > x else x - y
        self.write('{}° Order'.format(diff), self.order_f, right=self.digit_x.rect.left - 2, y=self.digit_x.rect.y)
        return '{}:{}'.format(x, y)

    def get_difference(self):
        x = int(self.digit_x.value)
        y = int(self.digit_y.value)
        return x - y

    def clear_ratios(self):
        self.digit_x.clear()
        self.digit_y.clear()

    def export_data(self, event):
        if event.data['panel'] is self:
            pass


class OrbitableObject(ColoredBody):
    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self and self.enabled:
            self.parent.parent.hide_orbit_types()
            self.parent.select_one(self)
            self.parent.parent.select_planet(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = OrbitableObject

    def show(self):
        current = Universe.nei()
        if current is not None:
            for system in current.get_p_systems():
                idx = system.id
                bodies = [body for body in system.astro_bodies if body.hill_sphere is not None]
                self.populate(bodies, layer=idx)
        super().show()

    def delete_objects(self, astronomical_object):
        super().delete_objects(astronomical_object)
        self.show()

    def on_mousebuttondown(self, event):
        pass

    def select_by_data(self, data):
        for obj in self.listed_objects.widgets():
            if obj.object_data == data:
                self.select_one(obj)
                break


class ObjectButton(ColoredBody):
    info = None
    linked_marker = None
    completed = False

    def __init__(self, parent, obj):
        self.orbit_data = None
        super().__init__(parent, obj, str(obj), 0, 0)
        self.img_dis = self.img_uns

    def update_text(self, orbit):
        self.completed = True
        self.enable()
        if self.object_data.has_name:
            name = self.object_data.name
        else:
            name = str(self.object_data)
        obj: str = name + ' @{:~}'.format(orbit)
        self.img_uns = self.f1.render(obj, True, self._color, COLOR_AREA)
        self.img_sel = self.f2.render(obj, True, self._color, COLOR_AREA)
        self.img_dis = self.img_uns
        self.max_w = self.img_sel.get_width()
        self.image = self.img_uns
        self.rect.size = self.image.get_size()
        if self.info is None:
            self.info = OrbitType(self.parent)
            self.info.link_astrobody(self.object_data)
            self.info.link_button(self)
            self.parent.orbit_descriptions.add(self.info)

    def on_mousebuttondown(self, event):
        if self.enabled and event.origin == self:
            self.parent.select_one(self)
            if not self.parent.is_added(self.object_data) and self.parent.current is not None:
                orbit, marker = self.parent.add_new(self.object_data)
                self.parent.buttons.change_layer(self, self.parent.current.id)
                self.create_type(orbit)
                self.link_marker(marker)
                self.disable()
            else:
                self.parent.on_button_press(self.object_data)
                if self.linked_marker != self.info.linked_marker:
                    self.info.link_marker(self.linked_marker)
                self.info.show()

    def move(self, x, y):
        self.rect.topleft = x, y

    def create_type(self, info):
        self.orbit_data = PseudoOrbit(info)

    def link_marker(self, marker):
        self.linked_marker = marker
        marker.linked_button = self

    def hide_info(self):
        if self.info is not None:
            self.info.hide()

    def hide(self):
        super().hide()
        self.hide_info()


class Marker(Meta, IncrementalValue):
    locked = True
    enabled = True
    text = ''
    color = COLOR_TEXTO
    max_value = None
    min_value = None

    _orbit = None
    obj = None

    linked_button = None

    warned = False

    def __init__(self, parent, name, value, color=None, lock=True):
        super().__init__(parent)
        self.f1 = self.crear_fuente(16)
        self.f2 = self.crear_fuente(16, bold=True)
        self.name = name
        self._value = value
        self.unit = value.u

        if not lock:
            self.locked = False
            self.color = color
        self.update()
        self.image = self.img_uns
        self.rect = self.image.get_rect(x=3)

    def set_max_value(self, value):
        self.max_value = value

    def set_min_value(self, value):
        self.min_value = value

    @property
    def orbit(self):
        return self._orbit

    @orbit.setter
    def orbit(self, orbit):
        self._orbit = orbit
        self.parent.notify()

    @property
    def value(self):
        if self.orbit is not None:
            return round(self._orbit.semi_major_axis, 3)
        else:
            return self._value

    @value.setter
    def value(self, new_value):
        if self._orbit is not None:
            self._orbit.semi_major_axis = new_value

    def force_selection(self):
        if not self.locked:
            self.parent.anchor_maker(self)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and event.origin == self:
            self.force_selection()
            EventHandler.trigger('SetOrigin', self, {'origin': self})

    def tune_value(self, delta):
        if not self.locked:
            self.increment = self.update_increment()
            self.increment *= delta
            ta = 'Regular satellites must orbit close to their planet, that is within half of the maximun value.'
            ta += '\n\nTry moving the satellite to a lower orbit.'

            tb = "A satellite cannot orbit beyond it's main body's Hill Sphere."
            tc = "A satellite cannot orbit below it's main body's Roche's limit."
            td = f"If the asteroid {str(self.obj)} passes trough the planet's Roche's limit, it will be turned into" \
                 f" a ring.\n\nYou have been warned."
            test_a = self.value.m + self.increment > self.min_value
            test_b = self.value.m + self.increment < self.max_value
            test_c = self.it_may_be_a_ring(self.obj)
            if self.obj.celestial_type == 'satellite':
                assert test_b, ta
            assert test_b, tb
            if not test_a:
                if not test_c:
                    raise AssertionError(tc)
                elif not self.warned:
                    self.warned = True
                    raise AssertionError(td)
                else:
                    name = str(self.obj)
                    ring = self.parent.current.set_ring(self.obj)
                    Universe.current_planetary().remove_astro_obj(self.obj)
                    self.parent.create_ring_markers(ring)
                    self.parent.remove_marker(self)
                    self.parent.sort_markers()
                    raise AssertionError(f'The asteroid {name} has been turned into a ring')

            self.value += q(self.increment, self.value.u)
            self.linked_button.update_text(self.value)
            self.increment = 0
            self.parent.sort_markers()

    def it_may_be_a_ring(self, obj):
        it_may = obj.celestial_type == 'asteroid'
        if self.parent.current.orbit.a.m < Universe.current_planetary().parent.frost_line.m:
            it_may = it_may and obj.comp != 'Icy'
        else:
            it_may = it_may and obj.comp == 'Icy'

        return it_may

    def set_value(self, new_value):
        self.value = q(new_value.m, self.value.u)
        self.parent.sort_markers()

    def update(self):
        self.reset_power()
        self.text = '{:~}'.format(round(self.value, 3))
        self.img_sel = self.f2.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        self.img_uns = self.f1.render(self.name + ' @ ' + self.text, True, self.color, COLOR_BOX)
        super().update()
        if self.selected:
            self.image = self.img_sel

    def links(self, orbit, obj):
        self.orbit = orbit
        self.obj = obj

    def unlink(self):
        self.orbit = None
        self.obj = None

    def __repr__(self):
        return self.name + ' Marker'

    def show(self):
        super().show()


class SetOrbitButton(TextButton):
    linked_marker = None

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set Orbit', x, y)
        self.disable()

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.link_satellite_to_planet(self.linked_marker)

    def link(self, marker):
        self.linked_marker = marker


class AddResonanceButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Set to Resonance', x, y)

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            assert self.parent.selected_marker.obj is not None, "The orbit is empty."
            satellite = self.parent.selected_marker.obj
            planet = self.parent.current
            position = from_planetary_resonance(planet, satellite, self.parent.ratios_to_string())
            difference = self.parent.get_difference()
            selected = None
            for sat in self.parent.get_raw_orbit_markers():
                if difference > 0:  # 3:2
                    if sat.value > satellite.orbit.a:
                        selected = sat
                        break
                elif difference < 0:  # 2:3
                    if sat.value < satellite.orbit.a:
                        selected = sat
                        break
            selected.value = round(position, 3)
            selected.force_selection()
            self.disable()
            self.parent.clear_ratios()

    def enable(self):
        super().enable()
        self.parent.image.fill(COLOR_BOX, [325, 396, 63, 18])


class ToggleSatellitesButton(ToggleableButton):
    def on_mousebuttondown(self, event):
        if event.origin == self:
            if self.parent.current is not None:
                self.parent.select_planet(self.parent.current, force=True)

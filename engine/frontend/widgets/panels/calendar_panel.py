from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetHandler
from engine.frontend.widgets import BaseWidget, ValueText, Meta
from .common import ListedArea, ColoredBody, TextButton, RadioButton
from engine.backend.eventhandler import EventHandler
from engine.equations import Universe, SolarCalendar
from pygame.sprite import LayeredUpdates
from pygame import Surface, mouse, draw


class CalendarPanel(BaseWidget):
    skippable = True
    _skip = False

    locked = False

    show_swap_system_button = True

    calendar: SolarCalendar = None  # this is just an alias
    held_data = None

    first_week_day: int = 0

    def __init__(self, parent):
        self.name = 'Calendar'
        super().__init__(parent)
        self.properties = LayeredUpdates()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.fuente = self.crear_fuente(12)
        self.rect = self.image.get_rect()

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)

        self.add_text = ValueText(self, 'Add', 390, 480, size=12)
        self.add_text.modifiable = True
        self.add_text.hide()

        r = self.add_text.rect
        self.month_text = ValueText(self, 'days to month', r.right + 20, r.y, size=12)
        self.month_text.modifiable = True
        self.month_text.hide()
        self.properties.add(self.planet_area, layer=1)
        self.properties.add(self.add_text, self.month_text, layer=2)

        self.lunisolar = LunisolarCalendarButton(self, ANCHO - 13, ALTO - 32)
        self.lunar = LunarCalendarButton(self, *self.lunisolar.rect.topright)
        self.solar = SolarCalendarButton(self, *self.lunar.rect.topright)
        self.properties.add(self.solar, self.lunar, self.lunisolar, layer=1)

        self.arrow_r = ArrowR(self, ANCHO - 218, 32)
        self.arrow_l = ArrowL(self, 3, 32)
        self.properties.add(self.arrow_r, self.arrow_l, layer=6)

        self.intercalary = RadioButton(self, r.x + 6, r.bottom + 8)
        rect = self.intercalary.rect
        self.where = ValueText(self, " as intercalary, before", rect.right, rect.top - 1, size=12)
        self.where.modifiable = True
        self.properties.add(self.intercalary, self.where, layer=2)

        self.held_data = {}
        EventHandler.register(self.save_days, 'Save')
        EventHandler.register(self.hold_loaded_data, "LoadCalendars")

    @property
    def skip(self):
        return self._skip

    @skip.setter
    def skip(self, value):
        self._skip = value

    def select_astrobody(self, planet):
        densest = sorted(planet.satellites, key=lambda i: i.density.to('earth_density').m, reverse=True)
        satellite = densest[0]

        self.properties.remove_sprites_of_layer(3)
        self.properties.remove_sprites_of_layer(4)

        if satellite.title == 'Major':
            calendar = SolarCalendar(planet, satellite)
            planet.set_calendar(calendar)
            self.calendar = planet.calendar
            if planet.id in self.held_data:
                for month_key in self.held_data[planet.id]:
                    self.calendar.months[int(month_key)]["leap"] += self.held_data[planet.id][month_key]
                    self.calendar.days_remaining -= self.held_data[planet.id][month_key]

        w = self.calendar.week_days
        m = self.calendar.month_days
        r = self.calendar.days_remaining
        l = self.calendar.year_leap
        a = self.calendar.year_local

        x = self.planet_area.rect.x
        y = self.planet_area.rect.bottom + 2
        width = self.planet_area.rect.width

        t = (f'{self.calendar.month_local} months of {m} days.'
             f'\n4 {w}-day long weeks per month.'
             f'\n{a} days per year.'
             f'\nleap years every {l} years.')

        self.write2(t, self.fuente, width=width, y=y, x=x)
        self.show_calendar()

        if r > 0:
            self.write_remaining_text()

    def show_year_title(self, week_day):
        title_sprite = YearTitle(self, week_day, 0, 32)
        self.properties.add(title_sprite, layer=5)
        title_sprite.show()

    def show_calendar(self):
        for month in self.properties.get_sprites_from_layer(3):
            month.hide()

        week_day = self.first_week_day
        self.show_year_title(week_day)

        for widget in self.properties.get_sprites_from_layer(6):
            widget.show()

        for mi in self.calendar.months.keys():
            dx = 120 * (mi % 3) + 16
            dy = (100 * (mi // 3)) + 70
            month = MonthSprite(self, mi, week_day, self.calendar.week_days, dx, dy)
            week_day = month.last_week_day + 1
            self.properties.add(month, layer=3)
            month.show()

    def switch_first_day(self, delta):
        for sprite in self.properties.get_sprites_from_layer(5):
            sprite.kill()

        if 0 <= self.first_week_day + delta < self.calendar.week_days:
            self.first_week_day += delta
            self.show_year_title(self.first_week_day)
            for month in self.properties.get_sprites_from_layer(3):
                month.move_days(self.first_week_day)

    def select_one(self, radio):
        if radio is self.intercalary:
            radio.select()
            self.where.show()
            self.where.enable()
            self.where.editable = True
            self.where.select()
            self.where.text_area.enable()
            EventHandler.trigger('DeselectOthers', self.where, {})
            EventHandler.trigger('SetOrigin', self.where, {'origin': self.where.text_area})

    def write_remaining_text(self, recreate=False):
        self.image.fill(COLOR_BOX, [390, 464, 200, 32])
        self.locked = False
        remaining_text = f'Distribute {self.calendar.days_remaining} missing days'
        self.write2(remaining_text, self.fuente, width=200, x=390, y=464)

        if not recreate:
            for wg in self.properties.get_sprites_from_layer(2):
                wg.show()
                wg.enable()

    def add_remaning_days(self):
        widgets = self.properties.get_sprites_from_layer(2)
        wid_day, wid_month, wid_inter, wid_where = widgets
        val_day = wid_day.value
        val_month = wid_month.value
        val_inter = wid_inter.on
        val_where = wid_where.value

        value_day, value_month = None, None
        if val_day != '':
            value_day = int(val_day)
        if val_month != '':
            value_month = int(val_month)

        if value_day is not None and value_month is not None:
            month_index = value_month - 1
            months = self.properties.get_sprites_from_layer(3)
            if month_index > len(months) - 1:
                month = None
            else:
                month = months[month_index]

            if self.calendar.days_remaining - value_day >= 0:
                self.calendar.days_remaining -= value_day
                if month is not None:
                    if val_inter is True:
                        self.calendar.months[month_index]["intercalary"].append(int(val_where))
                        wid_inter.deselect()
                        wid_where.value = ''
                    else:
                        self.calendar.months[month_index]["leap"] += value_day
                else:
                    self.calendar.special_monthless_period += value_day
                wid_month.value = ''
                wid_day.value = ''

            if self.calendar.days_remaining == 0:
                self.image.fill(COLOR_BOX, [390, 464, 200, 32])
                wid_month.hide()
                wid_day.hide()
                wid_where.hide()
                wid_inter.hide()
            else:
                self.write_remaining_text()

            if month is not None:
                month.recreate()

            elif month is None:
                y = self.properties.remove_sprites_of_layer(3)[-1].rect.y + 8
                special = SpecialMonthlessPeriod(self, value_day, 290, y)
                self.properties.add(special, layer=3)
                special.show()

            elif value_month is None:
                WidgetHandler.origin = wid_month.text_area

    def show(self):
        super().show()
        for prop in self.properties.get_sprites_from_layer(1):
            prop.show()

    def hide(self):
        self.image.fill(COLOR_BOX)
        super().hide()
        for prop in self.properties.sprites():
            prop.hide()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            delta = 0
            if event.data['button'] == 4:
                delta = -1
            elif event.data['button'] == 5:
                delta = +1
            elif event.data['button'] == 1:
                if self.intercalary.on:
                    self.intercalary.deselect()

            for prop in self.properties.get_sprites_from_layer(3):
                prop.move(0, delta)

    @staticmethod
    def save_days(event):
        data = {}
        for nei in Universe.current_galaxy.stellar_neighbourhoods:
            for system in nei.get_p_systems():
                for planet in [planet for planet in system.planets if planet.calendar is not None]:
                    months = planet.calendar.months
                    leaps = {m: months[m]['leap'] for m in months if months[m]['leap'] > 0}
                    data[planet.id] = leaps

        EventHandler.trigger(event.tipo + 'Data', 'Calendar', {"Calendars": data})

    def hold_loaded_data(self, event):
        if 'Calendars' in event.data and len(event.data['Calendars']):
            self.held_data.update(event.data['Calendars'])


class CalendablePlanets(ColoredBody):
    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.parent.select_astrobody(self.object_data)


class AvailablePlanets(ListedArea):
    listed_type = CalendablePlanets
    name = 'Astrobodies'

    def show(self):
        current = Universe.nei()
        if current is not None:
            for system in current.get_p_systems():
                idx = system.id
                population = [i for i in system.planets if len(i.satellites) > 0]
                self.populate(population, layer=idx)
        super().show()


class DaySprite(BaseWidget):
    enabled = True
    moveable = False
    month_id = None

    def __init__(self, parent, idx, day_month, week_day, size, remaining=False, weekday=False):
        super().__init__(parent)
        self.size = size
        self.image = Surface((self.size, self.size))
        rect = self.image.get_rect()

        indice = None
        if remaining:
            self.image.fill('red')
            self.moveable = remaining
        elif weekday:
            self.image.fill('blue')
            indice = idx
        elif type(idx) is int:
            indice = idx
        else:
            self.image.fill('green')

        self.rect = self.image.get_rect()
        self.number = indice
        if indice is not None:
            f = self.crear_fuente(8)
            render = f.render(str(idx + 1), 1, 'white')
            render_rect = render.get_rect(center=rect.center)
            self.image.blit(render, render_rect)
        self.day_month = day_month
        self.week_day = week_day

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.has_mouse_over = True
            mouse.set_pos(self.rect.center)

    def on_mousebuttonup(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.has_mouse_over = False

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def __repr__(self):
        return f"Day #{self.day_month} of {str(self.parent)}"


class MonthSprite(BaseWidget):
    image, rect = None, None
    day_g = None

    last_week_day = 0

    def __init__(self, parent, idx, first_week_day, week_lenght, dx, dy):
        super().__init__(parent)
        self.number = idx + 1
        self.week = week_lenght
        self.day_g = []

        self.create_title(dx, dy)
        self.first_day = first_week_day if first_week_day < week_lenght else 0
        if idx >= 0:
            self.create_normal_days()

    def create_normal_days(self):
        common = self.parent.calendar.months[self.number - 1]['common']
        leap = self.parent.calendar.months[self.number - 1]['leap']
        self.last_week_day = self.create_days(common, leap, self.rect)

    def create_title(self, x, y):
        self.image = self.write3(f"Month #{self.number}", self.crear_fuente(14), self.week * 12, j=1)
        self.rect = self.image.get_rect(topleft=(x, y - 8))

    def create_days(self, common, leap, rect, intecalary=None):
        dx = rect.x
        dy = rect.y + rect.h
        days = [i for i in range(common + leap)]
        if intecalary is not None:
            for inter in intecalary:
                days.insert(inter - 1, str(inter))
        for i, weekday in enumerate([i for i in range(self.week)]):
            day = DaySprite(self, weekday, weekday % len(days), i % self.week, 11, weekday=True)
            day.month_id = self.number
            x = dx + (i % self.week) * (day.size + 1)
            y = dy + (i // self.week) * (day.size + 1)
            day.rect.topleft = (x, y)
            day.show()
            self.parent.properties.add(day, layer=4)

        dy += 11
        for i, day_i in enumerate(days, start=self.first_day):
            day = DaySprite(self, day_i, int(day_i) % len(days), i % self.week, 11, remaining=False)
            day.month_id = self.number
            x = dx + (i % self.week) * (day.size + 1)
            y = dy + (i // self.week) * (day.size + 1)

            day.rect.topleft = (x, y)
            day.show()
            self.parent.properties.add(day, layer=4)
            self.day_g.append(day)

        else:
            return self.day_g[-1].week_day

    def recreate(self):
        for day in self.day_g:
            day.hide()
            day.kill()

        self.day_g.clear()
        common = self.parent.calendar.months[self.number - 1]['common']
        leap = self.parent.calendar.months[self.number - 1]['leap']
        intercalary = self.parent.calendar.months[self.number - 1]['intercalary']
        self.create_days(common, leap, self.rect, intercalary)

    def move_days(self, delta):
        dx = self.rect.x
        dy = self.rect.bottom + 11
        for i, day in enumerate(self.day_g, start=self.first_day + delta):
            x = dx + (i % self.week) * (day.size + 1)
            y = dy + (i // self.week) * (day.size + 1)

            day.rect.topleft = (x, y)

    def show(self):
        super().show()
        for day in self.day_g:
            day.show()

    def hide(self):
        super().hide()
        for day in self.day_g:
            day.hide()

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def __repr__(self):
        return f"Month #{self.number}"


class YearTitle(BaseWidget):
    def __init__(self, parent, week_day, x, y):
        super().__init__(parent)
        t = f'Common Year starting on Day #{str(week_day + 1)}'
        self.image = self.write3(t, self.crear_fuente(14, bold=True), ANCHO - 200, j=1)
        self.rect = self.image.get_rect(topleft=(x, y))

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)


class SpecialMonthlessPeriod(MonthSprite):
    def __init__(self, parent, days, dx, dy):
        super().__init__(parent, -1, 0, days, dx, dy)
        rect = self.rect.copy()
        rect.centerx = self.rect.centerx
        rect.y += 10
        self.create_days(0, days, rect)

    def create_title(self, x, y):
        f = self.crear_fuente(12)
        self.image = self.write3("Special Monthless Period", f, f.size(" Monthless ")[0], j=1)
        self.rect = self.image.get_rect(topleft=(x, y - 8))


class SolarCalendarButton(TextButton):
    enabled = True

    def __init__(self, parent, x, y):
        super().__init__(parent, 'Solar Calendar', x, y, )
        self.rect.right = x


class LunarCalendarButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Lunar Calendar', x, y, )
        self.rect.right = x


class LunisolarCalendarButton(TextButton):
    def __init__(self, parent, x, y):
        super().__init__(parent, 'Lunisolar Calendar', x, y)
        self.rect.right = x


class BaseArrow(Meta):
    enabled = True
    delta = 0

    def __init__(self, parent, x, y, points):
        super().__init__(parent)
        self.layer = 50

        self.img_uns = self.crear((0, 0, 0), points)
        self.img_sel = self.crear((255, 255, 255), points)
        self.image = self.img_uns
        self.rect = self.image.get_rect(topleft=(x, y))

    @staticmethod
    def crear(color, points):
        imagen = Surface((16, 16))
        rect = imagen.get_rect()
        imagen.fill(COLOR_BOX)
        draw.polygon(imagen, color, [
            getattr(rect, points[0]),
            getattr(rect, points[1]),
            getattr(rect, points[2])
        ])
        return imagen

    def on_mousebuttondown(self, event):
        if event.data['button'] == 1 and self.enabled and event.origin == self:
            self.parent.switch_first_day(self.delta)


class ArrowR(BaseArrow):
    delta = 1

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, ['topleft', 'midright', 'bottomleft'])


class ArrowL(BaseArrow):
    delta = -1

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y, ['topright', 'midleft', 'bottomright'])

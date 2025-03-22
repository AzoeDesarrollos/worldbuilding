from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group, WidgetHandler
from engine.frontend.widgets import BaseWidget, ValueText
from engine.backend.eventhandler import EventHandler
from engine.equations import Universe, SolarCalendar
from .common import ListedArea, ColoredBody
from pygame import Surface, mouse


class CalendarPanel(BaseWidget):
    skippable = True
    _skip = False

    locked = False

    show_swap_system_button = True

    calendar: SolarCalendar = None  # this is just an alias
    held_data = None

    def __init__(self, parent):
        self.name = 'Calendar'
        super().__init__(parent)
        self.properties = Group()
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
        if satellite.title == 'Major' and planet.calendar is None:
            calendar = SolarCalendar(planet, satellite)
            planet.set_calendar(calendar)
            self.calendar = planet.calendar
            if planet.id in self.held_data:
                for month_key in self.held_data[planet.id]:
                    self.calendar.months[int(month_key)]["leap"] += self.held_data[planet.id][month_key]
                    self.calendar.days_remaining -= self.held_data[planet.id][month_key]

        w = self.calendar.week_days
        m = self.calendar.month_days
        d = self.calendar.month_local * m  # year length
        r = self.calendar.days_remaining
        l = self.calendar.year_leap
        a = self.calendar.year_local

        x = self.planet_area.rect.x
        y = self.planet_area.rect.bottom + 2
        width = self.planet_area.rect.width

        t = (f'{self.calendar.month_local} months of {m} days.'
             f'\n4 {w}-day long weeks per month.'
             f'\n{d} days in in a common year.'
             f'\n{a} days in in a leap year.'
             f'\n\nleap years every {l} years.')

        self.write2(t, self.fuente, width=width, y=y, x=x)

        title_sprite = YearTitle(self, 200, 32)
        self.properties.add(title_sprite, layer=5)
        title_sprite.show()
        for mi in self.calendar.months.keys():
            dx = 150 * (mi % 2) + 16
            dy = (75 * (mi // 2)) + 32
            month = MonthSprite(self, mi, w, d, dx, dy)
            self.properties.add(month, layer=3)
            month.show()

        if r > 0:
            self.write_remaining_text()

    def write_remaining_text(self, recreate=False):
        self.image.fill(COLOR_BOX, [390, 464, 200, 32])
        self.locked = False
        remaining_text = f'Distribute {self.calendar.days_remaining} leap years days'
        self.write2(remaining_text, self.fuente, width=200, x=390, y=464)

        if recreate is False:
            for wg in self.properties.get_widgets_from_layer(2):
                wg.show()
                wg.enable()

    def add_remaning_days(self):
        widgets = self.properties.get_widgets_from_layer(2)
        wid_day, wid_month = widgets
        val_day = wid_day.value
        val_month = wid_month.value

        value_day, value_month = None, None
        if val_day != '':
            value_day = int(val_day)
        if val_month != '':
            value_month = int(val_month)

        if value_day is not None and value_month is not None:
            month_index = value_month - 1
            month = self.properties.get_widgets_from_layer(3)[month_index]
            if self.calendar.days_remaining - value_day >= 0:
                self.calendar.days_remaining -= value_day
                self.calendar.months[month_index]["leap"] += value_day
                wid_month.value = ''
                wid_day.value = ''

            if self.calendar.days_remaining == 0:
                self.image.fill(COLOR_BOX, [390, 464, 200, 32])
                wid_month.hide()
                wid_day.hide()
            else:
                self.write_remaining_text()

            month.recreate()
        elif value_month is None:
            WidgetHandler.origin = wid_month.text_area

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(1):
            prop.show()

    def hide(self):
        self.image.fill(COLOR_BOX)
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            delta = 0
            if event.data['button'] == 4:
                delta = -1
            elif event.data['button'] == 5:
                delta = +1

            for prop in self.properties.get_widgets_from_layer(3):
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

    def __init__(self, parent, idx, day_month, size, remaining=False):
        super().__init__(parent)
        self.size = size
        self.image = Surface((self.size, self.size))
        if remaining:
            self.image.fill('red')
            self.moveable = remaining
        self.rect = self.image.get_rect()
        self.number = idx
        self.day_month = day_month

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

    def __init__(self, parent, idx, week_lenght, year_lenght, dx, dy):
        super().__init__(parent)
        self.number = idx + 1
        self.year = year_lenght
        self.week = week_lenght
        self.day_g = []

        self.x, self.y = dx, dy
        x, y = 0 + dx, 32 + dy
        self.create_title(x, y)
        self.create_days()

    def create_title(self, x, y):
        title = self.write3(f"Month #{self.number}", self.crear_fuente(14), self.week * 12, j=1)
        self.image = Surface((self.week * 12, (8 * 9) - 2))
        self.image.fill(COLOR_BOX)
        self.image.blit(title, (0, 0))
        self.rect = self.image.get_rect(topleft=(x, y - 8))

    def create_days(self):
        x = 0 + self.x
        y = 32 + self.y
        common = self.parent.calendar.months[self.number - 1]['common']
        leap = self.parent.calendar.months[self.number - 1]['leap']
        days = common + leap
        for i in range(days):
            day = DaySprite(self, i + 1, i % days, 11, i >= common)
            day.month_id = self.number
            x += day.size + 1
            if i % self.week == 0:
                y += day.size + 1
                x = self.x

            elif i % days == 0:
                y += day.size + 20
                x = 50 + self.x

            day.move(x, y)
            day.show()
            self.parent.properties.add(day, layer=4)
            self.day_g.append(day)

    def recreate(self):
        for day in self.day_g:
            day.kill()
        self.day_g.clear()

        self.create_days()

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
    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = self.write3("The Year", self.crear_fuente(16, bold=True), ANCHO // 3)
        self.rect = self.image.get_rect(top=y)
        self.rect.centerx = x

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

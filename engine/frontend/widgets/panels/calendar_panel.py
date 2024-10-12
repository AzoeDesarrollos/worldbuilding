from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group
from engine.frontend.widgets import BaseWidget
from pygame import Surface, mouse
from pygame.sprite import spritecollide, collide_rect
from .common import ListedArea, ColoredBody
from engine.equations import Universe, SolarCalendar


class CalendarPanel(BaseWidget):
    skippable = True
    _skip = False

    locked = False

    show_swap_system_button = True

    def __init__(self, parent):
        self.name = 'Calendar'
        super().__init__(parent)
        self.properties = Group()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

        self.planet_area = AvailablePlanets(self, ANCHO - 200, 32, 200, 340)
        self.days = Group()

        self.properties.add(self.planet_area, layer=1)

    @property
    def skip(self):
        return self._skip

    @skip.setter
    def skip(self, value):
        self._skip = value

    def select_astrobody(self, planet):
        densest = sorted(planet.satellites, key=lambda i: i.density.to('earth_density').m, reverse=True)
        satellite = densest[0]
        if satellite.title == 'Major':
            s_caledar = SolarCalendar(planet, satellite)
            w = s_caledar.week_days
            m = s_caledar.month_days
            d = s_caledar.month_local * m
            r = s_caledar.days_remaining
            l = s_caledar.year_leap

            x = self.planet_area.rect.x
            y = self.planet_area.rect.bottom + 2
            width = self.planet_area.rect.width

            t = (f'{s_caledar.month_local} months of {m} days.'
                 f'\n4 {w}-day long weeks per month.'
                 f'\n{d} days in in a common year.'
                 f'\n{d + r} days in in a leap year.'
                 f'\n\nleap years every {l} years.')

            self.write2(t, self.crear_fuente(12), width=width, y=y, x=x)

            title_sprite = YearTitle(self, 200, 32)
            self.properties.add(title_sprite, layer=2)
            title_sprite.show()
            for mi in range(s_caledar.month_local):
                dx = 150 * (mi % 2) + 16
                dy = (75 * (mi // 2)) + 32
                month = MonthSprite(self, mi, w, m, d, dx, dy)
                self.properties.add(month, layer=2)
                month.show()
            # y = dy
            # for dr in range(r):
            #     day = DaySprite(self, d + dr + 1, None, 11, True)
            #     self.properties.add(day, layer=2)
            #     day.show()
            #     # y += 200
            #     # x = 100
            #     day.move(210, 540)

    def show(self):
        super().show()
        for prop in self.properties.get_widgets_from_layer(1):
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.get_widgets_from_layer(1):
            prop.hide()
        for prop in self.properties.get_widgets_from_layer(2):
            prop.hide()

    def on_mousebuttondown(self, event):
        if event.origin == self:
            delta = 0
            if event.data['button'] == 4:
                delta = -1
            elif event.data['button'] == 5:
                delta = +1
            elif event.data['button'] == 1:
                print(event.data)

            for prop in self.properties.get_widgets_from_layer(2):
                prop.move(0, delta)


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
        # if self.day_month is not None:
        #     text = f"of Month #{str(self.month_id)}"
        # else:
        #     text = ''
        return f"Day "


class MonthSprite(BaseWidget):
    def __init__(self, parent, idx, week_lenght, days_n, year_lenght, dx, dy):
        super().__init__(parent)
        self.number = idx + 1
        x, y = 0 + dx, 32 + dy
        title = self.write3(f"Month #{idx + 1}", self.crear_fuente(14), 100)
        self.image = Surface((week_lenght * 12, (8 * 9) - 2))
        self.image.fill(COLOR_BOX)
        self.image.blit(title, (0, 0))
        self.rect = self.image.get_rect(topleft=(x, y - 8))
        for i in range(days_n):
            day = DaySprite(self, i + 1, i % days_n, 11, i >= year_lenght)
            day.month_id = idx + 1
            x += day.size + 1
            if i % week_lenght == 0:
                y += day.size + 1
                x = dx

            elif i % days_n == 0:
                y += day.size + 20
                x = 50 + dx

            day.move(x, y)
            day.show()
            self.parent.days.add(day)
            self.parent.properties.add(day, layer=2)

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)


class YearTitle(BaseWidget):
    def __init__(self, parent, x, y):
        super().__init__(parent)
        self.image = self.write3("The Year", self.crear_fuente(16, bold=True), ANCHO // 3)
        self.rect = self.image.get_rect(top=y)
        self.rect.centerx = x

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

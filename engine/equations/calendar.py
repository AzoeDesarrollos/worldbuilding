from math import trunc
from engine.backend.util import q


class Calendar:
    months = None
    days_remaining = None
    calendar_type = None


class SolarCalendar(Calendar):
    special_monthless_period = 0

    calendar_type = 'Solar'

    def __init__(self, planet, moon):
        planet_period = planet.orbit.period.to('earth_day').m
        month_year = planet_period / moon.orbit.period.to('earth_day').m

        self.year_local = trunc(planet_period)
        day_local, year_leap = get_day_local(planet_period, self.year_local)

        self.day_local = q(day_local, 'hour')
        planet.rotation = q(day_local, 'hour/day')
        # remaining_time = q(round(day_local - trunc(day_local), 4), 'hour').to('second')
        self.year_leap = year_leap

        self.month_local = trunc(month_year)

        self.days_month = self.year_local / self.month_local
        self.month_days = trunc(self.days_month)
        c, i = "common", 'intercalary'
        self.months = {month_n: {c: self.month_days, i: []} for month_n in range(self.month_local)}
        days_year = self.month_local * self.month_days
        self.days_remaining = self.year_local - days_year

        self.week_days = int(self.month_days / 4)
        self.weeks_year = int(days_year / self.week_days)
        self.short_week = int(self.year_local - self.weeks_year * self.week_days)

    @property
    def hour_local(self):
        return self.day_local / 24


class LunarCalendar(Calendar):
    calendar_type = 'Lunar'

    def __init__(self, planet, moon):
        planet_period = planet.orbit.period.to('earth_day').m
        moon_period = moon.orbit.period.to('earth_day').m

        self.week_days = round(moon_period / 4)
        self.month_days = trunc(moon_period)
        self.month_local = round(planet_period / moon_period)
        self.year_local = trunc(planet_period)
        self.days_year = self.month_local * self.month_days
        self.days_remaining = self.year_local - self.days_year
        day_local, year_leap, = get_day_local(planet_period, self.year_local)
        self.leap_month = year_leap * self.month_local

        self.day_local = q(day_local, 'hour')
        planet.rotation = q(day_local, 'hour/day')

        c, i = "common", 'intercalary'
        self.months = {month_n: {c: self.month_days, i: []} for month_n in range(self.month_local)}

        self.weeks_year = int(self.days_year / self.week_days)
        self.short_week = int(self.year_local - self.weeks_year * self.week_days)


class LunisolarCalendar(Calendar):
    pass


def get_day_local(planet_period, year_local):
    year_leap, day_local = 0, 0
    while trunc(day_local) != 24:
        year_leap += 1
        day_local = round((planet_period / (year_local + (1 / year_leap)) * 24), 4)

    return day_local, year_leap
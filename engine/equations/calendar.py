from math import trunc


class SolarCalendar:
    def __init__(self, planet, moon):
        planet_period = planet.orbit.period.to('earth_day').m
        month_year = planet_period / moon.orbit.period.to('earth_day').m

        self.year_local = trunc(planet_period)
        year_leap, day_local = 0, 0
        while trunc(day_local) != 24:
            year_leap += 1
            day_local = round((planet_period / (self.year_local + (1 / year_leap if year_leap > 0 else 1)) * 24), 4)

        self.day_local = day_local
        self.year_leap = year_leap

        self.month_local = trunc(month_year)

        self.days_month = self.year_local / self.month_local
        self.month_days = trunc(self.days_month)
        days_year = self.month_local * self.month_days
        self.days_remaining = self.year_local - days_year

        self.week_days = int(self.month_days / 4)
        self.weeks_year = int(days_year / self.week_days)
        self.short_week = int(self.year_local - self.weeks_year * self.week_days)

    @property
    def hour_local(self):
        return self.day_local / 24

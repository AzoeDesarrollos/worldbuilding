class IncrementalValue:
    ticks = 0
    potencia = 0
    clicks = 0
    increment = 0

    def update_increment(self):
        self.ticks = 0
        if self.clicks == 10:
            self.potencia += 1
            if self.potencia > 3:
                self.potencia = 3
            self.clicks = 2
        else:
            self.clicks += 1

        return round((0.001 * (pow(10, self.potencia))), 4)

    def reset_power(self):
        self.ticks += 1
        if self.ticks >= 30:
            self.clicks = 0
            self.increment = 0
            self.potencia = 0

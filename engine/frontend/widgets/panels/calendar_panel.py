from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, Group
from engine.frontend.widgets import BaseWidget
from pygame import Surface


class CalendarPanel(BaseWidget):
    skippable = True
    skip = False

    locked = False

    show_swap_system_button = True

    def __init__(self, parent):
        self.name = 'Calendar'
        super().__init__(parent)
        self.properties = Group()
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()

    def show(self):
        super().show()
        print(self.name)

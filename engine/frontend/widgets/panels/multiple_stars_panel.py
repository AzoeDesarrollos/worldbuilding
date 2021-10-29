from engine.frontend.globales import ANCHO, ALTO, COLOR_BOX, WidgetGroup
from engine.backend.eventhandler import EventHandler
from .star_system_panel import SystemType
from ..basewidget import BaseWidget
from pygame import Surface


class MultipleStarsPanel(BaseWidget):
    skippable = True
    skip = False

    def __init__(self, parent):
        self.name = 'Multiple Stars'
        super().__init__(parent)
        self.image = Surface((ANCHO, ALTO - 32))
        self.image.fill(COLOR_BOX)
        self.rect = self.image.get_rect()
        self.properties = WidgetGroup()

        f1 = self.crear_fuente(16, underline=True)
        self.write(self.name + ' Panel', f1, centerx=(ANCHO // 4) * 1.5, y=0)

        self.current = SystemsType(self)
        self.properties.add(self.current)

    def show(self):
        super().show()
        for prop in self.properties.widgets():
            prop.show()

    def hide(self):
        super().hide()
        for prop in self.properties.widgets():
            prop.hide()


class SystemsType(SystemType):
    def __init__(self, parent):
        super().__init__(parent)
        self.properties = WidgetGroup()
        props = [
            'Primary System', 'Secondary System', 'Average Separation',
            'Eccentriciy (primary)', 'Eccentricty (secondary)', 'Barycenter',
            'Maximun Separation', 'Minimun Separation', 'System Name']
        self.create(props)
        EventHandler.register(self.clear, 'ClearData')

from pygame.sprite import LayeredUpdates
from .widgethandler import WidgetHandler
from .renderer import Renderer


class WidgetGroup(LayeredUpdates):
    """Wrapper para evitar inspeccciones incorrectas de PyCharm"""
    def get_widgets_from_layer(self, layer: int):
        return super().get_sprites_from_layer(layer)

    def widgets(self):
        return super().sprites()

    def remove(self, *sprites) -> None:
        super().remove(*sprites)
        for sp in sprites:
            Renderer.del_widget(sp)
            WidgetHandler.del_widget(sp)

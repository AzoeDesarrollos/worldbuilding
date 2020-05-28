from pygame.sprite import LayeredUpdates


class WidgetGroup(LayeredUpdates):
    """Wrapper para evitar inspeccciones incorrectas de PyCharm"""
    def get_widgets_from_layer(self, layer: int):
        return super().get_sprites_from_layer(layer)

    def widgets(self):
        return super().sprites()

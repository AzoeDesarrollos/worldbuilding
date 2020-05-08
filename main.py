from engine.frontend.globales import WidgetHandler, Renderer
from engine.backend.eventhandler import EventHandler

while True:
    EventHandler.process()
    WidgetHandler.update()
    Renderer.update()

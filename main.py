from engine.frontend.globales import WidgetHandler, Renderer
from engine.backend.eventhandler import EventHandler

while True:
    try:
        EventHandler.process()
        WidgetHandler.update()
        Renderer.update()
    except AssertionError as error:
        print(error)

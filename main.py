from engine.frontend.globales import WidgetHandler, Renderer
from engine.frontend.widgets.message import PopUpMessage
from engine.backend.eventhandler import EventHandler

while True:
    try:
        EventHandler.process()
        WidgetHandler.update()
        Renderer.update()
    except AssertionError as error:
        assertion = PopUpMessage(str(error))
        WidgetHandler.lock_and_set(assertion)

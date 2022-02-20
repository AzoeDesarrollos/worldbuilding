from engine.backend.eventhandler import EventHandler
from .background import Background


def trigger_view():
    EventHandler.trigger('SwitchMode', 'Background', {"mode": 2})
    EventHandler.process()


def reset_view(event):
    if event.origin == 'engine':
        EventHandler.trigger('SwitchMode', 'Background', {"mode": 1})


EventHandler.register(reset_view, 'Fin')

__all__ = [
    'trigger_view',
    'Background'
]

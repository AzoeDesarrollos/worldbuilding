# from engine import Renderer, WidgetHandler, EventHandler
# from engine.frontend.widgets.star_group_button import StarGroupButton
# from engine.equations import Galaxy
#
# g = Galaxy()
#
# for i, key in enumerate('OBAFGKM'):
#     cant = len(g[key])
#     spr = StarGroupButton(key, 32, 32 + i * 64, cant)
#
# while True:
#     EventHandler.process()
#     WidgetHandler.update()
#     Renderer.update()
#
# # from engine.equations.planet import planet_temperature
# #
# # # print(planet_temperature(1.02,1.05,28.5))
from engine.equations.satellite import create_moon
#
# data = {
#     'density': 4,
#     'a': 80,
#     'b': 50,
#     'c': 30
# }

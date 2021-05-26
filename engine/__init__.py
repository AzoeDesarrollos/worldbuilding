from pint import UnitRegistry
from os import getcwd, path
from .backend import *
from decimal import getcontext, Decimal

if path.exists(path.join(getcwd(), "lib")):
    ruta = path.join(getcwd(), 'lib', 'engine')
else:
    ruta = path.join(getcwd(), 'engine')

ureg = UnitRegistry()
ureg.load_definitions(path.join(ruta, 'unit_definitions.txt'))
q = ureg.Quantity

material_densities = abrir_json(path.join(ruta, 'material_densities.json'))
molecular_weight = abrir_json(path.join(ruta, 'molecular_weight.json'))
recomendation = abrir_json(path.join(ruta, 'recomendation.json'))

context = getcontext()
decimal_context = context
d = Decimal

from pint import UnitRegistry
from .frontend import *
from .backend import *

ureg = UnitRegistry()
ureg.load_definitions('engine/unit_definitions.txt')
q = ureg.Quantity

material_densities = abrir_json('engine/material_densities.json')

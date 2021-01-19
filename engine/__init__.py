from pint import UnitRegistry
from .backend import *

ureg = UnitRegistry()
ureg.load_definitions('engine/unit_definitions.txt')
q = ureg.Quantity

material_densities = abrir_json('engine/material_densities.json')
molecular_weight = abrir_json('engine/molecular_weight.json')
recomendation = abrir_json('engine/recomendation.json')

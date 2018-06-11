from pint import UnitRegistry

ureg = UnitRegistry()
ureg.load_definitions('engine/unit_definitions.txt')
q = ureg.Quantity

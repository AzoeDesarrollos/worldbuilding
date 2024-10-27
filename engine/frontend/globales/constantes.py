from pygame import Color

# tamaño de la ventana
ALTO = 630
ANCHO = 590

NUEVA_LINEA = 30

# Colores de fondo y texto plano
COLOR_FONDO = Color(10, 10, 10)
COLOR_TEXTO = Color(0, 0, 0)
COLOR_BOX = Color(125, 125, 125)
COLOR_AREA = Color(200, 200, 200)
COLOR_DARK_AREA = Color([160] * 3)
COLOR_DISABLED = Color(150, 150, 150)
COLOR_SELECTED = Color(255, 255, 255)
COLOR_WARNING = Color(230, 155, 0)

# Colores de cuerpos celestes
COLOR_TERRESTIAL = Color([65] * 3)
COLOR_GASGIANT = Color(199, 149, 25)
COLOR_PUFFYGIANT = Color(178, 64, 141)
COLOR_GASDWARF = Color(85, 89, 37)
COLOR_DWARFPLANET = Color(34, 112, 179)
COLOR_HABITABLE = Color(0, 105, 59)

COLOR_ROCKYMOON = Color(119, 67, 29)
COLOR_ICYMOON = Color(100, 100, 200)
COLOR_IRONMOON = Color(33, 126, 63)

# Colores para las órbitas
COLOR_STARORBIT = Color(111, 115, 47)
COLOR_RESONANT = Color(255, 125, 125)

# Colores para las PieCharts
COLOR_SILICATES = Color([155, 80, 0])
COLOR_IRON = Color([155] * 3)
COLOR_WATER_ICE = Color([0, 200, 255])

# Colores para las PieCharts de Albedo
COLOR_THICK_CLOUDS = Color([75] * 3)
COLOR_THIN_CLOUDS = Color([190] * 3)
COLOR_OPEN_OCEAN = Color([0, 50, 255])
COLOR_SEA_ICE = COLOR_WATER_ICE
COLOR_URBAN = COLOR_DISABLED
COLOR_DESERT = Color([255, 255, 0])
COLOR_GRASSLAND = Color([0, 205, 70])
COLOR_INLAND_WATER_BODIES = Color([0, 100, 255])
COLOR_SNOW_AND_ICE = COLOR_WATER_ICE
COLOR_FOREST = COLOR_HABITABLE

color_areas = [COLOR_DESERT, COLOR_FOREST, COLOR_GRASSLAND, COLOR_INLAND_WATER_BODIES, COLOR_OPEN_OCEAN, COLOR_SEA_ICE,
               COLOR_SNOW_AND_ICE, COLOR_THICK_CLOUDS, COLOR_THIN_CLOUDS, COLOR_URBAN]

__all__ = [
    # Tamaño de la ventana
    'ALTO',
    'ANCHO',

    'NUEVA_LINEA',

    # Colores de fondo
    'COLOR_BOX',
    'COLOR_AREA',
    'COLOR_FONDO',
    'COLOR_DARK_AREA',

    # Colores de texto
    'COLOR_TEXTO',
    'COLOR_SELECTED',
    'COLOR_DISABLED',
    'COLOR_WARNING',

    # Colores para los botones de planetas
    'COLOR_DWARFPLANET',
    'COLOR_TERRESTIAL',
    'COLOR_GASGIANT',
    'COLOR_PUFFYGIANT',
    'COLOR_GASDWARF',
    'COLOR_HABITABLE',

    # Colores para los botones de los satélites
    'COLOR_ICYMOON',
    'COLOR_ROCKYMOON',
    'COLOR_IRONMOON',

    # Color de las órbitas
    'COLOR_STARORBIT',
    'COLOR_RESONANT',

    # Colores de las PieCharts
    'COLOR_IRON',
    'COLOR_SILICATES',
    'COLOR_WATER_ICE',

    'COLOR_THICK_CLOUDS',
    'COLOR_THIN_CLOUDS',
    'COLOR_OPEN_OCEAN',
    'COLOR_SEA_ICE',
    'COLOR_URBAN',
    'COLOR_DESERT',
    'COLOR_GRASSLAND',
    'COLOR_INLAND_WATER_BODIES',
    'COLOR_SNOW_AND_ICE',
    'COLOR_FOREST',
    'color_areas'

]

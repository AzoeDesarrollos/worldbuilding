from pygame import Color

# tamaño de la ventana
ALTO = 630
ANCHO = 590

# Colores de fondo y texto plano
COLOR_FONDO = Color(10, 10, 10)
COLOR_TEXTO = Color(0, 0, 0)
COLOR_BOX = Color(125, 125, 125)
COLOR_AREA = Color(200, 200, 200)
COLOR_DISABLED = Color(150, 150, 150)
COLOR_SELECTED = Color(255, 255, 255)

# Colores de cuerpos celestes
COLOR_TERRESTIAL = Color(59, 82, 154)
COLOR_GASGIANT = Color(199, 149, 25)
COLOR_PUFFYGIANT = Color(178, 64, 141)
COLOR_GASDWARF = Color(85, 89, 37)
COLOR_DWARFPLANET = Color(34, 112, 179)
COLOR_HABITABLE = Color(0, 105, 59)

COLOR_ROCKYMOON = Color(119, 67, 29)
COLOR_ICYMOON = Color(100, 100, 200)
COLOR_IRONMOON = Color(33, 126, 63)

# Colores para las órbitas
COLOR_STARORBIT = 111, 115, 47

color = [155] * 3
COLOR_IRON = Color(color)
COLOR_IRON_DIS = Color(color)
hsla = list(COLOR_IRON.hsla)
hsla[1] = 20
hsla[2] = 70
COLOR_IRON_DIS.hsla = hsla

color = [155, 80, 0]  # silicates
COLOR_SILICATES = Color(color)
COLOR_SILICATES_DIS = Color(color)
hsla = list(COLOR_SILICATES.hsla)
hsla[1] = 20
hsla[2] = 70
COLOR_SILICATES_DIS.hsla = hsla

color = [0, 200, 255]  # water ice
COLOR_WATER_ICE = Color(color)
COLOR_WATER_ICE_DIS = Color(color)
hsla = list(COLOR_WATER_ICE.hsla)
hsla[1] = 20
hsla[2] = 70
COLOR_WATER_ICE_DIS.hsla = hsla

del color, hsla, Color

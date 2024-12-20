from ..common import find_and_interpolate, Linea, Punto, BodyMarker, MarkersManager, density
from pygame import K_UP, K_DOWN, K_RIGHT, K_LEFT, K_SPACE, K_LSHIFT, K_LCTRL, K_ESCAPE
from pygame import init, quit, display, font, event, Rect, Surface, image, mouse
from engine.frontend.globales import COLOR_TEXTO, COLOR_BOX, ANCHO, ALTO, Group
from pygame import KEYDOWN, QUIT, SCALED, MOUSEMOTION, MOUSEBUTTONDOWN, KEYUP
from pygame.sprite import Sprite
from engine.backend import q
from os import getcwd, path
from sys import exit

radius_keys = [1 + i / 100 for i in range(-3, 11)] + [1 + i / 10 for i in range(2, 10)]
mass_keys = [i / 100 for i in range(3, 11)]
mass_keys += [i / 10 for i in range(2, 10)]
mass_keys += [i for i in range(1, 14)]

init()
fuente = font.SysFont('Verdana', 11)
fuente2 = font.SysFont('Verdana', 13)
mass_imgs = [fuente.render(str(mass_keys[i]), True, COLOR_TEXTO, COLOR_BOX) for i in range(len(mass_keys))]
radius_imgs = [fuente.render(str(radius_keys[i]), True, COLOR_TEXTO, COLOR_BOX) for i in range(len(radius_keys))]

if path.exists(path.join(getcwd(), "lib")):
    ruta = path.join(getcwd(), 'lib', 'engine', 'frontend', 'graphs', 'gasgraph', 'gasgraph.png')
else:
    ruta = path.join(getcwd(), 'engine', 'frontend', 'graphs', 'gasgraph', 'gasgraph.png')

img_rect = Rect(31, 16, 540, 570)
img = image.load(ruta)


class Number(Sprite):
    def __init__(self, imagen, **kwargs):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect(**kwargs)


def gasgraph_loop(system, limit_mass=None):
    done = False
    data = {}
    text_mass = 'Mass: N/A'
    text_radius = 'Radius: N/A'
    text_density = 'Density: N/A'

    text_mass_e = ''
    text_radius_e = ''
    text_density_e = ''

    invalid = True

    fondo = display.set_mode((ANCHO, ALTO), SCALED)
    fondo.fill(COLOR_BOX)
    exes, yes = [], []
    numbers = Group()
    for i in [i for i in range(len(radius_keys[:4]))]:
        n = Number(radius_imgs[i], x=i * 28 + 30, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i + 4 for i in range(len(radius_keys[4:14]))]:
        n = Number(radius_imgs[i], x=i * 27 + 26, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i + 14 for i in range(len(radius_keys[14:]))]:
        n = Number(radius_imgs[i], x=i * 22 + 90, y=3)
        numbers.add(n)
        exes.append(n.rect.centerx)

    for i in [i for i in range(len(mass_keys))]:
        n = Number(mass_imgs[i], right=30, centery=i * 20 + 21)
        numbers.add(n)
        yes.append(n.rect.centery)

    x = exes[radius_keys.index(1.02)]
    y = yes[mass_keys.index(2)]

    rect_super = Rect(31, y, x - 3, (img_rect.h / 2) - 60)
    rect_puffy = Rect(x + 28, 16, (img_rect.w / 2) + 100, y - 16)
    rect_giant = Rect(31, 16, x - 3, y - 16)

    if limit_mass is not None:
        lim_y = round(find_and_interpolate(limit_mass, mass_keys, yes))
        lim_rect = Rect(31, lim_y, img_rect.w, img_rect.h - lim_y + img_rect.y)
        lim_img = Surface(lim_rect.size)
        lim_img.set_alpha(150)
    else:
        lim_rect = None
        lim_img = None

    lineas = Group()
    linea_h = Linea(img_rect, img_rect.x, img_rect.centery, img_rect.w, 1, lineas)
    linea_v = Linea(img_rect, img_rect.centerx, img_rect.y, 1, img_rect.h, lineas)
    punto = Punto(img_rect, img_rect.centerx, img_rect.centery, lineas)

    move_x, move_y = True, True

    marcadores = Group()
    markers = MarkersManager.gas_markers(system.id)

    for planet in system.planets:
        if planet.planet_type == 'gaseous':
            mass = planet.mass.m
            radius = planet.radius.m

            x = find_and_interpolate(mass, mass_keys, yes)
            y = find_and_interpolate(radius, radius_keys, exes)
            MarkersManager.set_marker([x, y])

    for x, y in markers:
        marcadores.add(BodyMarker(x, y))

    while not done:
        x, y = mouse.get_pos()
        for e in event.get([KEYDOWN, KEYUP, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION]):
            if (e.type == KEYDOWN and e.key == K_ESCAPE) or e.type == QUIT:
                quit()
                exit()

            elif e.type == MOUSEMOTION:
                px, py = e.pos

                if move_y:
                    linea_h.move_y(py)
                    punto.move_y(py)
                if move_x:
                    linea_v.move_x(px)
                    punto.move_x(px)

                dx, dy = punto.rect.center
                valid = [rect_puffy.collidepoint(dx, dy),
                         rect_giant.collidepoint(dx, dy),
                         rect_super.collidepoint(dx, dy)]
                if lim_rect is not None:
                    off_limit = lim_rect.collidepoint(dx, dy)
                else:
                    off_limit = False

                if img_rect.collidepoint(px, py) and any(valid) and not off_limit:
                    invalid = False
                    mass = round(find_and_interpolate(linea_h.rect.y + 1, yes, mass_keys), 5)
                    radius = round(find_and_interpolate(linea_v.rect.x, exes, radius_keys), 3)
                    clase = 'Puffy Giant' if valid[0] else ''
                    clase = 'Gas Giant' if valid[1] else clase
                    clase = 'Super Jupiter' if valid[2] else clase
                    data.update({'mass': mass, 'radius': radius, 'clase': clase, 'albedo': 42.25})

                    d = round(density(mass, radius), 5)
                    text_mass = 'Mass: {}'.format(mass)
                    text_radius = 'Radius: {}'.format(radius)
                    text_density = 'Density: {}'.format(d)

                    text_mass_e = 'Mass E: {}'.format(round(q(mass, 'jupiter_mass').to('earth_mass').m, 3))
                    text_radius_e = 'Radius E: {}'.format(round(q(radius, 'jupiter_radius').to('earth_radius').m, 3))
                    text_density_e = 'Density E: {}'.format(round(q(d, 'jupiter_density').to('earth_density').m, 3))

                else:
                    data = {}
                    invalid = True
                    text_mass = 'Mass: N/A'
                    text_radius = 'Radius: N/A'
                    text_density = 'Density: N/A'
                    text_mass_e = 'Mass E: N/A'
                    text_radius_e = 'Radius E: N/A'
                    text_density_e = 'Density E: N/A'

            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    done = True

            elif e.type == KEYDOWN and not invalid:
                if e.key == K_SPACE:
                    done = True

                elif e.key == K_LSHIFT:
                    move_x = False

                elif e.key == K_LCTRL:
                    move_y = False

                elif e.key == K_UP:
                    if y - 1 >= img_rect.top:
                        ev = event.Event(MOUSEMOTION, pos=(x, y - 1), buttons=mouse.get_pressed())
                        mouse.set_pos(x, y - 1)
                        event.post(ev)

                elif e.key == K_DOWN:
                    if y + 1 < img_rect.bottom:
                        ev = event.Event(MOUSEMOTION, pos=(x, y + 1), buttons=mouse.get_pressed())
                        mouse.set_pos(x, y + 1)
                        event.post(ev)

                elif e.key == K_RIGHT:
                    if x + 1 < img_rect.right:
                        ev = event.Event(MOUSEMOTION, pos=(x + 1, y), buttons=mouse.get_pressed())
                        mouse.set_pos(x + 1, y)
                        event.post(ev)

                elif e.key == K_LEFT:
                    if x - 1 >= img_rect.left:
                        ev = event.Event(MOUSEMOTION, pos=(x - 1, y), buttons=mouse.get_pressed())
                        mouse.set_pos(x - 1, y)
                        event.post(ev)

            elif e.type == KEYUP:
                if e.key == K_LSHIFT:
                    move_x = True

                elif e.key == K_LCTRL:
                    move_y = True

        render_mass = fuente2.render(text_mass, True, COLOR_TEXTO, COLOR_BOX)
        render_radius = fuente2.render(text_radius, True, COLOR_TEXTO, COLOR_BOX)
        render_density = fuente.render(text_density, True, COLOR_TEXTO, COLOR_BOX)

        fondo.fill(COLOR_BOX)
        m = fondo.blit(render_mass, (3, ALTO - 20))
        r = fondo.blit(render_radius, (150, ALTO - 20))
        d = fondo.blit(render_density, (300, ALTO - 20))

        render_e_mass = fuente2.render(text_mass_e, True, COLOR_TEXTO, COLOR_BOX)
        render_e_radius = fuente2.render(text_radius_e, True, COLOR_TEXTO, COLOR_BOX)
        render_e_density = fuente2.render(text_density_e, True, COLOR_TEXTO, COLOR_BOX)
        r_m = render_e_mass.get_rect(bottomleft=m.topleft)
        r_r = render_e_radius.get_rect(bottomleft=r.topleft)
        r_d = render_e_density.get_rect(bottomleft=d.topleft)

        fondo.blit(render_e_mass, r_m)
        fondo.blit(render_e_radius, r_r)
        fondo.blit(render_e_density, r_d)

        fondo.blit(img, img_rect)
        if limit_mass is not None:
            fondo.blit(lim_img, lim_rect)
        numbers.draw(fondo)
        marcadores.update()
        marcadores.draw(fondo)
        lineas.update()
        lineas.draw(fondo)
        display.update()

    if done and len(data):
        MarkersManager.set_marker(punto.rect.center)

    display.quit()
    return data

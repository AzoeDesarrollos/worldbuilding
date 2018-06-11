from engine.frontend import planet_loop, star_loop, subselector, orbit_loop
from engine.globs.util import guardar_json

opciones = [
    'planet',
    'star',
    'orbit',
    'none'
]

while True:
    p = subselector('Which type of body you want to create?', opciones, 'Type')
    if p.isdigit():
        idx = int(p)
        p = opciones[idx]

    if p == 'planet':
        data = planet_loop()
        guardar_json('worlds/'+data['name']+'.json',data)

    elif p == 'star':
        data = star_loop()
        guardar_json('worlds/'+data['name']+'.json',data)

    elif p == 'orbit':
        data = orbit_loop()
        guardar_json('worlds/'+data['name']+'.json',data)

    elif p == '' or p == 'none':
        break

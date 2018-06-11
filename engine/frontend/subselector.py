
def subselector(intro, opciones, prompt):
    print(intro)
    for i, op in enumerate(opciones):
        print(i, '-', op)

    p = input(prompt+': ')
    if p.isdigit():
        idx = int(p)
        p = opciones[idx]
    return p

def _convert(delta, grupo_a, grupo_b, comparison):
    if delta in grupo_b:
        idx = grupo_b.index(delta)
        return grupo_a[idx]
    else:
        diffs = None
        up = 0
        down = 1
        if comparison == 'gt':
            diffs = [delta > j for j in grupo_b]
        elif comparison == 'lt':
            diffs = [delta < j for j in grupo_b]

        for i, b in enumerate(diffs):
            if b:
                down = i
            else:
                up = i
                break

        d = (grupo_b[down] - delta) / (grupo_b[down] - grupo_b[up])
        e = grupo_a[up] - grupo_a[down]

        return e * d + grupo_a[down]


def pos_to_keys(delta, keys, puntos, comparison):
    return _convert(delta, keys, puntos, comparison)


def keys_to_pos(delta, keys, puntos, comparison):
    return round(_convert(delta, puntos, keys, comparison))
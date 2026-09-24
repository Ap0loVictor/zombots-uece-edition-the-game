def check_grid_collision(x, y, hitbox_w, hitbox_h, offset_x, offset_y, level):
    if level is None:
        return False
    # Espaço para lógica de colisão com a grid real do level
    return False


# bounds = limites do mundo (min_x, min_y, max_x, max_y)
# Cada limite pode ser None, o que representa uma borda ABERTA, ou seja,
# um lado por onde o mundo ainda se estende (ex.: a direita, quando a
# tela avança para a próxima parte do mapa).
def check_bounds_collision(x, y, hitbox_w, hitbox_h, offset_x, offset_y, bounds):
    if bounds is None:
        return False

    min_x, min_y, max_x, max_y = bounds

    # Canto superior esquerdo da hitbox no espaço de mundo
    hx = x + offset_x
    hy = y + offset_y

    if min_x is not None and hx < min_x:
        return True
    if min_y is not None and hy < min_y:
        return True
    if max_x is not None and hx + hitbox_w > max_x:
        return True
    if max_y is not None and hy + hitbox_h > max_y:
        return True

    return False


# aabb = hitbox de colisão
def check_aabb_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)

def check_grid_collision(x, y, hitbox_w, hitbox_h, offset_x, offset_y, level):
    if level is None:
        return False
    # Espaço para lógica de colisão com a grid real do level
    return False


# aabb = hitbox de colisão
def check_aabb_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)

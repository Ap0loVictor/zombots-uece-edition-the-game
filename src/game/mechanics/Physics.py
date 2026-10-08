def check_grid_collision(x, y, hitbox_w, hitbox_h, level):
    if level is None:
        return False
    # Espaço para lógica de colisão com a grid real do level
    return False


# bounds = limites do mundo (min_x, min_y, max_x, max_y)
# Cada limite pode ser None, o que representa uma borda ABERTA, ou seja,
# um lado por onde o mundo ainda se estende (ex.: a direita, quando a
# tela avança para a próxima parte do mapa).

def check_bounds_collision(x, y, hitbox_w, hitbox_h, bounds):
    if bounds is None:
        return False

    min_x, min_y, max_x, max_y = bounds

    # Canto superior esquerdo da hitbox no espaço de mundo

    if min_x is not None and x < min_x:
        return True
    if min_y is not None and y < min_y:
        return True
    if max_x is not None and x + hitbox_w > max_x:
        return True
    if max_y is not None and y + hitbox_h > max_y:
        return True

    return False


# aabb = hitbox de colisão
def check_aabb_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)

def get_world_hitbox(entity, x = None, y=None):
    """
    Retorna a hitbox da entidade em coordenadas do mundo.
    x e y podem ser fornecidos para calcular a hitbox em uma posição candidata.
    """

    if x is None:
        x = entity.x

    if y is None:
        y = entity.y

    if entity.hitbox is None:
        return x, y, entity.width, entity.height

    offset_x, offset_y, width, height = entity.hitbox

    return (x + offset_x), (y + offset_y), width, height

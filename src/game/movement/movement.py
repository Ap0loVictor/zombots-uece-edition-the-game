from src.mechanics.Physics import check_grid_collision, check_bounds_collision, check_aabb_collision

class Movement:
    """
    Classe base para mecânicas de movimentação.
    Encapsula velocidade, direção, estados de movimento e deslocamento por eixos (X e Y)
    com suporte desacoplado para checagens de colisão usando Physics.
    """

    def __init__(self, speed=250.0, direction="down", hitbox_w=14, hitbox_h=14, offset_x=2, offset_y=1):
        self.speed = speed
        self.direction = direction
        self.is_moving = False
        self.was_moving = False

        # Hitbox e offsets para colisões
        self.hitbox_w = hitbox_w
        self.hitbox_h = hitbox_h
        self.offset_x = offset_x
        self.offset_y = offset_y

    def check_collision(self, x, y, level=None, solid_entities=None, bounds=None):
        """
        Hook de colisão que utiliza as funções da física do motor.
        Retorna True se houver colisão, False caso contrário.
        """
        # Checa colisão com o mapa (Grid) // nn funciona ainda
        if check_grid_collision(x, y, self.hitbox_w, self.hitbox_h, self.offset_x, self.offset_y, level):
            return True

        # Checa colisão com as bordas do mundo (paredes da tela)
        if check_bounds_collision(x, y, self.hitbox_w, self.hitbox_h, self.offset_x, self.offset_y, bounds):
            return True

        # Checa colisão com outras entidades (AABB)
        if solid_entities is not None and len(solid_entities) > 0:
            hx, hy = x + self.offset_x, y + self.offset_y
            for entity in solid_entities:
                ex = getattr(entity, 'x', 0)
                ey = getattr(entity, 'y', 0)
                ew = getattr(entity, 'width', 16)
                eh = getattr(entity, 'height', 16)
                if check_aabb_collision(hx, hy, self.hitbox_w, self.hitbox_h, ex, ey, ew, eh):
                    return True
                    
        return False

    def move_axis(self, x, y, dx, dy, level=None, solid_entities=None, bounds=None):
        """
        Aplica deslocamento independente por eixo (X e Y), checando colisões se existirem.
        """
        self.was_moving = self.is_moving
        self.is_moving = False

        # Deslocamento no eixo X
        if dx != 0:
            self.is_moving = True
            new_x = x + dx
            if not self.check_collision(new_x, y, level, solid_entities, bounds):
                x = new_x

        # Deslocamento no eixo Y
        if dy != 0:
            self.is_moving = True
            new_y = y + dy
            if not self.check_collision(x, new_y, level, solid_entities, bounds):
                y = new_y

        return x, y

    def update(self, x, y, dt, *args, **kwargs):
        """
        Método de atualização a ser sobrescrito por especializações.
        """
        return x, y

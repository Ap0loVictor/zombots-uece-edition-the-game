from src.game.mechanics.Physics import check_grid_collision, check_bounds_collision, check_aabb_collision

class Movement:
    """
    Classe base para mecânicas de movimentação.
    Encapsula velocidade, direção, estados de movimento e deslocamento por eixos (X e Y)
    com suporte desacoplado para checagens de colisão usando Physics.
    """

    def __init__(self, speed=250.0, direction="down"):
        self.speed = speed
        self.direction = direction
        self.is_moving = False
        self.was_moving = False

    def check_hitbox(self, entity,x, y):    
        if entity.hitbox is None:
            return x , y, entity.width, entity.height
        
        offset_x, offset_y, width, height = entity.hitbox
        return (x + offset_x), (y + offset_y), width, height
    
    def check_collision(self, entity, x, y, level=None, solid_entities=None, bounds=None):
        """
        Verifica colisões da entidade com o mapa, bordas e
        outras entidades.

        Retorna:
            True  -> colisão com mapa ou borda
            entity -> colisão com outra entidade
            False -> nenhuma colisão
        """
        hx, hy, hw, hh = self.check_hitbox(entity, x, y)

        # Colisão com o mapa
        if check_grid_collision(hx, hy, hw, hh, level):
            return True

        # Checa colisão com as bordas do mundo (paredes da tela)
        if check_bounds_collision(hx, hy, hw, hh, bounds):
            return True
        
        # Checa colisão com outras entidades (AABB)
        if solid_entities is not None:
            for other in solid_entities:

                if other is entity:
                    continue

                ox, oy, ow, oh = self.check_hitbox(other, other.x, other.y)
                
                if check_aabb_collision(hx, hy, hw, hh, ox, oy, ow, oh):
                    return other
                    
        return False

    def move_axis(self, entity, dx, dy, level=None, solid_entities=None, bounds=None):
        """
        Aplica deslocamento independente por eixo (X e Y), checando colisões se existirem.
        """
        self.was_moving = self.is_moving
        self.is_moving = False
        x = entity.x
        y = entity.y

        # Deslocamento no eixo X
        if dx != 0:
            self.is_moving = True
            new_x = x + dx
            if not self.check_collision(entity, new_x, y, level, solid_entities, bounds):
                x = new_x

        # Deslocamento no eixo Y
        if dy != 0:
            self.is_moving = True
            new_y = y + dy
            if not self.check_collision(entity, x, new_y, level, solid_entities, bounds):
                y = new_y

        return x, y

    def update(self, x, y, dt, *args, **kwargs):
        """
        Método de atualização a ser sobrescrito por especializações.
        """
        return x, y

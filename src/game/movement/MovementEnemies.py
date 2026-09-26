from src.game.movement.Movement import Movement

class MovementEnemies(Movement):
    """
        Movimentação controlada pela IA do inimigo.

        O inimigo utiliza a posição de um alvo para determinar
        a direção do deslocamento.
    """

    def __init__(self, speed=100.0, direction="down"):
        super().__init__(speed=speed,direction=direction)

    def update(self, entity, dt, target=None, level=None, solid_entities=None, bounds=None):
        dx = 0
        dy = 0

        if target is not None:
            tx, ty = target
            diff_x = tx - entity.x
            diff_y = ty - entity.y

            if abs(diff_x) > abs(diff_y):
                self.direction = "right" if diff_x > 0 else "left"
            else :
                self.direction = "down" if diff_y > 0 else "up"

            if diff_x != 0:
                dx = self.speed * dt if diff_x > 0 else -self.speed * dt
            if diff_y !=0:
                dy = self.speed * dt if diff_y > 0 else -self.speed * dt

        return self.move_axis(entity, dx, dy, level=level, solid_entities=solid_entities, bounds=bounds)   
        
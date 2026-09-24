from src.game.movement.movement import Movement

class EnemiesMovement(Movement):
    """
    """

    def __init__(self, speed=100.0, direction="down", hitbox_w=16, hitbox_h=48, offset_x=-8, offset_y=-24):
        super().__init__(
            speed=speed,
            direction=direction,
            hitbox_w=hitbox_w,
            hitbox_h=hitbox_h,
            offset_x=offset_x,
            offset_y=offset_y
        )

    def update(self, x, y, dt, target=None, level=None, solid_entities=None, bounds=None):
        dx = 0
        dy = 0

        if target is not None:
            tx, ty = target
            diff_x = tx - x
            diff_y = ty - y

            if abs(diff_x) > abs(diff_y):
                self.direction = "right" if diff_x > 0 else "left"
            else :
                self.direction = "down" if diff_y > 0 else "up"

            if diff_x != 0:
                dx = self.speed * dt if diff_x > 0 else -self.speed * dt
            if diff_y !=0:
                dy = self.speed * dt if diff_y > 0 else -self.speed * dt

        return self.move_axis(x, y , dx, dy, level=level, solid_entities=solid_entities, bounds=bounds)   
        
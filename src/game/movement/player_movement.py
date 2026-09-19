import pygame
from src.game.movement.movement import Movement


class PlayerMovement(Movement):
    """
    Especialização de Movement para o jogador.
    Interpreta as teclas pressionadas pelo usuário e invoca
    a lógica de deslocamento da classe base.
    """

    def __init__(self, speed=250.0, direction="down", hitbox_w=16, hitbox_h=48, offset_x=-8, offset_y=-24):
        super().__init__(
            speed=speed,
            direction=direction,
            hitbox_w=hitbox_w,
            hitbox_h=hitbox_h,
            offset_x=offset_x,
            offset_y=offset_y
        )

    def update(self, x, y, dt, keys, level=None, solid_entities=None):
        was_moving = self.is_moving
        self.is_moving = False
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed * dt
            self.direction = "up"

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed * dt
            self.direction = "down"

        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed * dt
            self.direction = "left"

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed * dt
            self.direction = "right"

        return self.move_axis(x, y, dx, dy, level=level, solid_entities=solid_entities)

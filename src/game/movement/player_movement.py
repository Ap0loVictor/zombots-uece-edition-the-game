import pygame
from src.game.movement.movement import Movement


class PlayerMovement(Movement):
    """
    Especialização de Movement para o jogador.
    Interpreta as teclas pressionadas pelo usuário e invoca
    a lógica de deslocamento da classe base.
    """

    def __init__(self, speed=250.0, direction="down"):
        super().__init__(speed=speed,direction=direction)

    def update(self, entity, dt, keys, level=None, solid_entities=None, bounds=None):
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

        return self.move_axis(entity, dx, dy, level=level, solid_entities=solid_entities, bounds=bounds)

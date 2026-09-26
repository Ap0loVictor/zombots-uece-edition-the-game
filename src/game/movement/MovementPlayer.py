from math import hypot

import pygame
from src.game.movement.Movement import Movement


class MovementPlayer(Movement):
    """
    Especialização de Movement para o jogador.
    Interpreta as teclas pressionadas pelo usuário e invoca
    a lógica de deslocamento da classe base.
    """

    def __init__(self, speed=250.0, direction="down"):
        super().__init__(speed=speed,direction=direction)

    def update(self, entity, dt, keys, level=None, solid_entities=None, bounds=None):
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        up = keys[pygame.K_w] or keys[pygame.K_UP]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]

        #direções opostas se cancela
        dx = int(right) - int(left)
        dy = int(down) - int(up)

        # mantém a orientaçao usada pela mira, priorizando o eixo y
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

        # pra diagonal ter a mesma velocidade dos eixos
        length = hypot(dx, dy)
        if length > 0:
            step = self.speed * dt / length
            dx *= step
            dy *= step

        return self.move_axis(entity, dx, dy, level=level, solid_entities=solid_entities, bounds=bounds)

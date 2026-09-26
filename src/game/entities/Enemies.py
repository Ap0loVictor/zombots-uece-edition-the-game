from src.game.entities.Entity import Entity
from src.game.movement.enemies_movement import EnemiesMovement
from assets.sprites.entities.EnemySprite import get_enemy_sprite
import random


class Enemies(Entity):
    """
    Entidade dos Inimigos.
    Coordena posição, movimentação e sprite.
    Diferente do Player, o inimigo não recebe input do usuário:
    seu movimento é decidido por uma IA interna (ex: perseguir o player).
    """
    
    def __init__(self, start_x, start_y, enemy_type=None, speed=None, sprite=None, movement=None):
            super().__init__(start_x, start_y, health=50, width=16, height=48, hitbox=(-8, -24, 16, 48))

            self.enemy_type = enemy_type if enemy_type is not None else random.choice(["robo", "zumbi"])
            resolved_speed = speed if speed is not None else 100.0

            self.movement = movement if movement is not None else EnemiesMovement(speed=resolved_speed)
            self.sprite = sprite if sprite is not None else get_enemy_sprite(self.enemy_type)


    def update(self, dt, target=None, level=None, solid_entities=None, bounds=None):
          if self.alive:
                self.x, self.y = self.movement.update(
                      self, dt, target=target,
                      level=level, solid_entities=solid_entities, bounds=bounds
                )

    def get_polygons(self):
          return self.sprite.get_world_polygons(self.x, self.y, self.direction)


    def get_position(self):
        return self.x, self.y

    @property
    def direction(self):
        return self.movement.direction

    @property
    def speed(self):
        return self.movement.speed




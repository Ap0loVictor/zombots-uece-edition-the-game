from src.game.entities.Entity import Entity
from assets.sprites.entities.BoxSprite import BoxSprite
import random


class Box(Entity):
    """
    Box entity.
    Can be broken to drop something
    """
    
    def __init__(self, start_x, start_y, sprite=None, damage = 0):
            super().__init__(start_x, start_y, health=1, width=25, height=25, hitbox=(2, 2, 23, 23), damage=damage)
            self.sprite = sprite if sprite is not None else BoxSprite()

    def get_polygons(self):
          return self.sprite.get_world_polygons(self.x, self.y)

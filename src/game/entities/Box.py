from src.game.entities.Entity import Entity
from assets.sprites.entities.BoxSprite import BoxSprite
from assets.sprites.PixelSprite import load_sprite_sheet_frames
import random

BREAK_SHEET = "assets/pxos/Caixa/caixa_grande.png"
BREAK_FRAME_COUNT = 11
BREAK_DURATION = 0.5

class Box(Entity):
    """
    Box entity.
    Can be broken to drop something
    """
    
    def __init__(self, start_x, start_y, sprite=None, damage = 0):
        super().__init__(start_x, start_y, health=1, width=25, height=60, hitbox=(2, 2, 23, 23), damage=damage)
        self.frames = load_sprite_sheet_frames(BREAK_SHEET, frame_count=BREAK_FRAME_COUNT)
        self.sprite = sprite if sprite is not None else self.frames[0]
        self.is_breaking = False
        self.break_timer = 0.0

    def receive_damage(self, damage):
        if self.is_breaking:
            return
        self.health -= damage
        if self.health < 1:
            self.health = 0
            self.is_breaking = True  # só fica "alive=False" depois da animação

    def update(self, dt):
        if not self.is_breaking:
            return
        self.break_timer += dt
        progresso = min(1.0, self.break_timer / BREAK_DURATION)
        indice = min(len(self.frames) - 1, int(progresso * len(self.frames)))
        self.sprite = self.frames[indice]
        if progresso >= 1.0:
            self.alive = False 

    def get_polygons(self):
          return self.sprite.get_world_polygons(self.x, self.y)

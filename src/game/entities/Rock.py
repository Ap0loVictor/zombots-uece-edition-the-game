from assets.sprites.entities.RockSprite import RockSprite
from src.game.entities.Prop import Prop

class Rock(Prop):
    """
    Entidade estática representando uma parede ou pedra intransponível.
    """
    def __init__(self, x, y):
        # A posição da pedra no mundo
        super().__init__(x, y, width=32, height=32, hitbox=(2, 2, 28, 28))
        self.damage = 34 # Temporário
        # Inicia o sprite
        self.sprite = RockSprite()
        
    def get_polygons(self):
        """
        Retorna a lista de polígonos prontos para renderização, baseados
        na posição da pedra.
        """
        return self.sprite.get_world_polygons(self.x, self.y)

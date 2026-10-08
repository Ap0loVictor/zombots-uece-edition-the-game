from assets.sprites.props.TornSprite import TornSprite
from src.game.props.Prop import Prop

class Torn(Prop):
    """
    Entidade estática representando uma parede ou pedra intransponível.
    """
    def __init__(self, x, y):
        # A posição da pedra no mundo
        super().__init__(x, y, width=16, height=16, hitbox=(2, 2, 14, 14), sprite = TornSprite())
        self.damage = 10

        
    def get_polygons(self):
        """
        Retorna a lista de polígonos prontos para renderização, baseados
        na posição da pedra.
        """
        return self.sprite.get_world_polygons(self.x, self.y)

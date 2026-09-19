from assets.sprites.temp.TempRock import TemporaryRockSprite

class Rock:
    """
    Entidade estática representando uma parede ou pedra intransponível.
    """
    def __init__(self, x, y):
        # A posição da pedra no mundo
        self.x = float(x)
        self.y = float(y)
        
        # 32 igual os pixel da pedra
        self.width = 32
        self.height = 32
        
        # Inicia o sprite
        self.sprite = TemporaryRockSprite()
        
    def get_polygons(self):
        """
        Retorna a lista de polígonos prontos para renderização, baseados
        na posição da pedra.
        """
        return self.sprite.get_world_polygons(self.x, self.y)

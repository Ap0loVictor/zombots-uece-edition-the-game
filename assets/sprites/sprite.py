class Sprite:
    """
    Classe base abstrata para representação visual de entidades no jogo.
    Define o contrato para obtenção de polígonos e partes desenháveis.
    """

    def __init__(self):
        self.parts = []

    def get_parts(self):
        """
        Retorna a lista de partes com coordenadas locais relativas a (0, 0).
        """
        return self.parts

    def get_world_polygons(self, origin_x, origin_y, direction="right"):
        """
        Calcula os polígonos no espaço do mundo, aplicando translação e orientação.
        
        :param origin_x: Posição X da entidade no mundo.
        :param origin_y: Posição Y da entidade no mundo.
        :param direction: Direção da entidade ("left" ou "right").
        :return: Lista de dicionários contendo {"name", "vertices", "color"}.
        """
        raise NotImplementedError("Subclasses devem implementar get_world_polygons")

from assets.sprites.sprite import Sprite

ROCK_COLOR = (100, 100, 100) # Cinza

# Vértices da pedra (um quadrado de 32x32 pixels)
# Começando de 0,0 (canto superior esquerdo) até 32,32
ROCK_POLYGON = [
    (0, 0),
    (32, 0),
    (32, 32),
    (0, 32)
]

class TemporaryRockSprite(Sprite):
    def __init__(self):
        super().__init__()
        self.parts = [
            {"name": "body", "vertices": ROCK_POLYGON, "color": ROCK_COLOR}
        ]

    def get_world_polygons(self, origin_x, origin_y):
        """
        Retorna as partes convertidas para o espaço da tela.
        origin_x e origin_y representam o canto superior esquerdo da pedra.
        """
        world_polygons = []
        for part in self.parts:
            transformed_vertices = []
            for vx, vy in part["vertices"]:
                wx = origin_x + vx
                wy = origin_y + vy
                transformed_vertices.append((wx, wy))
            
            world_polygons.append({
                "name": part["name"],
                "vertices": transformed_vertices,
                "color": part["color"]
            })
        return world_polygons

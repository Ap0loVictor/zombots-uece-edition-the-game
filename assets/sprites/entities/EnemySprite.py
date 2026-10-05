from assets.sprites.sprite import Sprite
from assets.sprites.PixelSprite import PixelSprite

ROBO = (0, 0, 255)
ZOMBIES = (0, 128, 0)
SUBBOSS = (255, 140, 0)   # laranja
FINALBOSS = (150, 0, 150)

BODY_POLYGON = [
    (0, 0),
    (16, 0),
    (16, 48),
    (0, 48)
]

class EnemySprite(Sprite):

    def __init__(self, color=ZOMBIES):
        super().__init__()
        self.parts = [
            {"name": "body", "vertices": BODY_POLYGON, "color": color}
        ]

    def get_world_polygons(self, origin_x, origin_y, direction="down"):
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


def get_enemy_sprite(enemy_type="zombie"):
    """Sprite de imagem para a renderização principal."""
    sprites = {
        "robot": "assets/pxos/Jannsen_Sprites/jan_idle_32x64.png",
        "zombie": "assets/pxos/Marques_Sprites/marques_idle_32x64.png",
    }

    path = sprites.get(enemy_type, sprites["zombie"])
    return PixelSprite(path)


def get_enemy_polygon(enemy_type="zombie"):
    """Representação geométrica para o minimapa."""
    if enemy_type == "robot":
        return EnemySprite(ROBO)
    if enemy_type == "subboss":
        return EnemySprite(SUBBOSS)
    if enemy_type == "finalboss":
        return EnemySprite(FINALBOSS)

    return EnemySprite(ZOMBIES)


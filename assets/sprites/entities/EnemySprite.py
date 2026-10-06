from assets.sprites.sprite import Sprite
from assets.sprites.PixelSprite import PixelSprite

ROBO = (0, 0, 255)
ZOMBIES = (0, 128, 0)
ZOMBOT = (255, 255, 0)
SUB_BOSS = (255, 140, 0)  
FINAL_BOSS = (150, 0, 150)

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
        "robot": "assets/pxos/bases/robotBase.png",
        "zombie": "assets/pxos/bases/zombieBase.png",
        "zombot": "assets/pxos/bases/zombotBase.png"
    }

    path = sprites.get(enemy_type, sprites["zombie"])
    return PixelSprite(path)


def get_enemy_polygon(enemy_type="zombie"):
    """Representação geométrica para o minimapa."""
    if enemy_type == "robot":
        return EnemySprite(ROBO)
    if enemy_type == "zombot":
        return EnemySprite(ZOMBOT)
    if enemy_type == "subboss":
        return EnemySprite(SUB_BOSS)
    if enemy_type == "finalboss":
        return EnemySprite(FINAL_BOSS)

    return EnemySprite(ZOMBIES)


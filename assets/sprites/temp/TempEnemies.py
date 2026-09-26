from assets.sprites.sprite import Sprite


# ============================================================
# CORES
# ============================================================


ROBO = (0, 0, 255)
ZOMBIES = (0, 128, 0)



# ============================================================
# POLÍGONO LOCAL DO inimigo (Centro em 0, 0)
# Retângulo vertical: 16 de largura x 48 de altura
# ============================================================

BODY_POLYGON = [
    (-8, -24),
    (8, -24),
    (8, 24),
    (-8, 24)
]


class TemperoraryEnemieSprite(Sprite):

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

def get_temp_enemies(enemy_type="zombie"):

    if enemy_type == "robot":
        return TemperoraryEnemieSprite(ROBO)
    
    return TemperoraryEnemieSprite(ZOMBIES)


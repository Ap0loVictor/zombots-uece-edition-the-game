# ============================================================
# TEMPORARY PLAYER SPRITE
# ============================================================

from assets.sprites.sprite import Sprite

RED = (220, 50, 50)

# ============================================================
# POLÍGONO LOCAL DO PERSONAGEM (Centro em 0, 0)
# Retângulo vertical: 16 de largura x 48 de altura
# ============================================================

BODY_POLYGON = [
    (0, 0),
    (16, 0),
    (16, 48),
    (0, 48)
]

ARM_POLYGON_RIGHT = [
    (16, 10),   # começa na borda direita do body
    (34, 10),
    (34, 46),
    (16, 46)
]

ARM_POLYGON_LEFT = [
    (-18, 10),  # espelhado: sai pela borda esquerda do body
    (0, 10),
    (0, 46),
    (-18, 46)
]

ARM_POLYGON_UP = [
    (-10, -18),   # sai por cima do body
    (26, -18),
    (26, 0),
    (-10, 0)
]

ARM_POLYGON_DOWN = [
    (-10, 48),    # sai por baixo do body
    (26, 48),
    (26, 66),
    (-10, 66)
]

class PlayerSprite(Sprite):
    """
    Representação vetorial/poligonal temporária do jogador.
    Um retângulo vermelho vertical (em pé).
    """

    def __init__(self):
        super().__init__()
        self.parts = [
            {"name": "body", "vertices": BODY_POLYGON, "color": RED},
            {"name": "arm", "vertices": ARM_POLYGON_RIGHT, "color": RED},
        ]

    def get_world_polygons(self, origin_x, origin_y, direction="down", attacking=False):
        """
        Calcula os vértices no espaço do mundo aplicando
        a translação da posição (origin_x, origin_y).
        """
        world_polygons = []

        arm_polygons = {
            "right": ARM_POLYGON_RIGHT,
            "left": ARM_POLYGON_LEFT,
            "up": ARM_POLYGON_UP,
            "down": ARM_POLYGON_DOWN,
        }

        for part in self.parts:
            if part["name"] == "arm":
                if not attacking:
                    continue
                vertices = arm_polygons.get(direction, ARM_POLYGON_RIGHT)
            else:
                vertices = part["vertices"]

            transformed_vertices = []
            for vx, vy in vertices:
                wx = origin_x + vx
                wy = origin_y + vy
                transformed_vertices.append((wx, wy))

            world_polygons.append({
                "name": part["name"],
                "vertices": transformed_vertices,
                "color": part["color"]
            })

        return world_polygons

    def get_attack_hitbox(self, reach=18, size=36):
        if self.direction == "right":
            return self.x + self.width, self.y + 10, reach, size
        elif self.direction == "left":
            return self.x - reach, self.y + 10, reach, size
        else:
            w, h = size, reach
            x = self.x - (w - self.width) / 2
            y = self.y - reach if self.direction == "up" else self.y + self.height
            return x, y, w, h


def get_temp_player():
    """
    Função de compatibilidade para obter a estrutura de partes locais.
    """
    return PlayerSprite().get_parts()
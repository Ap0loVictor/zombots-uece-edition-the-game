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
    (-8, -24),
    (8, -24),
    (8, 24),
    (-8, 24)
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
        ]

    def get_world_polygons(self, origin_x, origin_y, direction="down"):
        """
        Calcula os vértices no espaço do mundo aplicando
        a translação da posição (origin_x, origin_y).
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


def get_temp_player():
    """
    Função de compatibilidade para obter a estrutura de partes locais.
    """
    return PlayerSprite().get_parts()
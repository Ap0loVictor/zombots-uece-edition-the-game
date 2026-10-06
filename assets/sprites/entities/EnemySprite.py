from assets.sprites.sprite import Sprite
from assets.sprites.PixelSprite import load_sprite_sheet_frames


# Caminhos apenas: os frames são carregados quando o inimigo é criado.
ENEMY_ANIMATIONS = {
    "zombie": {
        "idle": ("Zombie_Sprites/zombie_idle_32x64_sheet.png", 6),
        "walk": ("Zombie_Sprites/Walking_Sprites/zombie_walk_spritesheet_256x64.png", 8),
        "attack": ("Zombie_Sprites/Atack_Sprites/zombie_attack_spritesheet_4x_1024x256.png", 8),
    },
    "robot": {
        "idle": ("Robot_Sprites/robot_idle_32x64_sheet.png", 6),
        "walk": ("Robot_Sprites/robot_walk_spritesheet_256x64.png", 8),
        "attack": ("Robot_Sprites/robot_attack_spritesheet_256x64.png", 8),
    },
    "zombot": {
        "idle": ("Zombot_Sprites/zombot_idle_32x64_sheet.png", 6),
        "walk": ("Zombot_Sprites/zombot_walk_spritesheet_256x64.png", 8),
        "attack": ("Zombot_Sprites/zombot_attack_spritesheet_256x64.png", 8),
    },
    "bobie": {
        "idle": ("Bobie-Zombie_Sprites/bobie_idle_32x64_sheet.png", 6),
        "walk": ("Bobie-Zombie_Sprites/bobie_walk_spritesheet_256x64.png", 8),
        "attack": ("Bobie-Zombie_Sprites/bobie_attack_spritesheet_256x64.png", 8),
    },
}


def _animation_paths(enemy_type):
    aliases = {"robo": "robot", "zumbi": "zombie", "bobie-zombie": "bobie"}
    enemy_type = aliases.get(enemy_type.lower(), enemy_type.lower())
    # Chefes continuam usando o visual do zumbi até terem assets próprios.
    return ENEMY_ANIMATIONS.get(enemy_type, ENEMY_ANIMATIONS["zombie"])


def get_enemy_animations(enemy_type="zombie"):
    return {
        state: load_sprite_sheet_frames("assets/pxos/" + path, frame_count=count)
        for state, (path, count) in _animation_paths(enemy_type).items()
    }

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
    """Primeiro frame idle, mantendo a interface usada por outros chamadores."""
    path, count = _animation_paths(enemy_type)["idle"]
    return load_sprite_sheet_frames("assets/pxos/" + path, frame_count=count)[0]


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

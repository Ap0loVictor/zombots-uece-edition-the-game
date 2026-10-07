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


_CACHE_ANIMACOES = {}

def get_enemy_animations(enemy_type="zombie"):
    caminhos = _animation_paths(enemy_type)
    chave = id(caminhos)  # os dicts de ENEMY_ANIMATIONS são constantes
    if chave not in _CACHE_ANIMACOES:
        _CACHE_ANIMACOES[chave] = {
            state: load_sprite_sheet_frames("assets/pxos/" + path, frame_count=count)
            for state, (path, count) in caminhos.items()
        }
    return _CACHE_ANIMACOES[chave]


# Vilões: cada folha tem frames de larguras iguais; "altura" é a altura em tela do frame de andar.
VILLAIN_ANIMATIONS = {
    "professor": {
        "altura": 160,
        "sheets": {
            "walk": ("Vilões/Professor/andar.png", 9),
            "punch": ("Vilões/Professor/bater.png", 7),
            "kick": ("Vilões/Professor/chutar.png", 7),
            "special": ("Vilões/Professor/supergolpe.png", 5),
            "fall": ("Vilões/Professor/cair_derrotado.png", 7),
        },
    },
    "mrblack": {
        "altura": 150,
        "sheets": {
            "walk": ("Vilões/MrBlack/andar.png", 8),
            "punch": ("Vilões/MrBlack/bater.png", 7),
            "kick": ("Vilões/MrBlack/chutar.png", 7),
            "special": ("Vilões/MrBlack/dash_dano.png", 6),
            "fall": ("Vilões/MrBlack/cair_derrotado.png", 7),
        },
    },
}

_CACHE_VILOES = {}

def get_villain_animations(kind):
    """Retorna {"scale": fator único do personagem, "frames": {estado: [frames]}}."""
    if kind not in _CACHE_VILOES:
        dados = VILLAIN_ANIMATIONS[kind]
        frames = {
            estado: load_sprite_sheet_frames("assets/pxos/" + path, frame_count=count)
            for estado, (path, count) in dados["sheets"].items()
        }
        _CACHE_VILOES[kind] = {"scale": dados["altura"] / frames["walk"][0].height, "frames": frames}
    return _CACHE_VILOES[kind]


ROBO = (0, 0, 255)
ZOMBIES = (0, 128, 0)
ZOMBOT = (255, 255, 0)
PROFESSOR = (190, 140, 190)
MR_BLACK = (90, 30, 110)

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
    if enemy_type == "professor":
        return EnemySprite(PROFESSOR)
    if enemy_type == "mrblack":
        return EnemySprite(MR_BLACK)

    return EnemySprite(ZOMBIES)

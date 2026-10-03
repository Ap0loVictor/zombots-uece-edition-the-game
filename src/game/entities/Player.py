from src.game.entities.Entity import Entity
from src.game.movement.MovementPlayer import MovementPlayer
from assets.sprites.entities.PlayerSprite import PlayerSprite
from assets.sprites.PixelSprite import PixelSprite

class Player(Entity):
    """
    Entidade do Jogador.
    """

    def __init__(self, start_x, start_y, speed=250.0, direction="down", movement=None, sprite=None, invincibility_duration=2.0, attack_duration=0.2):
        super().__init__(start_x, start_y, health=100, width=64, height=128, hitbox=(17, 20, 32, 90), damage=10)
        self.invincibility_duration = invincibility_duration
        self.invincibility_remaining = 0.0

        self.attack_duration = attack_duration
        self.attack_timer = 0.0
        self.has_hit = False

        # Mecânica especializada de movimentação (injeção ou padrão)
        self.movement = movement if movement is not None else MovementPlayer(speed=speed, direction=direction)

        # Sprite visual temporário com polígonos
        
        self.sprite = sprite if sprite is not None else PixelSprite("assets/pxos/Apolo_Sprites/apolo_idle_32x64.png")

    @property
    def is_invincible(self):
        return self.invincibility_remaining > 0.0

    def start_invincibility(self):
        if not self.alive or self.is_invincible or self.invincibility_duration <= 0:
            return
        self.invincibility_remaining = self.invincibility_duration
        print("IFRAMES ATIVO")

    def receive_damage(self, damage):
        if not self.alive or self.is_invincible or damage <= 0:
            return False

        super().receive_damage(damage)
        if self.alive:
            print(f"Vida do jogador: {self.health}")
            self.start_invincibility()
        return True

    @property
    def is_attacking(self):
        return self.attack_timer > 0.0

    def start_attack(self):
        if not self.alive or self.is_attacking:
            return
        self.attack_timer = self.attack_duration
        self.has_hit = False

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    def update(self, dt, keys, level=None, solid_entities=None, bounds=None):
        """
        Delega a lógica de movimentação para o componente especializado,
        permitindo colisões opcionais com level, solid_entities e bounds (limites do mundo).
        """

        self.invincibility_remaining = max(0.0, self.invincibility_remaining - dt)
        self.attack_timer = max(0.0, self.attack_timer -dt)
        if self.alive:
            self.x, self.y = self.movement.update(self, dt, keys, level=level, solid_entities=solid_entities, bounds=bounds)

    # ========================================================
    # PONTO DE INTERAÇÃO / MIRA
    # ========================================================

    def get_facing_point(self, offset=16):
        hx, hy, hw, hh = self.hitbox

        px = self.x + hx + hw / 2
        py = self.y + hy + hh / 2

        if self.direction == "up":
            py -= offset
        elif self.direction == "down":
            py += offset
        elif self.direction == "left":
            px -= offset
        elif self.direction == "right":
            px += offset

        return px, py
    # ========================================================
    # SPRITE / RENDERIZAÇÃO
    # ========================================================

    def get_polygons(self):
        if hasattr(self.sprite, "get_world_polygons"):
            return self.sprite.get_world_polygons(
                self.x,
                self.y,
                self.direction,
                attacking=self.is_attacking
            )

        hx, hy, hw, hh = self.hitbox

        return [{
            "name": "body",
            "vertices": [
                (self.x + hx, self.y + hy),
                (self.x + hx + hw, self.y + hy),
                (self.x + hx + hw, self.y + hy + hh),
                (self.x + hx, self.y + hy + hh)
            ],
            "color": (220, 50, 50)
        }]

    def get_attack_hitbox(self, reach=28, size=40):
        hx, hy, hw, hh = self.hitbox

        if self.direction in ("left", "right"):
            w, h = reach, size
            x = (
                self.x + hx - reach
                if self.direction == "left"
                else self.x + hx + hw
            )
            y = self.y + hy + (hh - h) / 2

        else:
            w, h = size, reach
            x = self.x + hx + (hw - w) / 2
            y = (
                self.y + hy - reach
                if self.direction == "up"
                else self.y + hy + hh
            )
        return x, y, w, h


    # ========================================================
    # GETTERS E PROPRIEDADES DE COMPATIBILIDADE
    # ========================================================

    def get_position(self):
        return self.x, self.y

    def get_direction(self):
        return self.movement.direction

    @property
    def direction(self):
        return self.movement.direction

    @direction.setter
    def direction(self, value):
        self.movement.direction = value

    @property
    def speed(self):
        return self.movement.speed

    @speed.setter
    def speed(self, value):
        self.movement.speed = value

    @property
    def is_moving(self):
        return self.movement.is_moving

    @property
    def was_moving(self):
        return self.movement.was_moving
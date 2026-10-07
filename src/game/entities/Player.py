import random

from src.engine.audio import audio
from src.game.entities.Entity import Entity
from src.game.entities.Hadouken import Hadouken
from src.game.movement.MovementPlayer import MovementPlayer
from assets.sprites.entities.PlayerSprite import PlayerSprite
from assets.sprites.PixelSprite import PixelSprite, load_sprite_sheet_frames

PERSONAGENS = {
    "apolo":   {"pasta": "assets/pxos/Apolo_Sprites/",   "idle": "apolo_idle_32x64.png"},
    "jannsen": {"pasta": "assets/pxos/Jannsen_Sprites/",  "idle": "jan_idle_32x64.png"},
    "marques": {"pasta": "assets/pxos/Marques_Sprites/",  "idle": "marques_idle_32x64.png"},
}

class Player(Entity):
    """
    Entidade do Jogador.
    """

    def __init__(self, start_x, start_y, character="apolo", speed=250.0, direction="down", movement=None, sprite=None, invincibility_duration=2.0, attack_duration=0.2):
        super().__init__(start_x, start_y, health=100, width=64, height=128, hitbox=(17, 20, 32, 90), damage=25)
        self.invincibility_duration = invincibility_duration
        self.invincibility_remaining = 0.0

        self.attack_duration = attack_duration
        self.attack_timer = 0.0
        self.has_hit = False
        self.attack_cooldown_duration = 0.4
        self.attack_cooldown_timer = 0.0

        # Mecânica especializada de movimentação (injeção ou padrão)
        self.movement = movement if movement is not None else MovementPlayer(speed=speed, direction=direction)

        self.dash_speed_multiplier = 3.5
        self.dash_duration = 0.2
        self.dash_cooldown_duration = 1.0
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_dx = 0.0
        self.dash_dy = 0.0
        self.flip_x = False

        self._timer_passo = 0.0
        self._indice_passo = 0
        self._intervalo_passo = 0.12  # avança um frame da caminhada a cada 0.12s
        self.special_charge_time = 10.0
        self.special_timer = 0.0
        self.cast_duration = 0.3
        self.cast_timer = 0.0

        # Carrega ações somente do personagem confirmado na seleção.
        self.character = character if character in PERSONAGENS else "apolo"
        dados = PERSONAGENS[self.character]
        base = dados["pasta"]
        self.sprite_idle = PixelSprite(base + dados["idle"])

        if self.character == "apolo":
            self.sprite_windup = PixelSprite(base + "apolo_punch_windup_32x64.png")
            self.sprite_extended = PixelSprite(base + "apolo_punch_extended_32x64.png")
            self.sprite_recoil = PixelSprite(base + "apolo_punch_recoil_32x64.png")
            self.sprite_walk_right = PixelSprite(base + "apolo_walk_right_32x64.png")
            self.walk_frames = [self.sprite_idle, self.sprite_walk_right]
            self.dash_frames = load_sprite_sheet_frames(base + "apolo_dash.png", frame_count=11)
        elif self.character == "jannsen":
            # PNGs exportados sem alterações dos arquivos .pxo na mesma pasta.
            self.sprite_windup = PixelSprite(base + "Atack/davi_guard_pose_32x64.png")
            self.sprite_extended = PixelSprite(base + "Atack/davi_punch_pose_32x64.png")
            self.sprite_recoil = PixelSprite(base + "Atack/davi_guard2_pose_32x64.png")
            self.walk_frames = load_sprite_sheet_frames(base + "Walking/walk_spritesheet_256x64(2).png", frame_count=8)
            self.sprite_walk_right = self.walk_frames[1]
            self.dash_frames = load_sprite_sheet_frames(base + "jan_dash_style2_sheet_112x64.png", frame_count=11)
        elif self.character == "marques":
            self.sprite_windup, self.sprite_extended, self.sprite_recoil = load_sprite_sheet_frames(
                base + "Fight_Set/punch_spritesheet_96x64.png", frame_count=3
            )
            self.walk_frames = load_sprite_sheet_frames(base + "Walking_Set/walk_spritesheet_256x64.png", frame_count=8)
            self.sprite_walk_right = self.walk_frames[1]
            self.dash_frames = load_sprite_sheet_frames(base + "marques_dash_style2_sheet_112x64.png", frame_count=11)

        self.sprite = sprite if sprite is not None else self.sprite_idle

    def start_invincibility(self):
        if not self.alive or self.is_invincible or self.invincibility_duration <= 0:
            return
        self.invincibility_remaining = self.invincibility_duration
        print("IFRAMES ATIVO")

    def receive_damage(self, damage):
        if not self.alive or self.is_invincible or self.is_dashing or damage <= 0:
            return False

        super().receive_damage(damage)
        if self.alive:
            audio.play_sfx(random.choice(("player_damage_1", "player_damage_2")))
            print(f"Vida do jogador: {self.health}")
            self.start_invincibility()
        else:
            audio.play_sfx("player_death")
        return True


    def start_dash(self):
        if not self.alive or self.is_dashing or self.dash_cooldown_timer > 0.0:
            return

        dx, dy = {
            "left": (-1, 0), "right": (1, 0),
            "up": (0, -1), "down": (0, 1),
        }[self.direction]

        self.dash_dx = dx * self.speed * self.dash_speed_multiplier
        self.dash_dy = dy * self.speed * self.dash_speed_multiplier
        self.dash_timer = self.dash_duration
        self.dash_cooldown_timer = self.dash_cooldown_duration

    def _atualizar_sprite(self, dt):
        self.flip_x = False

        if self.is_dashing:
            progresso = 1.0 - (self.dash_timer / self.dash_duration)
            indice = min(len(self.dash_frames) - 1, int(progresso * len(self.dash_frames)))
            self.sprite = self.dash_frames[indice]
            self.flip_x = (self.direction == "left")
            return
        
        if self.is_casting:
            self.sprite = self.sprite_extended  # braço estendido enquanto lança
            self.flip_x = (self.direction == "left")
            return

        if self.is_attacking:
            progresso = 1.0 - (self.attack_timer / self.attack_duration)

            if progresso < 0.4:
                self.sprite = self.sprite_windup
            elif progresso < 0.8:
                self.sprite = self.sprite_extended
            else:
                self.sprite = self.sprite_recoil

            self.flip_x = (self.direction == "left")
            return

        if self.is_moving:
            self._timer_passo += dt
            if self._timer_passo >= self._intervalo_passo:
                self._timer_passo = 0.0
                self._indice_passo = (self._indice_passo + 1) % len(self.walk_frames)

            self.flip_x = (self.direction == "left")
            self.sprite = self.walk_frames[self._indice_passo]
        else:
            self.sprite = self.sprite_idle
            self.flip_x = (self.direction == "left")
            self._timer_passo = 0.0
            self._indice_passo = 0

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    def update(self, dt, keys, level=None, solid_entities=None, bounds=None):
        """
        Delega a lógica de movimentação para o componente especializado,
        permitindo colisões opcionais com level, solid_entities e bounds (limites do mundo).
        """

        self.invincibility_remaining = max(0.0, self.invincibility_remaining - dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)
        self.dash_cooldown_timer = max(0.0, self.dash_cooldown_timer - dt)

        self.cast_timer = max(0.0, self.cast_timer - dt)

        if self.alive:
            
            self.special_timer = min(self.special_charge_time, self.special_timer + dt)
            if self.is_dashing:
                self.dash_timer = max(0.0, self.dash_timer - dt)
                self.x, self.y = self.movement.move_axis(
                    self, self.dash_dx * dt, self.dash_dy * dt,
                    level=level, solid_entities=solid_entities, bounds=bounds
                )
            else:
                self.x, self.y = self.movement.update(self, dt, keys, level=level, solid_entities=solid_entities, bounds=bounds)

        self._atualizar_sprite(dt)

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
    def is_invincible(self):
        return self.invincibility_remaining > 0.0

    @property
    def is_attacking(self):
        return self.attack_timer > 0.0

    def start_attack(self):
        if not self.alive or self.is_attacking or self.attack_cooldown_timer > 0.0:
            return
        self.attack_timer = self.attack_duration
        self.attack_cooldown_timer = self.attack_cooldown_duration  
        self.has_hit = False
        audio.play_sfx("player_punch")

    @property
    def is_dashing(self):
        return self.dash_timer > 0.0
    
    @property
    def special_progress(self):
        """0.0 a 1.0: quanto da barra do especial está cheia."""
        return min(1.0, self.special_timer / self.special_charge_time)

    @property
    def special_ready(self):
        return self.special_timer >= self.special_charge_time

    @property
    def is_casting(self):
        return self.cast_timer > 0.0

    def start_special(self):
        """Dispara o Hadouken se a barra estiver cheia. Retorna o projétil ou None."""
        if not self.alive or not self.special_ready or self.is_dashing or self.is_casting:
            return None

        self.special_timer = 0.0
        self.cast_timer = self.cast_duration
        audio.play_sfx("hadouken")

        fx, fy = self.get_facing_point(offset=34)  # nasce na frente do jogador
        return Hadouken(fx, fy, self.direction)

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

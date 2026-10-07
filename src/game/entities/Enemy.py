from src.game.entities.Entity import Entity
from src.game.movement.MovementEnemies import MovementEnemies
from src.game.mechanics.Physics import check_aabb_collision, get_world_hitbox
from assets.sprites.entities.EnemySprite import get_enemy_animations, get_enemy_polygon
import random


class Enemy(Entity):
    """
    Entidade dos Inimigos.
    Coordena posição, movimentação e sprite.
    Diferente do Player, o inimigo não recebe input do usuário:
    seu movimento é decidido por uma IA interna (ex: perseguir o player).
    """
    WIDTH = 64
    HEIGHT = 128
    HITBOX = (17, 20, 32, 90)
    
    def __init__(self, start_x, start_y, enemy_type=None, speed=None, sprite=None, movement=None, damage=0):
        super().__init__(start_x, start_y, health=50, width=self.WIDTH, height=self.HEIGHT, hitbox=self.HITBOX, damage=damage)

        self.enemy_type = enemy_type if enemy_type is not None else random.choice(["robot", "zombie"])
        resolved_speed = speed if speed is not None else 100.0

        self.movement = movement if movement is not None else MovementEnemies(speed=resolved_speed)
        if sprite is None:
            animations = get_enemy_animations(self.enemy_type)
            self.sprite_idle = animations["idle"][0]
            self.walk_frames = animations["walk"]
            self.attack_frames = animations["attack"]
        else:
            self.sprite_idle = sprite
            self.walk_frames = [sprite]
            self.attack_frames = [sprite]
        self.sprite = self.sprite_idle
        self.flip_x = False
        self._timer_passo = 0.0
        self._indice_passo = 0
        self._intervalo_passo = 0.12
        self.attack_duration = 0.6
        self.attack_timer = 0.0
        self.attack_cooldown_duration = 1.0
        self.attack_cooldown_timer = 0.0
        self.minimap_sprite = get_enemy_polygon(self.enemy_type)
        self.knockback_dx = 0.0
        self.knockback_dy = 0.0
        self.knockback_timer = 0.0

    @property
    def is_attacking(self):
        return self.attack_timer > 0.0

    def try_attack(self, player):
        """Inicia um golpe por contato, no máximo uma vez por segundo.

        Retorna True quando o golpe começa, mesmo se o jogador bloquear o dano.
        """
        if not self.alive or not player.alive or self.is_attacking or self.attack_cooldown_timer > 0.0:
            return False
        if not check_aabb_collision(*get_world_hitbox(self), *get_world_hitbox(player)):
            return False

        dx = player.x - self.x
        dy = player.y - self.y
        if dx != 0:
            self.movement.direction = "left" if dx < 0 else "right"
        elif dy != 0:
            self.movement.direction = "up" if dy < 0 else "down"
        self.attack_timer = self.attack_duration
        self.attack_cooldown_timer = self.attack_cooldown_duration
        self._atualizar_sprite(0.0, moving=False)

        # Uma tentativa de dano por golpe; i-frames e dash são tratados pelo Player.
        if player.receive_damage(self.damage):
            force = 200
            dist = max(1, (dx**2 + dy**2) ** 0.5)
            self.apply_knockback((-dx / dist) * force, (-dy / dist) * force)
        return True

    def _atualizar_sprite(self, dt, moving):
        self.flip_x = (self.direction == "left")
        if self.is_attacking:
            progresso = 1.0 - self.attack_timer / self.attack_duration
            indice = min(len(self.attack_frames) - 1, int(progresso * len(self.attack_frames)))
            self.sprite = self.attack_frames[indice]
            self._timer_passo = 0.0
            self._indice_passo = 0
        elif moving:
            self._timer_passo += dt
            while self._timer_passo >= self._intervalo_passo:
                self._timer_passo -= self._intervalo_passo
                self._indice_passo = (self._indice_passo + 1) % len(self.walk_frames)
            self.sprite = self.walk_frames[self._indice_passo]
        else:
            self.sprite = self.sprite_idle
            self._timer_passo = 0.0
            self._indice_passo = 0


    def apply_knockback(self, dx, dy, duration=0.15):
        self.knockback_dx = dx
        self.knockback_dy = dy
        self.knockback_timer = duration


    def update(self, dt, target=None, level=None, solid_entities=None, bounds=None):
        if not self.alive:
            return

        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)
        old_position = self.get_position()

        if self.knockback_timer > 0.0:
            self.knockback_timer = max(0.0, self.knockback_timer - dt)
            dx = self.knockback_dx * dt
            dy = self.knockback_dy * dt
            self.x, self.y = self.movement.move_axis(self, dx, dy, solid_entities=solid_entities, bounds=bounds)
        elif not self.is_attacking:
            self.x, self.y = self.movement.update(
                self, dt, target=target,
                level=level, solid_entities=solid_entities, bounds=bounds
            )

        self._atualizar_sprite(dt, moving=self.get_position() != old_position)

    def get_polygons(self):
          return self.minimap_sprite.get_world_polygons(self.x, self.y, self.direction)


    def get_position(self):
        return self.x, self.y

    @property
    def direction(self):
        return self.movement.direction

    @property
    def speed(self):
        return self.movement.speed



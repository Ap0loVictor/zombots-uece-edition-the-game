import random

from assets.sprites.entities.EnemySprite import get_villain_animations
from src.engine.audio import audio
from src.game.entities.Enemy import Enemy

# Por golpe:
#   frames: duração (s) de cada frame da folha
#   active: frame -> alcance (px a partir do centro do vilão) em que o golpe acerta
#   aoe:    frames ativos que acertam dos dois lados (explosões)
#   damage: multiplicador sobre o dano base
#   move:   frame -> velocidade (px/s) com que o vilão avança durante o golpe
VILLAINS = {
    "professor": {
        "health": 200, "damage": 15, "speed": 80.0,
        "special_range": 170, "special_cooldown": (4.0, 7.0),
        "attacks": {
            "punch": {"frames": [.10, .10, .10, .16, .10, .10, .10], "active": {3: 95}, "damage": 1.0},
            "kick": {"frames": [.08, .08, .10, .10, .12, .08, .08], "active": {2: 90, 3: 100, 4: 105}, "damage": 1.3},
            "special": {"frames": [.45, .30, .18, .30, .25], "active": {2: 175, 3: 190},
                        "aoe": (3,), "damage": 2.0, "move": {2: 380}},
        },
    },
    "mrblack": {
        "health": 500, "damage": 20, "speed": 70.0,
        "special_range": 320, "special_cooldown": (3.5, 6.5),
        "attacks": {
            "punch": {"frames": [.10, .08, .08, .08, .14, .10, .10], "active": {4: 95}, "damage": 1.0},
            "kick": {"frames": [.10, .08, .10, .08, .14, .10, .10], "active": {2: 90, 4: 95}, "damage": 1.3},
            "special": {"frames": [.35, .07, .07, .07, .25, .25], "active": {1: 75, 2: 75, 3: 75, 4: 150},
                        "aoe": (4,), "damage": 2.0, "move": {1: 520, 2: 520, 3: 520}},
        },
    },
}


class Villain(Enemy):
    """Chefe com sprites próprias: anda, soca, chuta, usa o golpe especial e cai ao ser derrotado.

    Os golpes são escolhidos ao acaso entre os que estão ao alcance.
    """
    STAND_DIST = 70       # distância horizontal em que para de perseguir
    ALIGN_Y = 12          # diferença de profundidade (y) tolerada para parar
    ATTACK_Y = 24         # diferença de profundidade máxima para iniciar um golpe
    HIT_Y = 30            # idem, para o golpe acertar (45 nas explosões)
    WALK_STEP = 0.1
    FALL_STEP = 0.13
    FALL_HOLD = 1.0       # tempo deitado antes de sumir
    KNOCKBACK_FACTOR = 0.4

    def __init__(self, start_x, start_y, kind):
        self.stats = VILLAINS[kind]
        animacoes = get_villain_animations(kind)
        self.frames = animacoes["frames"]
        self.scale = animacoes["scale"]
        super().__init__(start_x, start_y, enemy_type=kind, speed=self.stats["speed"],
                         sprite=self.frames["walk"][0], damage=self.stats["damage"])
        self.health = self.max_health = self.stats["health"]
        self.walk_frames = self.frames["walk"]
        self.sprite_idle = self.frames["punch"][0]  # postura de guarda
        self.sprite = self.sprite_idle

        self.facing_left = False
        self.target = None
        self.attack_kind = None
        self.attack_elapsed = 0.0
        self.hit_done = False
        self.attack_cooldown_timer = random.uniform(0.6, 1.2)
        self.special_cooldown_timer = random.uniform(*self.stats["special_cooldown"]) / 2
        self.death_elapsed = 0.0

    @property
    def is_attacking(self):
        return self.attack_kind is not None

    @property
    def playing_death(self):
        """True enquanto a animação de queda ainda precisa ser exibida."""
        total = len(self.frames["fall"]) * self.FALL_STEP + self.FALL_HOLD
        return not self.alive and self.death_elapsed < total

    def sprite_box(self):
        """(deslocamento x, deslocamento y, altura) do frame atual, com os pés alinhados à base da entidade."""
        altura = round(self.sprite.height * self.scale)
        largura = round(self.sprite.width * self.scale)
        return (self.width - largura) / 2, self.height - altura, altura

    def receive_damage(self, damage):
        if not self.alive:
            return
        super().receive_damage(damage)
        if not self.alive:
            self.attack_kind = None
            self.death_elapsed = 0.0

    def _play_death_sound(self):
        audio.play_sfx(f"{self.enemy_type}_death")

    def apply_knockback(self, dx, dy, duration=0.15):
        if self.alive and not self.is_attacking:  # durante o golpe ele não é empurrado
            super().apply_knockback(dx * self.KNOCKBACK_FACTOR, dy * self.KNOCKBACK_FACTOR, duration)

    def _spec(self):
        return self.stats["attacks"][self.attack_kind]

    def _frame_do_golpe(self):
        acumulado = 0.0
        duracoes = self._spec()["frames"]
        for i, duracao in enumerate(duracoes):
            acumulado += duracao
            if self.attack_elapsed < acumulado:
                return i
        return len(duracoes) - 1

    def _iniciar_golpe(self, kind, dx):
        self.attack_kind = kind
        self.attack_elapsed = 0.0
        self.hit_done = False
        if dx != 0:
            self.facing_left = dx < 0
        if kind == "special":
            self.special_cooldown_timer = random.uniform(*self.stats["special_cooldown"])
        effect = "special" if kind == "special" else "attack"
        audio.play_sfx(f"{self.enemy_type}_{effect}")
        self._atualizar_sprite(0.0, moving=False)

    def try_attack(self, player):
        """Sorteia um golpe quando possível e aplica o dano nos frames ativos. True se um golpe começou."""
        if not self.alive or not player.alive:
            return False
        if self.attack_kind:
            self._resolver_golpe(player)
            return False
        if self.attack_cooldown_timer > 0.0 or abs(player.y - self.y) > self.ATTACK_Y:
            return False

        dx = player.x - self.x
        distancia = abs(dx)
        corpo_a_corpo = distancia <= self.STAND_DIST + 20
        opcoes = ["punch", "kick"] if corpo_a_corpo else []
        if self.special_cooldown_timer <= 0.0 and distancia <= self.stats["special_range"]:
            opcoes += ["special"] * (1 if corpo_a_corpo else 2)
        if not opcoes:
            return False

        self._iniciar_golpe(random.choice(opcoes), dx)
        return True

    def _resolver_golpe(self, player):
        spec = self._spec()
        indice = self._frame_do_golpe()
        alcance = spec["active"].get(indice)
        if alcance is None or self.hit_done:
            return

        dx = player.x - self.x
        explosao = indice in spec.get("aoe", ())
        frente = abs(dx) if explosao else (-dx if self.facing_left else dx)
        if frente < -10 or frente > alcance or abs(player.y - self.y) > (45 if explosao else self.HIT_Y):
            return

        self.hit_done = True
        player.receive_damage(round(self.damage * spec["damage"]))

    def _avancar_golpe(self, dt, level, solid_entities, bounds):
        spec = self._spec()
        self.attack_elapsed += dt
        if self.attack_elapsed >= sum(spec["frames"]):
            self.attack_kind = None
            self.attack_cooldown_timer = random.uniform(0.7, 1.5)
            return

        velocidade = spec.get("move", {}).get(self._frame_do_golpe())
        if velocidade and (self.target is None or abs(self.target[0] - self.x) > 45):  # não atravessa o jogador
            passo = velocidade * dt * (-1 if self.facing_left else 1)
            self.x, self.y = self.movement.move_axis(self, passo, 0, level=level,
                                                     solid_entities=solid_entities, bounds=bounds)

    def _perseguir(self, dt, target, level, solid_entities, bounds):
        dx = target[0] - self.x
        dy = target[1] - self.y
        if abs(dx) > 4:
            self.facing_left = dx < 0

        perto = abs(dx) <= self.STAND_DIST
        alinhado = abs(dy) <= self.ALIGN_Y
        if perto and alinhado:
            return
        alvo = (self.x if perto else target[0], self.y if alinhado else target[1])
        self.x, self.y = self.movement.update(self, dt, target=alvo, level=level,
                                              solid_entities=solid_entities, bounds=bounds)

    def update(self, dt, target=None, level=None, solid_entities=None, bounds=None):
        if not self.alive:
            self.death_elapsed += dt
            self._atualizar_sprite(dt, moving=False)
            return

        self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)
        self.special_cooldown_timer = max(0.0, self.special_cooldown_timer - dt)
        if target is not None:
            self.target = target
        old_position = self.get_position()

        if self.attack_kind:
            self._avancar_golpe(dt, level, solid_entities, bounds)
        elif self.knockback_timer > 0.0:
            self.knockback_timer = max(0.0, self.knockback_timer - dt)
            self.x, self.y = self.movement.move_axis(
                self, self.knockback_dx * dt, self.knockback_dy * dt,
                level=level, solid_entities=solid_entities, bounds=bounds)
        elif target is not None:
            self._perseguir(dt, target, level, solid_entities, bounds)

        self._atualizar_sprite(dt, moving=self.get_position() != old_position)

    def _atualizar_sprite(self, dt, moving):
        self.flip_x = self.facing_left
        if not self.alive:
            queda = self.frames["fall"]
            self.sprite = queda[min(len(queda) - 1, int(self.death_elapsed / self.FALL_STEP))]
        elif self.attack_kind:
            self.sprite = self.frames[self.attack_kind][self._frame_do_golpe()]
            self._timer_passo = 0.0
            self._indice_passo = 0
        elif moving:
            self._timer_passo += dt
            while self._timer_passo >= self.WALK_STEP:
                self._timer_passo -= self.WALK_STEP
                self._indice_passo = (self._indice_passo + 1) % len(self.walk_frames)
            self.sprite = self.walk_frames[self._indice_passo]
        else:
            self.sprite = self.sprite_idle
            self._timer_passo = 0.0
            self._indice_passo = 0


class Professor(Villain):
    """Chefe da fase 5."""
    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y, "professor")


class MrBlack(Villain):
    """Chefe da fase 6."""
    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y, "mrblack")

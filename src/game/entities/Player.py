from src.game.entities.Entity import Entity
from src.game.movement.MovementPlayer import MovementPlayer
from assets.sprites.entities.PlayerSprite import PlayerSprite


class Player(Entity):
    """
    Entidade do Jogador.
    """

    def __init__(self, start_x, start_y, speed=250.0, direction="down", movement=None, sprite=None, invincibility_duration=2.0):
        super().__init__(start_x, start_y, health=100, width=48, height=16, hitbox=(-10,-23, 18, 50))
        self.invincibility_duration = invincibility_duration
        self.invincibility_remaining = 0.0

        # Mecânica especializada de movimentação (injeção ou padrão)
        self.movement = movement if movement is not None else MovementPlayer(speed=speed, direction=direction)

        # Sprite visual temporário com polígonos
        self.sprite = sprite if sprite is not None else PlayerSprite()

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
            self.start_invincibility()
        return True

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    def update(self, dt, keys, level=None, solid_entities=None, bounds=None):
        """
        Delega a lógica de movimentação para o componente especializado,
        permitindo colisões opcionais com level, solid_entities e bounds (limites do mundo).
        """

        self.invincibility_remaining = max(0.0, self.invincibility_remaining - dt)
        if self.alive:
            self.x, self.y = self.movement.update(self, dt, keys, level=level, solid_entities=solid_entities, bounds=bounds)

    # ========================================================
    # PONTO DE INTERAÇÃO / MIRA
    # ========================================================

    def get_facing_point(self, offset=16):
        """
        Retorna as coordenadas (px, py) do ponto imediatamente à frente
        do personagem com base na direção para onde ele está olhando.
        """
        px = self.x
        py = self.y

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
        """
        Retorna a lista de polígonos no espaço de mundo prontos para renderização.
        """
        return self.sprite.get_world_polygons(self.x, self.y, self.direction)

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

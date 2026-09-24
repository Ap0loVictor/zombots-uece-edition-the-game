from src.game.entities.Entity import Entity
from src.game.movement.player_movement import PlayerMovement
from assets.sprites.temp.TempPlayer import TemporaryPlayerSprite


class Player(Entity):
    """
    Entidade do Jogador.
    Coordena posição, movimentação cardinal através de PlayerMovement
    e geometria visual através de TemporaryPlayerSprite.
    """

    def __init__(self, start_x, start_y, speed=250.0, direction="down", movement=None, sprite=None):
        super().__init__(start_x, start_y, health=100, width=48, height=16, hitbox=(2,1, 44, 14))

        # Mecânica especializada de movimentação (injeção ou padrão)
        self.movement = movement if movement is not None else PlayerMovement(speed=speed, direction=direction)

        # Sprite visual temporário com polígonos
        self.sprite = sprite if sprite is not None else TemporaryPlayerSprite()

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    def update(self, dt, keys, level=None, solid_entities=None, bounds=None):
        """
        Delega a lógica de movimentação para o componente especializado,
        permitindo colisões opcionais com level, solid_entities e bounds (limites do mundo).
        """

        # print (self.health)
        if self.alive == True:
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
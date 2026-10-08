import math

from src.engine.transformacoes import translacao, rotacao, escala, multiplica_matrizes, aplica_transformacao
from src.engine.fill import scanline_fill_gradiente
from src.engine.primitivas import elipse

DIRECOES = {
    "right": (1, 0), "left": (-1, 0),
    "up": (0, -1), "down": (0, 1),
}


def _estrela(n_pontas, raio_externo, raio_interno):
    """Polígono de estrela centrado na origem (coordenadas locais)."""
    pontos = []
    for i in range(n_pontas * 2):
        r = raio_externo if i % 2 == 0 else raio_interno
        ang = math.pi * i / n_pontas
        pontos.append((r * math.cos(ang), r * math.sin(ang)))
    return pontos


ESTRELA_EXTERNA = _estrela(6, 26, 12)
ESTRELA_INTERNA = _estrela(6, 14, 6)

# Cores por vértice: pontas azuis, reentrâncias brancas (gradiente ponta -> centro)
CORES_EXTERNA = [(60, 140, 255) if i % 2 == 0 else (200, 235, 255) for i in range(12)]
CORES_INTERNA = [(255, 240, 120) if i % 2 == 0 else (255, 255, 255) for i in range(12)]


class Hadouken:
    """
    Projétil do ataque especial.
    Desenhado com polígonos de gradiente por vértice, e com
    translação + rotação + escala feitas por matriz 3x3.
    """

    def __init__(self, centro_x, centro_y, direcao="right", speed=450.0, damage=74,
                 lifetime=2.0):
        self.size = 44
        self.width = self.size
        self.height = self.size
        self.hitbox = None  # usa width/height inteiros (compatível com get_world_hitbox)

        # x, y = canto superior esquerdo; (centro_x, centro_y) é o centro do projétil
        self.x = centro_x - self.size / 2
        self.y = centro_y - self.size / 2

        self.direcao = direcao
        self.vx, self.vy = DIRECOES.get(direcao, (1, 0))
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self.tempo = 0.0
        self.alive = True
        self.atingidos = set()  # id() dos inimigos já acertados: atravessa, mas fere 1 vez

    @property
    def centro(self):
        return self.x + self.size / 2, self.y + self.size / 2

    def update(self, dt, bounds=None):
        if not self.alive:
            return
        self.tempo += dt
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt

        if self.tempo >= self.lifetime:
            self.alive = False
        if bounds is not None:
            min_x, min_y, max_x, max_y = bounds
            if self.x + self.size < min_x or self.x > max_x or self.y + self.size < min_y or self.y > max_y:
                self.alive = False

    def draw(self, tela, camera_x=0):
        cx, cy = self.centro
        cx -= camera_x

        # Cauda: elipses menores e mais apagadas atrás do projétil (escala + translação)
        horizontal = self.vx != 0
        for i in range(1, 4):
            dist = 20 * i
            tx = cx - self.vx * dist
            ty = cy - self.vy * dist
            fade = 1 - i * 0.25
            cor = (int(80 * fade), int(160 * fade), int(255 * fade))
            rx, ry = (int(18 - i * 3), int(10 - i * 2)) if horizontal else (int(10 - i * 2), int(18 - i * 3))
            elipse(tela, tx, ty, rx, ry, cor)

        m, m2 = self._matrizes(cx, cy)
        scanline_fill_gradiente(tela, aplica_transformacao(m, ESTRELA_EXTERNA), CORES_EXTERNA)
        scanline_fill_gradiente(tela, aplica_transformacao(m2, ESTRELA_INTERNA), CORES_INTERNA)

    def _matrizes(self, cx, cy):
        # Estrela externa: gira e "pulsa" (rotação + escala + translação, em matriz)
        pulso = 1.0 + 0.15 * math.sin(self.tempo * 18)
        m = multiplica_matrizes(
            translacao(cx, cy),
            multiplica_matrizes(rotacao(self.tempo * 9), escala(pulso, pulso)),
        )
        # Estrela interna: gira ao contrário
        m2 = multiplica_matrizes(translacao(cx, cy), rotacao(-self.tempo * 14))
        return m, m2

    def get_polygons(self):  # usado pelo minimapa (coordenadas do mundo)
        cx, cy = self.centro
        m, m2 = self._matrizes(cx, cy)
        return [
            {"name": "externa", "vertices": aplica_transformacao(m, ESTRELA_EXTERNA), "color": (60, 140, 255)},
            {"name": "interna", "vertices": aplica_transformacao(m2, ESTRELA_INTERNA), "color": (255, 240, 120)},
        ]

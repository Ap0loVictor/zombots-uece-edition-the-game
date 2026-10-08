import math

from src.engine.fill import scanline_fill_gradiente, interpola_cor
from src.engine.rendering import desenhar_poligono
from src.engine.transformacoes import translacao, rotacao, escala, multiplica_matrizes, aplica_transformacao
from src.game.entities.Entity import Entity

DURACAO_POP = 0.4  # tempo do item saindo da caixa (escala 0 -> 1 com salto)


def _coracao():
    pontos = []
    for i in range(28):
        t = 2 * math.pi * i / 28
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pontos.append((x * 0.7, y * 0.7))
    return pontos


CORACAO = _coracao()
_y0, _y1 = min(p[1] for p in CORACAO), max(p[1] for p in CORACAO)
# cor por vértice: rosa claro no topo, vermelho escuro na ponta de baixo
CORES_CORACAO = [interpola_cor((255, 160, 180), (170, 10, 40), (y - _y0) / (_y1 - _y0)) for _, y in CORACAO]


class Drop(Entity):
    """Coração que sai da caixa e cura o jogador."""
    VIDA = "vida"

    def __init__(self, tipo, centro_x, centro_y):
        super().__init__(centro_x - 12, centro_y - 12, width=24, height=24, health=1, hitbox=(2, 2, 20, 20))
        self.tipo = tipo
        self.tempo = 0.0

    @property
    def pronto(self):
        return self.tempo >= DURACAO_POP  # só pode ser pego depois de sair da caixa

    def update(self, dt):
        self.tempo += dt

    def _matriz(self):
        cx, cy = self.x + self.width / 2, self.y + self.height / 2
        pop = min(1.0, self.tempo / DURACAO_POP)
        esc = pop * (1 + 0.3 * math.sin(pop * math.pi))   # escala com "estouro"
        salto = -20 * math.sin(pop * math.pi)             # translação: sobe e desce

        pulso = 1 + 0.12 * math.sin(self.tempo * 8)
        balanco = 0.15 * math.sin(self.tempo * 3)
        flutua = 3 * math.sin(self.tempo * 4) * pop
        return multiplica_matrizes(
            translacao(cx, cy + salto + flutua),
            multiplica_matrizes(rotacao(balanco), escala(esc * pulso, esc * pulso)),
        )

    def _partes(self):
        return [("coracao", CORACAO, CORES_CORACAO, (255, 225, 230))]

    def draw(self, tela, camera_x=0):
        m = self._matriz()
        for _, pontos, cores, borda in self._partes():
            pts = [(x - camera_x, y) for x, y in aplica_transformacao(m, pontos)]
            scanline_fill_gradiente(tela, pts, cores)
            desenhar_poligono(tela, pts, borda)

    def get_polygons(self):  # usado pelo minimapa (passa pelo recorte Cohen-Sutherland)
        m = self._matriz()
        return [{"name": nome, "vertices": aplica_transformacao(m, pontos), "color": cores[len(cores) // 2]}
                for nome, pontos, cores, _ in self._partes()]
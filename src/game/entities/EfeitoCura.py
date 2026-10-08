import math

from src.engine.fill import scanline_fill_gradiente
from src.engine.fonte import desenhar_texto_centralizado
from src.engine.primitivas import elipse
from src.engine.transformacoes import translacao, rotacao, escala, multiplica_matrizes, aplica_transformacao
from src.game.entities.Drop import CORACAO, CORES_CORACAO

DURACAO = 1.0
COR_AURA = (120, 255, 150)


def _estrela(n_pontas, raio_externo, raio_interno):
    pontos = []
    for i in range(n_pontas * 2):
        r = raio_externo if i % 2 == 0 else raio_interno
        pontos.append((r * math.cos(math.pi * i / n_pontas), r * math.sin(math.pi * i / n_pontas)))
    return pontos


FAISCA = _estrela(4, 7, 2.5)
CORES_FAISCA = [(255, 255, 255) if i % 2 == 0 else (90, 220, 120) for i in range(8)]


class EfeitoCura:
    """Power-up ao pegar o coração: aura, faíscas em órbita, corações subindo e texto."""

    def __init__(self, player, quantidade):
        self.player = player
        self.quantidade = quantidade
        self.tempo = 0.0

    @property
    def vivo(self):
        return self.tempo < DURACAO

    def update(self, dt):
        self.tempo += dt

    def _centro(self):
        hx, hy, hw, hh = self.player.hitbox
        return self.player.x + hx + hw / 2, self.player.y + hy + hh / 2

    # Caixa em volta do jogador: o minimapa usa x/y/width/height para descartar o que está fora da janela
    width = 120
    height = 160

    @property
    def x(self):
        return self._centro()[0] - self.width / 2

    @property
    def y(self):
        return self._centro()[1] - self.height / 2

    def _aura(self, p):
        aura = []
        for k in range(2):
            q = p * 1.6 - k * 0.35
            if 0 < q < 1:
                aura.append((14 + 40 * q, 30 + 50 * q))
        return aura

    def _formas(self, cx, cy):
        """Polígonos (pontos, cores) das faíscas e dos corações para o centro dado."""
        p = min(1.0, self.tempo / DURACAO)
        formas = []

        # Faíscas orbitando: rotação em torno do jogador, escala sobe e desce
        esc = math.sin(math.pi * p)
        for i in range(6):
            ang = self.tempo * 6 + i * math.pi / 3
            m = multiplica_matrizes(
                translacao(cx, cy),
                multiplica_matrizes(rotacao(ang), multiplica_matrizes(translacao(30 + 20 * p, 0), escala(esc, esc))),
            )
            formas.append((aplica_transformacao(m, FAISCA), CORES_FAISCA))

        # Corações subindo: translação para cima e escala que diminui
        for i in range(5):
            s = 0.6 * (1 - p)
            if s <= 0.02:
                continue
            sobe = 20 + p * 70 + (i % 2) * 12
            m = multiplica_matrizes(
                translacao(cx + (i - 2) * 14 + 4 * math.sin(self.tempo * 9 + i), cy - sobe),
                escala(s, s),
            )
            formas.append((aplica_transformacao(m, CORACAO), CORES_CORACAO))
        return formas

    def draw(self, tela, camera_x=0):
        p = min(1.0, self.tempo / DURACAO)
        cx, cy = self._centro()
        cx -= camera_x

        # Aura: elipses que se expandem a partir do corpo
        for rx, ry in self._aura(p):
            elipse(tela, int(cx), int(cy), int(rx), int(ry), COR_AURA)

        for pontos, cores in self._formas(cx, cy):
            scanline_fill_gradiente(tela, pontos, cores)

        if p < 0.9:
            y_texto = int(cy - 55 - p * 40)
            texto = f"+{self.quantidade}"
            desenhar_texto_centralizado(tela, texto, int(cx) + 2, y_texto + 2, (10, 40, 15), 2)
            desenhar_texto_centralizado(tela, texto, int(cx), y_texto, (150, 255, 160), 2)

    def get_polygons(self):  # usado pelo minimapa (coordenadas do mundo)
        p = min(1.0, self.tempo / DURACAO)
        cx, cy = self._centro()
        partes = []
        for rx, ry in self._aura(p):
            contorno = [(cx + rx * math.cos(2 * math.pi * i / 24), cy + ry * math.sin(2 * math.pi * i / 24))
                        for i in range(24)]
            partes.append({"name": "aura", "vertices": contorno, "color": COR_AURA, "contorno": True})
        for pontos, cores in self._formas(cx, cy):
            partes.append({"name": "forma", "vertices": pontos, "color": cores[len(cores) // 2]})
        return partes

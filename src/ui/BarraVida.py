import pygame

from src.engine.rendering import desenhar_poligono
from src.engine.fill import scanline_fill_gradiente
from src.engine.fonte import desenhar_texto

# Cache: a barra só é redesenhada (pixel a pixel) quando a vida muda
_cache = {}


def _cores_por_vida(proporcao):
    """(cor clara do topo, cor escura da base) conforme a vida restante."""
    if proporcao > 0.5:
        return (140, 255, 120), (20, 130, 40)     # verde
    if proporcao > 0.25:
        return (255, 235, 110), (190, 120, 10)    # amarelo/laranja
    return (255, 120, 100), (150, 10, 10)         # vermelho


def _montar_barra(largura, altura, vida, vida_max):
    superficie = pygame.Surface((largura, altura))
    superficie.fill((0, 0, 0))

    # Fundo: gradiente vertical cinza escuro (cor por vértice)
    fundo = [(0, 0), (largura, 0), (largura, altura), (0, altura)]
    scanline_fill_gradiente(superficie, fundo,
                            [(60, 60, 70), (60, 60, 70), (15, 15, 20), (15, 15, 20)])

    proporcao = max(0.0, min(1.0, vida / vida_max)) if vida_max > 0 else 0.0
    largura_cheia = int(largura * proporcao)

    if largura_cheia > 0:
        topo, base = _cores_por_vida(proporcao)
        # Cada vértice tem a sua cor: o lado esquerdo é mais escuro que o direito
        esq_topo = tuple(int(c * 0.7) for c in topo)
        esq_base = tuple(int(c * 0.7) for c in base)
        cheia = [(0, 0), (largura_cheia, 0), (largura_cheia, altura), (0, altura)]
        scanline_fill_gradiente(superficie, cheia, [esq_topo, topo, base, esq_base])

    desenhar_poligono(superficie, [(0, 0), (largura - 1, 0), (largura - 1, altura - 1), (0, altura - 1)],
                      (230, 230, 240))
    return superficie


def desenhar_barra_vida(tela, x, y, vida, vida_max, largura=200, altura=22):
    chave = (int(vida), int(vida_max), largura, altura)
    if chave not in _cache:
        _cache.clear()  # guarda só a barra atual
        _cache[chave] = _montar_barra(largura, altura, vida, vida_max)

    tela.blit(_cache[chave], (x, y))
    desenhar_texto(tela, f"HP {int(vida)}/{int(vida_max)}", x + 4, y + altura + 6, (235, 235, 245), escala=2)

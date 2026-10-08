import numpy as np
import pygame
from src.engine.rendering import setPixel, area_visivel


# ============================================================
# FLOOD FILL / BOUNDARY FILL (iterativos, 4-conectados)
# ============================================================

def flood_fill(superficie, x, y, cor_preenchimento):
    """
    Flood Fill: troca a cor do ponto semente (e de todos os vizinhos com a
    mesma cor) por cor_preenchimento. A região termina onde a cor muda.
    """
    largura, altura = superficie.get_width(), superficie.get_height()
    x, y = int(x), int(y)
    if not (0 <= x < largura and 0 <= y < altura):
        return

    cor_alvo = tuple(superficie.get_at((x, y)))[:3]
    cor_preenchimento = tuple(cor_preenchimento)[:3]
    if cor_alvo == cor_preenchimento:
        return

    pilha = [(x, y)]
    while pilha:
        x, y = pilha.pop()
        if not (0 <= x < largura and 0 <= y < altura):
            continue
        if tuple(superficie.get_at((x, y)))[:3] != cor_alvo:
            continue
        setPixel(superficie, x, y, cor_preenchimento)
        pilha.append((x + 1, y))
        pilha.append((x - 1, y))
        pilha.append((x, y + 1))
        pilha.append((x, y - 1))


def boundary_fill(superficie, x, y, cor_preenchimento, cor_borda):
    """
    Boundary Fill: pinta a partir da semente até encontrar a cor da borda.
    """
    largura, altura = superficie.get_width(), superficie.get_height()
    cor_preenchimento = tuple(cor_preenchimento)[:3]
    cor_borda = tuple(cor_borda)[:3]

    pilha = [(int(x), int(y))]
    while pilha:
        x, y = pilha.pop()
        if not (0 <= x < largura and 0 <= y < altura):
            continue
        atual = tuple(superficie.get_at((x, y)))[:3]
        if atual == cor_borda or atual == cor_preenchimento:
            continue
        setPixel(superficie, x, y, cor_preenchimento)
        pilha.append((x + 1, y))
        pilha.append((x - 1, y))
        pilha.append((x, y + 1))
        pilha.append((x, y - 1))


# ============================================================
# SCANLINE COM GRADIENTE DE COR POR VÉRTICE
# ============================================================

def interpola_cor(c1, c2, t):
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return (max(0, min(r, 255)), max(0, min(g, 255)), max(0, min(b, 255)))


def scanline_fill_gradiente(superficie, pontos, cores):
    """
    Scanline com cor definida por vértice: a cor é interpolada ao longo das
    arestas (em y) e depois ao longo de cada span horizontal (em x).
    """
    if not pontos:
        return

    xmin, ymin, xmax, ymax = area_visivel(superficie)
    ys = [p[1] for p in pontos]
    y_min, y_max = int(min(ys)), int(max(ys))
    n = len(pontos)

    pixels = pygame.surfarray.pixels3d(superficie)
    for y in range(max(y_min, ymin), min(y_max, ymax + 1)):
        intersecoes = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]
            c0, c1 = cores[i], cores[(i + 1) % n]

            if y0 == y1:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                c0, c1 = c1, c0
            if y < y0 or y >= y1:
                continue

            t = (y - y0) / (y1 - y0)
            intersecoes.append((x0 + t * (x1 - x0), interpola_cor(c0, c1, t)))

        intersecoes.sort(key=lambda p: p[0])

        for i in range(0, len(intersecoes) - 1, 2):
            x_ini, cor_ini = intersecoes[i]
            x_fim, cor_fim = intersecoes[i + 1]
            if x_fim == x_ini:
                continue

            xs = np.arange(max(int(x_ini), xmin), min(int(x_fim), xmax) + 1)
            if xs.size == 0:
                continue

            if cor_ini == cor_fim:
                pixels[xs[0]:xs[-1] + 1, y] = cor_ini
                continue

            t = (xs - x_ini) / (x_fim - x_ini)
            c_ini, c_fim = np.array(cor_ini), np.array(cor_fim)
            span = c_ini + (c_fim - c_ini) * t[:, None]  # interpolação por pixel, vetorizada
            pixels[xs, y] = np.clip(span, 0, 255).astype(np.uint8)
    del pixels

import numpy as np
import pygame
from src.engine.rendering import scanline_texture

BACKGROUND = [
    "assets/pxos/Fases/Fase1_Noite.png",
    "assets/pxos/Fases/Fase2_Noite.png",
    "assets/pxos/Fases/Fase3_Noite.png",
    "assets/pxos/Fases/Fase4_Noite.png",
    "assets/pxos/Fases/Sub_Final.png",
    "assets/pxos/Fases/Fase_Final.png",
]

# (y_topo, y_base) da área jogável
ZONAS_JOGAVEIS = [
    (515, 750),  # fase 1
    (565, 750),  # fase 2
    (575, 730),  # fase 3
    (575, 750),  # fase 4 
    (585, 700),  # sub-final
    (612, 725),  # final
]

def carregar_matriz(caminho):
    return pygame.surfarray.array3d(pygame.image.load(caminho))  # (largura, altura, 3)

def escalar_matriz(matriz, nova_altura):
    w, h = matriz.shape[:2]
    escala = nova_altura / h
    nova_w = round(w * escala)
    xs = np.minimum(w - 1, (np.arange(nova_w) / escala).astype(int))
    ys = np.minimum(h - 1, (np.arange(nova_altura) / escala).astype(int))
    return matriz[np.ix_(xs, ys)], escala

def escurecer(tela, fator):
    """fator 1.0 = imagem normal, 0.0 = preto."""
    pixels = pygame.surfarray.pixels3d(tela)
    np.multiply(pixels, fator, out=pixels, casting="unsafe")
    del pixels

class Cenario:
    def __init__(self, indice, altura_tela):
        original = carregar_matriz(BACKGROUND[indice])  # (largura, altura, 3)
        w, h = original.shape[:2]
        escala = altura_tela / h
        self.largura = round(w * escala)

        destino = pygame.Surface((self.largura, altura_tela))  # buffer de pixels fora da tela
        quad = [(0, 0), (self.largura, 0), (self.largura, altura_tela), (0, altura_tela)]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        scanline_texture(destino, quad, uvs, original.transpose(1, 0, 2))
        self.matriz = pygame.surfarray.array3d(destino)

        topo, base = ZONAS_JOGAVEIS[indice]
        self.zona_topo = round(topo * escala)
        self.zona_base = round(base * escala)

    def desenhar(self, tela, offset_x, camera_x):
        x0 = int(camera_x - offset_x)
        ini = max(0, x0)
        fim = min(self.largura, x0 + tela.get_width())
        if ini >= fim:
            return
        pixels = pygame.surfarray.pixels3d(tela)
        pixels[ini - x0:fim - x0] = self.matriz[ini:fim]
        del pixels  # libera o lock da superfície
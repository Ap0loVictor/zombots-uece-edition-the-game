import math
import random
import pygame

from src.engine.rendering import bresenham, scanline_fill, desenhar_poligono
from src.engine.primitivas import circulo, elipse
from src.engine.fill import boundary_fill, scanline_fill_gradiente
from src.engine.clipping import desenhar_linha_recortada, desenhar_poligono_recortado
from src.engine.fonte import desenhar_texto_centralizado

PRETO = (10, 10, 10)
BRANCO = (240, 240, 240)
VERDE_ZUMBI = (95, 160, 80)
CINZA_METAL = (130, 140, 155)
VERMELHO = (230, 40, 40)
AMARELO_LUA = (235, 225, 150)


class Intro:
    """
    Tela de abertura. Camada estática (cacheada) + camada animada por frame.

    Algoritmos usados:
      - Reta: Bresenham (antena, boca, prédio, raios do scanner)
      - Circunferência: Ponto Médio (cabeça, olho robô, lua, crateras, luz)
      - Elipse: Ponto Médio (olho zumbi, parafusos, órbita)
      - Boundary Fill: preenche cabeça, olhos, lua, crateras, boca etc.
      - Scanline com gradiente por vértice: céu e chão
      - Scanline simples: prédio da UECE
      - Cohen-Sutherland: raios do scanner recortados na janela
    """

    CENTRO = (400, 320)       # centro da cabeça
    OLHO_ROBO = (445, 295)
    LUA = (665, 120)
    JANELA_SCANNER = (140, 190, 660, 470)  # xmin, ymin, xmax, ymax

    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height
        self.fundo = None
        self.tempo = 0.0

    def open(self):
        self.tempo = 0.0
        if self.fundo is None:
            self.fundo = pygame.Surface((self.w, self.h))
            self._montar_fundo(self.fundo)

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE
        ):
            return "skip"
        return None

    # ------------------------------------------------------------
    # Helper: contorno + flood fill a partir de uma semente
    # ------------------------------------------------------------
    def _circ_cheio(self, s, cx, cy, r, cor, borda=PRETO):
        circulo(s, cx, cy, r, borda)
        boundary_fill(s, cx, cy, cor, borda)

    def _elip_cheia(self, s, cx, cy, rx, ry, cor, borda=PRETO):
        elipse(s, cx, cy, rx, ry, borda)
        boundary_fill(s, cx, cy, cor, borda)

    # ------------------------------------------------------------
    # Camada estática
    # ------------------------------------------------------------
    def _montar_fundo(self, s):
        w, h = self.w, self.h
        horizonte = 400

        # Céu e chão: scanline com cor por vértice
        scanline_fill_gradiente(
            s, [(0, 0), (w, 0), (w, horizonte), (0, horizonte)],
            [(8, 4, 28), (8, 4, 28), (95, 35, 85), (95, 35, 85)],
        )
        scanline_fill_gradiente(
            s, [(0, horizonte), (w, horizonte), (w, h), (0, h)],
            [(35, 55, 40), (35, 55, 40), (8, 14, 10), (8, 14, 10)],
        )

        # Estrelas (pontos)
        rnd = random.Random(7)
        for _ in range(70):
            sx, sy = rnd.randint(0, w - 1), rnd.randint(0, 260)
            circulo(s, sx, sy, 0, (230, 230, 255))

        # Lua: círculo + flood fill, crateras com círculos
        lx, ly = self.LUA
        self._circ_cheio(s, lx, ly, 55, AMARELO_LUA, (200, 190, 110))
        for dx, dy, r in ((-18, -12, 11), (14, 10, 8), (-6, 24, 6)):
            self._circ_cheio(s, lx + dx, ly + dy, r, (200, 190, 120), (170, 160, 90))

        # Prédio da UECE ao fundo: polígono por scanline + janelas
        predio = [(40, horizonte), (40, 330), (90, 330), (90, 300), (230, 300),
                  (230, 330), (280, 330), (280, horizonte)]
        scanline_fill(s, predio, (28, 20, 45))
        desenhar_poligono(s, predio, (70, 50, 100))
        for jx in range(60, 270, 30):
            for jy in (345, 370):
                janela = [(jx, jy), (jx + 14, jy), (jx + 14, jy + 14), (jx, jy + 14)]
                scanline_fill(s, janela, (200, 170, 60))

        # Linha do horizonte
        bresenham(s, 0, horizonte, w, horizonte, (120, 160, 120))

        # ---- Cabeça Zombot ----
        cx, cy = self.CENTRO
        self._circ_cheio(s, cx, cy, 100, VERDE_ZUMBI)

        # Antena
        bresenham(s, cx, cy - 100, cx, cy - 150, PRETO)
        bresenham(s, cx + 1, cy - 100, cx + 1, cy - 150, PRETO)

        # Parafusos nas laterais (elipses)
        self._elip_cheia(s, cx - 108, cy + 5, 12, 22, CINZA_METAL)
        self._elip_cheia(s, cx + 108, cy + 5, 12, 22, CINZA_METAL)

        # Olho zumbi (elipse) à esquerda
        ex, ey = cx - 45, cy - 25
        self._elip_cheia(s, ex, ey, 28, 18, BRANCO)
        self._circ_cheio(s, ex + 4, ey, 8, VERMELHO)

        # Olho robô (círculo) à direita + placa metálica
        ox, oy = self.OLHO_ROBO
        self._circ_cheio(s, ox, oy, 26, CINZA_METAL)
        self._circ_cheio(s, ox, oy, 15, VERMELHO)

        # Rachadura (retas) na testa
        for (a, b) in (((cx - 20, cy - 98), (cx - 5, cy - 75)),
                       ((cx - 5, cy - 75), (cx - 18, cy - 62)),
                       ((cx - 18, cy - 62), (cx - 2, cy - 48))):
            bresenham(s, a[0], a[1], b[0], b[1], PRETO)

        # Boca em zigue-zague (polígono fechado por retas) + flood fill
        boca = [(cx - 55, cy + 40), (cx - 30, cy + 30), (cx - 5, cy + 42),
                (cx + 20, cy + 30), (cx + 55, cy + 42), (cx + 45, cy + 70),
                (cx + 15, cy + 78), (cx - 15, cy + 78), (cx - 45, cy + 70)]
        desenhar_poligono(s, boca, PRETO)
        boundary_fill(s, cx, cy + 58, (60, 10, 20), PRETO)
        for dente in range(-35, 40, 18):
            bresenham(s, cx + dente, cy + 50, cx + dente, cy + 60, BRANCO)

        # Título
        desenhar_texto_centralizado(s, "ZOMBOTS", w // 2, 55, (6, 6, 6), escala=9)
        desenhar_texto_centralizado(s, "ZOMBOTS", w // 2 - 3, 52, (120, 230, 120), escala=9)
        desenhar_texto_centralizado(s, "UECE EDITION", w // 2, 105, (220, 220, 240), escala=3)

    # ------------------------------------------------------------
    # Camada animada (a cada frame)
    # ------------------------------------------------------------
    def draw(self, tela, dt=0.0):
        self.tempo += dt
        t = self.tempo
        tela.blit(self.fundo, (0, 0))  # camada estática cacheada

        cx, cy = self.CENTRO

        # Luz da antena piscando (círculo + flood fill)
        ligada = int(t * 2) % 2 == 0
        luz = (255, 60, 60) if ligada else (90, 20, 20)
        circulo(tela, cx, cy - 158, 9, PRETO)
        boundary_fill(tela, cx, cy - 158, luz, PRETO)

        # Órbita elíptica ao redor da lua; o raio vertical "respira"
        lx, ly = self.LUA
        ry = 22 + 8 * math.sin(t * 1.5)
        elipse(tela, lx, ly, 110, ry, (150, 130, 190))
        ang = t * 1.8
        sx = lx + 110 * math.cos(ang)
        sy = ly + ry * math.sin(ang)
        circulo(tela, sx, sy, 7, PRETO)
        boundary_fill(tela, sx, sy, (210, 215, 235), PRETO)

        # Scanner: raios saindo do olho robô, recortados por Cohen-Sutherland
        xmin, ymin, xmax, ymax = self.JANELA_SCANNER
        ox, oy = self.OLHO_ROBO
        for k in range(5):
            a = t * 0.9 + k * (2 * math.pi / 5)
            fx = ox + 900 * math.cos(a)   # extremidade bem fora da janela
            fy = oy + 900 * math.sin(a)
            desenhar_linha_recortada(tela, ox, oy, fx, fy, self.JANELA_SCANNER, (255, 70, 70))
        moldura = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        desenhar_poligono_recortado(tela, moldura, (255, 220, 90), self.JANELA_SCANNER)

        # Texto piscando
        if int(t * 1.6) % 2 == 0:
            desenhar_texto_centralizado(tela, "PRESS ENTER", self.w // 2, self.h - 45,
                                        (255, 255, 255), escala=3)

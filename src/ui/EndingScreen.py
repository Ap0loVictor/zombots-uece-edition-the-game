import pygame
from src.engine.background import carregar_matriz, escurecer
from src.engine.rendering import scanline_texture
from src.engine.fonte import desenhar_texto_centralizado

FADE_OUT = 1.0
FADE_IN = 1.5

class EndingScreen:
    def __init__(self, width, height, caminho):
        original = carregar_matriz(caminho)  # (largura, altura, 3)
        w, h = original.shape[:2]
        altura_img = round(width * h / w)    # mantém a proporção (letterbox)
        y0 = (height - altura_img) // 2

        destino = pygame.Surface((width, height))
        quad = [(0, y0), (width, y0), (width, y0 + altura_img), (0, y0 + altura_img)]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        scanline_texture(destino, quad, uvs, original.transpose(1, 0, 2))
        self.imagem = pygame.surfarray.array3d(destino)
        self.ultimo_frame = None
        self.tempo = 0.0
        self.width, self.height = width, height

    def open(self, tela):
        self.ultimo_frame = pygame.surfarray.array3d(tela)  # congela a cena da derrota
        self.tempo = 0.0

    def handle_event(self, evento):
        if (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_ESCAPE)
                and self.tempo >= FADE_OUT + FADE_IN):
            return "back"

    def draw(self, tela, dt):
        self.tempo += dt
        fade_out = self.tempo < FADE_OUT
        pixels = pygame.surfarray.pixels3d(tela)
        pixels[:] = self.ultimo_frame if fade_out else self.imagem
        del pixels

        if fade_out:
            escurecer(tela, 1 - self.tempo / FADE_OUT)
        else:
            escurecer(tela, min(1.0, (self.tempo - FADE_OUT) / FADE_IN))
            if self.tempo >= FADE_OUT + FADE_IN and int(self.tempo * 3) % 2 == 0:
                desenhar_texto_centralizado(tela, "ENTER: VOLTAR AO MENU",
                                            self.width // 2, self.height - 25, (235, 235, 245), escala=2)
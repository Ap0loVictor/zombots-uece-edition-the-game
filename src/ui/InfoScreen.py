import pygame
from src.engine.rendering import desenhar_poligono, scanline_fill
from src.engine.fonte import desenhar_texto_centralizado


class InfoScreen:
    """
    Tela simples com título e linhas de texto (Controls, Credits, Settings).
    ESC ou ENTER devolve "back" para o main voltar ao menu.
    """

    def __init__(self, screen_width, screen_height, title, lines):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.lines = lines
        self.needs_redraw = True

    def open(self):
        self.needs_redraw = True

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER
        ):
            return "back"
        return None

    def draw(self, tela):
        # A tela é estática: desenha uma vez ao abrir e mantém no buffer
        if not self.needs_redraw:
            return
        self.needs_redraw = False

        fundo = [
            (0, 0),
            (self.screen_width - 1, 0),
            (self.screen_width - 1, self.screen_height - 1),
            (0, self.screen_height - 1)
        ]

        scanline_fill(tela, fundo, (15, 15, 28))

        cx = self.screen_width // 2
        desenhar_texto_centralizado(tela, self.title, cx, 80, (120, 230, 120), escala=5)

        # Moldura do conteúdo
        margem = 80
        moldura = [
            (margem, 140),
            (self.screen_width - margem, 140),
            (self.screen_width - margem, self.screen_height - 100),
            (margem, self.screen_height - 100),
        ]
        desenhar_poligono(tela, moldura, (120, 150, 200))

        for i, line in enumerate(self.lines):
            desenhar_texto_centralizado(tela, line, cx, 185 + i * 36, (220, 220, 235), escala=2)

        desenhar_texto_centralizado(
            tela, "ESC: VOLTAR", cx, self.screen_height - 50, (130, 130, 160), escala=2
        )

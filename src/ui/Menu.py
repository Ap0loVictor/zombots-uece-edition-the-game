import pygame
from src.ui.Button import Button
from src.engine.fonte import desenhar_texto_centralizado

OPTIONS = [
    ("START", "start"),
    ("CONTROLS", "controls"),
    ("CREDITS", "credits"),
    ("SETTINGS", "settings"),
    ("EXIT", "exit"),
]


class Menu:
    """
    Menu principal: navega entre os botões com as setas e devolve a ação
    do botão escolhido com ENTER. Não conhece nada do jogo em si.
    """

    def __init__(self, screen_width, screen_height,
                 button_width=260, button_height=44, gap=14, top=200):
        self.screen_width = screen_width
        self.screen_height = screen_height

        x = (screen_width - button_width) // 2
        self.buttons = [
            Button(x, top + i * (button_height + gap), button_width, button_height, text, action)
            for i, (text, action) in enumerate(OPTIONS)
        ]

        self.index = 0
        self._update_selection()

    def open(self):
        """
        Chamado ao entrar no menu: força o redesenho da tela inteira.
        """
        self.needs_redraw = True

    def _update_selection(self):
        for i, button in enumerate(self.buttons):
            button.selected = (i == self.index)
        # Desenhar com setPixel é caro, então a tela só é refeita quando algo muda
        self.needs_redraw = True

    def handle_event(self, evento):
        """
        Retorna a ação do botão ativado (ex.: "start") ou None.
        """
        if evento.type != pygame.KEYDOWN:
            return None

        if evento.key == pygame.K_UP:
            self.index = (self.index - 1) % len(self.buttons)
            self._update_selection()
        elif evento.key == pygame.K_DOWN:
            self.index = (self.index + 1) % len(self.buttons)
            self._update_selection()
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return self.buttons[self.index].action

        return None

    def draw(self, tela):
        if not self.needs_redraw:
            return
        self.needs_redraw = False

        tela.fill((15, 15, 28))

        cx = self.screen_width // 2
        desenhar_texto_centralizado(tela, "ZOMBOTS", cx, 95, (120, 230, 120), escala=8)
        desenhar_texto_centralizado(tela, "UECE EDITION", cx, 150, (200, 200, 220), escala=2)

        for button in self.buttons:
            button.draw(tela)

        desenhar_texto_centralizado(
            tela, "SETAS: NAVEGAR   ENTER: SELECIONAR",
            cx, self.screen_height - 40, (130, 130, 160), escala=2
        )

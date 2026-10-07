import pygame
from assets.sprites.PixelSprite import PixelSprite
from src.engine.sprite import draw_sprite_scaled
from src.engine.fonte import desenhar_texto_centralizado
from src.engine.rendering import scanline_fill


PERSONAGENS = [
    ("apolo", "APOLO", "assets/pxos/Apolo_Sprites/apolo_idle_32x64.png"),
    ("jannsen", "JANNSEN", "assets/pxos/Jannsen_Sprites/jan_idle_32x64.png"),
    ("marques", "MARQUES", "assets/pxos/Marques_Sprites/marques_idle_32x64.png"),
]

class CharacterSelect:
    """Tela de seleção: setas esquerda/direita trocam o personagem, ENTER confirma."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.index = 0
        self.previews = [PixelSprite(path) for _, _, path in PERSONAGENS]
        self.needs_redraw = True

    def open(self):
        self.index = 0
        self.needs_redraw = True

    def handle_event(self, evento):
        if evento.type != pygame.KEYDOWN:
            return None

        if evento.key == pygame.K_LEFT:
            self.index = (self.index - 1) % len(PERSONAGENS)
            self.needs_redraw = True
        elif evento.key == pygame.K_RIGHT:
            self.index = (self.index + 1) % len(PERSONAGENS)
            self.needs_redraw = True
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return PERSONAGENS[self.index][0]
        elif evento.key == pygame.K_ESCAPE:
            return "voltar"

        return None

    def draw(self, tela):
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

        desenhar_texto_centralizado(tela, "ESCOLHA SEU PERSONAGEM", cx, 60, (120, 230, 120), escala=3)

        personagem_id, nome, _ = PERSONAGENS[self.index]
        preview = self.previews[self.index]
        altura_preview = 192
        largura_preview = preview.width * altura_preview // preview.height
        pos_x = cx - largura_preview // 2
        pos_y = self.screen_height // 2 - altura_preview // 2
        draw_sprite_scaled(tela, preview.matrix, pos_x, pos_y, altura_preview)

        desenhar_texto_centralizado(tela, nome, cx, pos_y + altura_preview + 30, (255, 255, 255), escala=4)
        desenhar_texto_centralizado(
            tela, "<-   ->   ENTER: CONFIRMAR",
            cx, self.screen_height - 40, (130, 130, 160), escala=2
        )
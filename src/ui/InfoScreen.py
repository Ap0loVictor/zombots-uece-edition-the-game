import pygame
from src.engine.rendering import desenhar_poligono, scanline_fill
from src.engine.fonte import desenhar_texto_centralizado, desenhar_texto, largura_texto, altura_texto

def quebrar_linhas(texto, largura_maxima, escala):
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        teste = f"{linha_atual} {palavra}".strip()

        if largura_texto(teste, escala) <= largura_maxima:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas

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
        self.scroll_y = 0
        self.linhas_quebradas = []

    def open(self):
        self.needs_redraw = True

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                return "back"
            if evento.key == pygame.K_DOWN:
                self.scroll_y += 30
                self.needs_redraw = True
            elif evento.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 30)
                self.needs_redraw = True
            elif evento.key == pygame.K_PAGEDOWN:
                self.scroll_y += 150
                self.needs_redraw = True
            elif evento.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - 150)
                self.needs_redraw = True
        elif evento.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, self.scroll_y - evento.y * 30)
            self.needs_redraw = True
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

        escala_texto = 2
        margem_texto = 16
        largura_maxima = self.screen_width - 2 * (80 + margem_texto)
        altura_linha = altura_texto(escala_texto) + 12

        topo = 155
        base = self.screen_height - 115
        altura_area = base - topo

        linhas = []
        for paragrafo in self.lines:
            linhas.extend(quebrar_linhas(paragrafo, largura_maxima, escala_texto))
            linhas.append("")

        if linhas:
            linhas.pop()

        altura_conteudo = len(linhas) * altura_linha
        scroll_max = max(0, altura_conteudo - altura_area)

        self.scroll_y = max(0, min(self.scroll_y, scroll_max))

        for i, linha in enumerate(linhas):
            y = topo + i * altura_linha - self.scroll_y

            if y + altura_texto(escala_texto) < topo or y > base:
                continue
            desenhar_texto(tela,linha,80 + margem_texto,y,(220, 220, 235),escala=escala_texto,)

        if scroll_max > 0:
            desenhar_texto_centralizado(tela,"V PARA BAIXO",self.screen_width // 2,base - 12,(130, 160, 200),escala=1,)

        desenhar_texto_centralizado(tela, "ESC: VOLTAR", cx, self.screen_height - 50, (130, 130, 160), escala=2)

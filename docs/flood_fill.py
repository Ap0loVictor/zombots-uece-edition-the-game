import pygame
import sys
sys.setrecursionlimit(10000)

pygame.init()
largura, altura = 500, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Flood Fill com Bresenham")

def setPixel(superficie, x, y, cor):
    if 0 <= x < superficie.get_width() and 0 <= y < superficie.get_height():
        superficie.set_at((x, y), cor)

# =========================
# Bresenham clássico (retas)
# =========================
def bresenham(superficie, x0, y0, x1, y1, cor):
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    ystep = 1 if dy >= 0 else -1
    dy = abs(dy)

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    y = y0
    for x in range(x0, x1 + 1):
        if steep:
            setPixel(superficie, y, x, cor)
        else:
            setPixel(superficie, x, y, cor)

        if d > 0:
            y += ystep
            d += incNE
        else:
            d += incE

# =========================
# Desenho do polígono
# =========================
def desenhar_poligono(superficie, pontos, cor):
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        bresenham(superficie, x0, y0, x1, y1, cor)

# =========================
# Flood Fill (4-conectado)
# =========================
def flood_fill_iterativo(superficie, x, y, cor_preenchimento, cor_borda):
    largura = superficie.get_width()
    altura = superficie.get_height()

    pilha = [(x, y)]

    while pilha:
        x, y = pilha.pop()

        if not (0 <= x < largura and 0 <= y < altura):
            continue

        cor_atual = superficie.get_at((x, y))[:3]

        if cor_atual == cor_borda or cor_atual == cor_preenchimento:
            continue

        setPixel(superficie, x, y, cor_preenchimento)

        pilha.append((x + 1, y))
        pilha.append((x - 1, y))
        pilha.append((x, y + 1))
        pilha.append((x, y - 1))

# =========================
# Loop principal
# =========================
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))

    # Polígono (qualquer formato fechado)
    poligono = [(100, 100), (400, 120), (350, 300), (150, 280)]

    cor_borda = (255, 255, 255)
    cor_preenchimento = (0, 255, 0)

    desenhar_poligono(tela, poligono, cor_borda)

    # Executa o flood fill apenas uma vez
    
    flood_fill_iterativo(tela, 250, 200, cor_preenchimento, cor_borda)

    pygame.display.flip()

pygame.quit()
sys.exit()

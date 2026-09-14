import pygame
import sys

pygame.init()
largura, altura = 500, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Algoritmo DDA - Comparação de Retas")

def setPixel(superficie, x, y, cor):
    if 0 <= x < superficie.get_width() and 0 <= y < superficie.get_height():
        superficie.set_at((int(x), int(y)), cor)

def dda(superficie, x0, y0, x1, y1, cor):
    dx = x1 - x0
    dy = y1 - y0

    passos = max(abs(dx), abs(dy))

    if passos == 0:
        setPixel(superficie, x0, y0, cor)
        return

    x_inc = dx / passos
    y_inc = dy / passos

    x = x0
    y = y0

    for _ in range(passos + 1):
        setPixel(superficie, round(x), round(y), cor)
        x += x_inc
        y += y_inc

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))

    # Reta horizontal
    dda(tela, 50, 50, 450, 50, (255, 0, 0))

    # Reta vertical
    dda(tela, 100, 50, 100, 350, (0, 255, 0))

    # Pouco inclinada para cima
    dda(tela, 50, 300, 450, 250, (0, 0, 255))

    # Muito inclinada para cima
    dda(tela, 200, 350, 250, 50, (255, 255, 0))

    # Pouco inclinada para baixo
    dda(tela, 50, 100, 450, 150, (255, 0, 255))

    # Muito inclinada para baixo
    dda(tela, 350, 50, 300, 350, (0, 255, 255))

    pygame.display.flip()

pygame.quit()
sys.exit()
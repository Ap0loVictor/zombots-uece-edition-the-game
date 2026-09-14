import pygame
import sys

pygame.init()
largura, altura = 500, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Reta Ingênua - Buracos Visíveis")

def setPixel(superficie, x, y, cor):
    if 0 <= x < superficie.get_width() and 0 <= y < superficie.get_height():
        superficie.set_at((int(x), int(y)), cor)

def reta_ingenua(superficie, x0, y0, x1, y1, cor):
    # Garantir x crescente
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0

    # Evita divisão por zero (reta vertical não é tratada aqui)
    if dx == 0:
        return

    m = (y1 - y0) / dx
    b = y0 - m * x0

    for x in range(x0, x1 + 1):
        y = m * x + b
        setPixel(superficie, x, round(y), cor)

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))

    # Pouco inclinada (quase contínua)
    reta_ingenua(tela, 50, 300, 450, 250, (0, 255, 0))

    # Média inclinação
    reta_ingenua(tela, 50, 350, 300, 100, (255, 255, 0))

    # Muito inclinada (buracos bem visíveis)
    reta_ingenua(tela, 200, 350, 260, 50, (255, 255, 255))

    pygame.display.flip()

pygame.quit()
sys.exit()
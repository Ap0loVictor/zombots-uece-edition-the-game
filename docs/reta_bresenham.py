import pygame
import sys

pygame.init()
largura, altura = 500, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Bresenham Clássico - Todos os Casos")

def setPixel(superficie, x, y, cor):
    if 0 <= x < superficie.get_width() and 0 <= y < superficie.get_height():
        superficie.set_at((x, y), cor)

def bresenham(superficie, x0, y0, x1, y1, cor):
    # Flags para transformações
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    ystep = 1
    if dy < 0:
        ystep = -1
        dy = -dy

    # Bresenham clássico
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    x = x0
    y = y0

    while x <= x1:
        if steep:
            setPixel(superficie, y, x, cor)
        else:
            setPixel(superficie, x, y, cor)

        if d <= 0:
            d += incE
        else:
            d += incNE
            y += ystep

        x += 1

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))

    # Horizontal
    bresenham(tela, 50, 50, 450, 50, (255, 0, 0))

    # Vertical
    bresenham(tela, 100, 50, 100, 350, (0, 255, 0))

    # Pouco inclinada para cima
    bresenham(tela, 50, 300, 450, 250, (0, 0, 255))

    # Muito inclinada para cima
    bresenham(tela, 200, 350, 250, 50, (255, 255, 0))

    # Pouco inclinada para baixo
    bresenham(tela, 50, 100, 450, 150, (255, 0, 255))

    # Muito inclinada para baixo
    bresenham(tela, 350, 50, 300, 350, (0, 255, 255))

    pygame.display.flip()

pygame.quit()
sys.exit()
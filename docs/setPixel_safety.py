import pygame 
import sys

pygame.init()
largura, altura = 400, 300
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Set Pixel")

def setPixel(superficie, x, y, cor):
    if 0 <= x < superficie.get_width() and 0 <= y < superficie.get_height():
        superficie.set_at((x, y), cor)
    
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = false
            
    tela.fill((0, 0, 0))
    setPixel(tela, 200, 150, (255, 255, 255))
    pygame.display.flip()

pygame.quit()
sys.exit()
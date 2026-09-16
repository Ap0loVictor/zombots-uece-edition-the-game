# No engine vão ficar as funções do cientista ent vou testar essa por enquanto
def testeeee():
    print("testado com sucesso")

def setPixel(superficie, x, y, cor):
    superficie.set_at((x, y), cor)
    
def rodar_jogo():
    import pygame 

    pygame.init()
    largura, altura = 400, 300
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Set Pixel")

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                
        tela.fill((0, 0, 0))
        setPixel(tela, 200, 150, (255, 255, 255))
        pygame.display.flip()

    pygame.quit()
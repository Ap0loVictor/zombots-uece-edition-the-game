import pygame
from src.game.entities.Player import Player
from src.game.entities.Rock import Rock
from src.engine.rendering import desenhar_poligono, scanline_fill
from src.mechanics.Physics import check_aabb_collision

def testeeee():
    print("so pra ver se roda")


def rodar_jogo():
    pygame.init()
    largura, altura = 800, 600
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Zombots")
    relogio = pygame.time.Clock()

    # Limites do mundo (min_x, min_y, max_x, max_y).
    # Cima, baixo e esquerda são paredes fechadas; a direita fica como None
    # (borda aberta), porque é por ali que o mapa vai se estender nas
    # próximas fases do beat 'em up.
    limites = (0, 0, None, altura)

    player = Player(start_x=largura // 2, start_y=altura // 2)
    pedra = Rock(200, 300)

    rodando = True
    while rodando and player.alive:
        dt = relogio.tick(60) / 1000.0  # Delta time em segundos

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # Atualiza a entidade Player com os inputs do teclado
        keys = pygame.key.get_pressed()
        player.update(dt, keys, solid_entities=[pedra], bounds=limites)

        # Fundo da tela
        tela.fill((30, 30, 45))

        # Renderização da Pedra
        for part in pedra.get_polygons():
            scanline_fill(tela, part["vertices"], part["color"])
            desenhar_poligono(tela, part["vertices"], part["color"])
        
        # Teste de colisão tirando vida
        if check_aabb_collision(player.x,player.y,player.width,player.height,pedra.x,pedra.y,pedra.width,pedra.height):
            player.receive_damage(pedra.damage)
            print("Vida:", player.health)
            if player.alive == False:
                print("Voce morreu, seu nooob")

        # Renderização das partes poligonais do Player com matemática pura (Bresenham/Scanline)
        for part in player.get_polygons():
            # Preenchimento (Algoritmo do docs)
            scanline_fill(tela, part["vertices"], part["color"])
            
            # Contorno da borda (Algoritmo do docs)
            desenhar_poligono(tela, part["vertices"], part["color"])

        pygame.display.flip()

    pygame.quit()

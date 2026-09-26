import pygame
from src.game.entities.Player import Player
from src.game.props.Rock import Rock
from src.game.props.Torn import Torn
from src.game.entities.Enemy import Enemy
from src.engine.rendering import desenhar_poligono, scanline_fill
from src.game.mechanics.Physics import check_aabb_collision, get_world_hitbox

def renderize_beings(beings, tela):
    for i in range(len(beings)):
        for being in beings[i].get_polygons():
            scanline_fill(tela, being["vertices"], being["color"]) # Preenchimento  
            desenhar_poligono(tela, being["vertices"], being["color"]) # Contorno da borda 

def runGame():
    pygame.init()
    width, height = 800, 600
    tela = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Zombots")
    clock = pygame.time.Clock()

    limits = (0, 0, None, height)

    player = Player(start_x=width // 2, start_y=height // 2)
    rock = Rock(200, 300)
    torn = Torn(400, 200)

    zombie = Enemy(start_x=20, start_y=100, enemy_type="zombie", damage=34)
    robot = Enemy(start_x=width, start_y=100, enemy_type="robot", damage=34)

    props = [rock, torn]
    enemies = [zombie, robot]
    entities = [player] + enemies
    things = props + entities

    running = True

    while running and player.alive:
        dt = clock.tick(60) / 1000.0  # Delta time em segundos

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

        for enemy in enemies:
            others = [rock] + [i for i in enemies if i is not enemy]
            enemy.update(dt, target=player.get_position(), solid_entities=others, bounds=limits)

        keys = pygame.key.get_pressed() # Atualiza a entidade Player com os inputs do teclado

        # Novo
        player.update(dt=dt, keys=keys, solid_entities=[rock] + enemies, bounds=limits)

        # Fundo da tela
        tela.fill((30, 30, 45))

        renderize_beings(things, tela=tela)

        player_box = get_world_hitbox(player)

        for enemy in enemies:
            if enemy.alive:
                enemy_box = get_world_hitbox(enemy)
                if check_aabb_collision(*player_box, *enemy_box):
                    player.receive_damage(enemy.damage) 
                    print("Vida:", player.health)

        player_box = get_world_hitbox(player)
        rock_box = get_world_hitbox(rock)
        torn_box = get_world_hitbox(torn)

        if check_aabb_collision(*player_box,*rock_box):
            player.receive_damage(rock.damage)
            print("Health:", player.health)
        
        if check_aabb_collision(*player_box,*torn_box):
            player.receive_damage(torn.damage)
            print("Health:", player.health)

        if not player.alive:
            print("Voce morreu, seu nooob")

        # FUNÇÃO PARA VER HITBOXES, APAGAR ANTES DE BOTAR NO ORIGINAL PQ NÃO PODEMOS USAR FUNÇÕES DO PYGAME 
        
        # pygame.draw.rect(tela,(255, 0, 0),(player.x + player.hitbox[0],player.y + player.hitbox[1],player.hitbox[2],player.hitbox[3]),2)
        # pygame.draw.rect(tela,(0, 255, 0),(rock.x + rock.hitbox[0],rock.y + rock.hitbox[1],rock.hitbox[2],rock.hitbox[3]),2)
        # pygame.draw.rect(tela,(0, 0, 0),(enemies[0].x + enemies[0].hitbox[0],enemies[0].y + enemies[0].hitbox[1],enemies[0].hitbox[2],enemies[0].hitbox[3]),2)
        # pygame.draw.rect(tela,(0, 0, 0),(enemies[1].x + enemies[1].hitbox[0],enemies[1].y + enemies[1].hitbox[1],enemies[1].hitbox[2],enemies[1].hitbox[3]),2)
        
        pygame.display.flip()

    pygame.quit()

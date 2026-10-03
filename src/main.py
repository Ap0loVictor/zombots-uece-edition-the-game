import pygame
from src.game.entities.Player import Player
from src.game.props.Rock import Rock
from src.game.props.Torn import Torn
from src.game.entities.Enemy import Enemy
from src.game.entities.Box import Box

from src.engine.sprite import draw_sprite_scaled
from src.engine.rendering import desenhar_poligono, scanline_fill, desenhar_minimapa
from src.game.mechanics.Physics import check_aabb_collision, get_world_hitbox

from src.ui.Menu import Menu
from src.ui.InfoScreen import InfoScreen
from src.engine.fonte import desenhar_texto_centralizado

def renderizeBeings(beings, tela):
    for being in beings:        
        if hasattr(being, "sprite") and hasattr(being.sprite, "matrix"):
            draw_sprite_scaled(tela,being.sprite.matrix,int(being.x),int(being.y), being.height)
        else:
            for polygon in being.get_polygons():
                scanline_fill(tela, polygon["vertices"], polygon["color"]) # Preenchimento  
                desenhar_poligono(tela, polygon["vertices"], polygon["color"]) # Contorno da borda 

def removeBeing(beings, object, condition, message):
    if object in beings:
        if not condition:
            print(message)
            beings.remove(object)
    return beings

# Testar depois, não apagar - Apolo
# Essas funções não são as mesmas.

def removeBeings(beings):
    for object in beings:
        if not object.alive:
            beings.remove(object)
    return beings

def updateBeing(entities):
    pass # Acho que não vai dar pra fazer esse.

def nova_partida(width, height):
    # Cria todos os objetos do zero, para cada START começar uma partida limpa
    player = Player(start_x=width // 2, start_y=height // 2)
    rock = Rock(200, 300)
    torn = Torn(400, 200)
    box1 = Box(600, 500)

    zombie = Enemy(start_x=20, start_y=100, enemy_type="zombie", damage=34)
    robot = Enemy(start_x=width, start_y=100, enemy_type="robot", damage=34)

    props = [rock, torn]
    boxes = [box1]
    enemies = [zombie, robot]
    entities = [player] + boxes + enemies

    return {
        "player": player,
        "rock": rock,
        "torn": torn,
        "box1": box1,
        "enemies": enemies,
        "things": props + entities,
        "limits": (0, 0, None, height),
        "janela_mundo": (0, 0, width, height),
        "viewport_minimapa": (600, 20, 780, 160),
    }

def atualizar_partida(partida, tela, dt, keys):
    player = partida["player"]
    rock = partida["rock"]
    torn = partida["torn"]
    box1 = partida["box1"]
    enemies = partida["enemies"]
    things = partida["things"]
    limits = partida["limits"]

    for enemy in enemies:
        others = [rock] + [i for i in enemies if i is not enemy]  # sem o player aqui
        enemy.update(dt, target=player.get_position(), solid_entities=others, bounds=limits)

    player.update(dt=dt, keys=keys, solid_entities=[rock] + enemies, bounds=limits)

    tela.fill((30, 30, 45))

    renderizeBeings(things, tela=tela)

    player_box = get_world_hitbox(player)

    for enemy in enemies:
        if enemy.alive:
            enemy_box = get_world_hitbox(enemy)
            if check_aabb_collision(*player_box, *enemy_box):
                if player.receive_damage(enemy.damage):
                    force = 200
                    dx = enemy.x - player.x
                    dy = enemy.y - player.y
                    dist = max(1, (dx**2 + dy**2) ** 0.5)
                    enemy.apply_knockback((dx / dist) * force, (dy / dist) * force)

    player_box = get_world_hitbox(player)
    torn_box = get_world_hitbox(torn)
    box_box = get_world_hitbox(box1)

    if check_aabb_collision(*player_box,*torn_box):
        player.receive_damage(torn.damage)

    if check_aabb_collision(*player_box,*box_box):
        box1.receive_damage(player.damage)

    if player.is_attacking and not player.has_hit:
        attack_box = player.get_attack_hitbox()

        for enemy in enemies:
            if enemy.alive:
                enemy_box = get_world_hitbox(enemy)
                if check_aabb_collision(*attack_box, *enemy_box):
                    enemy.receive_damage(player.damage)
                    player.has_hit = True

                    force = 300
                    kx, ky = {
                        "left": (-force, 0), "right": (force, 0),
                        "up": (0, -force), "down": (0, force)
                    }[player.direction]
                    print("inimigo Atigindo")
                    enemy.apply_knockback(kx, ky)

        if box1.alive:
            box_box = get_world_hitbox(box1)
            if check_aabb_collision(*attack_box, *box_box):
                box1.receive_damage(player.damage)
                player.has_hit = True

    # Fazendo um teste de remoção
    removeBeing(object=rock, beings=things, condition=player.alive, message="Voce morreu")
    removeBeing(object=box1, beings=things, condition=box1.alive, message="Quebraste a caixa")
    # entities = removeBeings(entities)

    # PARA VER HITBOXES, APAGAR ANTES DE BOTAR NO ORIGINAL PQ NÃO PODEMOS USAR FUNÇÕES DO PYGAME
    # for thing in things:
    #     pygame.draw.rect(tela,(0, 0, 0),(thing.x + thing.hitbox[0],thing.y + thing.hitbox[1],thing.hitbox[2],thing.hitbox[3]),2)

    # Minimapa
    desenhar_minimapa(tela, things, partida["janela_mundo"], partida["viewport_minimapa"],
                       cor_fundo=(10, 10, 20), cor_borda=(255, 255, 255))

def runGame():
    pygame.init()
    width, height = 800, 600
    tela = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Zombots")
    clock = pygame.time.Clock()

    menu = Menu(width, height)
    telas_info = {
        "controls": InfoScreen(width, height, "CONTROLS", [
            "W A S D / SETAS: MOVER",
            "SPACE: ATACAR",
            "P: PAUSAR",
            "ESC: VOLTAR AO MENU",
        ]),
        "credits": InfoScreen(width, height, "CREDITS", [
            "GABRIEL MARQUES",
            "DAVI JANNSEN",
            "APOLO",
            "",
            "COMPUTACAO GRAFICA - UECE",
        ]),
        "settings": InfoScreen(width, height, "SETTINGS", [
            "EM BREVE",
        ]),
    }

    # Estados possíveis: "menu", "playing", "paused", "controls", "credits", "settings"
    estado = "menu"
    menu.open()
    partida = None

    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time em segundos

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

            elif estado == "menu":
                acao = menu.handle_event(evento)
                if acao == "start":
                    partida = nova_partida(width, height)
                    estado = "playing"
                elif acao == "exit":
                    running = False
                elif acao in telas_info:
                    estado = acao
                    telas_info[estado].open()

            elif estado == "playing":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    partida["player"].start_attack()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado = "menu"
                    menu.open()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                    estado = "paused"
                    # Desenhado uma vez só: o frame congelado fica no buffer e o
                    # tela.fill de atualizar_partida() apaga o texto ao despausar
                    desenhar_texto_centralizado(tela, "PAUSED", width // 2, height // 2,
                                                (255, 255, 255), escala=6)

            elif estado == "paused":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                    estado = "playing"

            elif estado in telas_info:
                if telas_info[estado].handle_event(evento) == "back":
                    estado = "menu"
                    menu.open()

        if estado == "menu":
            menu.draw(tela)
        elif estado == "playing":
            keys = pygame.key.get_pressed() # Atualiza a entidade Player com os inputs do teclado
            atualizar_partida(partida, tela, dt, keys)
        elif estado in telas_info:
            telas_info[estado].draw(tela)

        tela.fill((30, 30, 45))
        
        renderizeBeings(things, tela=tela)

        player_box = get_world_hitbox(player)

        for enemy in enemies:
            if enemy.alive:
                enemy_box = get_world_hitbox(enemy)
                if check_aabb_collision(*player_box, *enemy_box):
                    if player.receive_damage(enemy.damage):
                        force = 200
                        dx = enemy.x - player.x
                        dy = enemy.y - player.y
                        dist = max(1, (dx**2 + dy**2) ** 0.5)
                        enemy.apply_knockback((dx / dist) * force, (dy / dist) * force)

        player_box = get_world_hitbox(player)
        torn_box = get_world_hitbox(torn)
        box_box = get_world_hitbox(box1)

        if check_aabb_collision(*player_box,*torn_box):
            player.receive_damage(torn.damage)
        
        if check_aabb_collision(*player_box,*box_box):
            box1.receive_damage(player.damage)

        if player.is_attacking and not player.has_hit:
            attack_box = player.get_attack_hitbox()

            for enemy in enemies:
                if enemy.alive:
                    enemy_box = get_world_hitbox(enemy)
                    if check_aabb_collision(*attack_box, *enemy_box):
                        enemy.receive_damage(player.damage)
                        player.has_hit = True

                        force = 300
                        kx, ky = {
                            "left": (-force, 0), "right": (force, 0),
                            "up": (0, -force), "down": (0, force)
                        }[player.direction]
                        print("inimigo Atigindo")
                        enemy.apply_knockback(kx, ky)

            if box1.alive:
                box_box = get_world_hitbox(box1)
                if check_aabb_collision(*attack_box, *box_box):
                    box1.receive_damage(player.damage)
                    player.has_hit = True

        # Fazendo um teste de remoção
        things = removeBeing(object=rock, beings= things, condition=player.alive, message="Voce morreu")
        
        boxes = removeBeing(object=box1, beings=things, condition=box1.alive, message="Quebraste a caixa")
        # entities = removeBeings(entities)

        # PARA VER HITBOXES, APAGAR ANTES DE BOTAR NO ORIGINAL PQ NÃO PODEMOS USAR FUNÇÕES DO PYGAME 
        for thing in things:
            pygame.draw.rect(tela,(0, 0, 0),(thing.x + thing.hitbox[0],thing.y + thing.hitbox[1],thing.hitbox[2],thing.hitbox[3]),2)
        
        # Minimapa
        desenhar_minimapa(tela, things, janela_mundo, viewport_minimapa,
                           cor_fundo=(10, 10, 20), cor_borda=(255, 255, 255))

        pygame.display.flip()

    pygame.quit()

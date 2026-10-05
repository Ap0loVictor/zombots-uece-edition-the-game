import pygame
import math
from src.game.entities.Player import Player
from src.game.props.Rock import Rock
from src.game.props.Torn import Torn
from src.game.entities.Enemy import Enemy,SubBoss, FinalBoss
from src.game.entities.Box import Box

from src.engine.sprite import draw_sprite_scaled
from src.engine.rendering import desenhar_poligono, scanline_fill, desenhar_minimapa
from src.game.mechanics.Physics import check_aabb_collision, get_world_hitbox

from src.ui.Menu import Menu
from src.ui.InfoScreen import InfoScreen
from src.ui.Intro import Intro
from src.engine.fonte import desenhar_texto_centralizado

def renderizeBeings(beings, tela, camera_x=0):
    for being in beings:

        if hasattr(being, "sprite") and hasattr(being.sprite, "matrix"):
            espelhar = getattr(being, "flip_x", False)
            draw_sprite_scaled(tela, being.sprite.matrix, int(being.x - camera_x), int(being.y),
                                being.height, flip_x=espelhar)
        else:
            for polygon in being.get_polygons():
                vertices_tela = [(vx - camera_x, vy) for vx, vy in polygon["vertices"]]
                scanline_fill(tela, vertices_tela, polygon["color"])
                desenhar_poligono(tela, vertices_tela, polygon["color"]) # Contorno da borda 

def removeBeing(beings, object, condition, message):
    if object in beings:
        if not condition:
            print(message)
            beings.remove(object)
    return beings

# Testar depois, não apagar - Apolo
# Essas funções não são as mesmas.

def removeBeings(beings):
   return [being for being in beings if getattr(being, "alive", True)]

def updateBeing(entities):
    pass # Acho que não vai dar pra fazer esse.

def fase_0(offset_x, width, height):
    return [
        Enemy(start_x=offset_x + 20, start_y=100, enemy_type="zombie", damage=5),
        Enemy(start_x=offset_x + width - 20, start_y=100, enemy_type="robot", damage=5),
    ]

def fase_1(offset_x, width, height):
    return [
        Enemy(start_x=offset_x + 20, start_y=150, enemy_type="zombie", damage=5),
        Enemy(start_x=offset_x + width - 20, start_y=150, enemy_type="robot", damage=5),
    ]

def fase_2(offset_x, width, height):
    return [
        Enemy(start_x=offset_x + 20, start_y=200, enemy_type="zombie", damage=5),
        Enemy(start_x=offset_x + width - 20, start_y=200, enemy_type="robot", damage=5),
        Enemy(start_x=offset_x + width // 2, start_y=100, enemy_type="zombie", damage=5),
    ]

def fase_3(offset_x, width, height):
    return [
        Enemy(start_x=offset_x + 20, start_y=250, enemy_type="zombie", damage=5),
        Enemy(start_x=offset_x + width - 20, start_y=250, enemy_type="robot", damage=5),
        Enemy(start_x=offset_x + width // 2, start_y=150, enemy_type="robot", damage=5),
    ]

def fase_4(offset_x, width, height):
    return [SubBoss(start_x=offset_x + width // 2, start_y=50)]

def fase_5(offset_x, width, height):
    return [FinalBoss(start_x=offset_x + width // 2, start_y=50)]

LARGURA_FASE = 900
FASES = [fase_0, fase_1, fase_2, fase_3, fase_4, fase_5]

def spawnar_fase(indice_fase, width, height):
    if indice_fase < len(FASES):
        offset_x = indice_fase * LARGURA_FASE
        return FASES[indice_fase](offset_x, width, height)
    return []  # não há mais fases -> vitória

def nova_partida(width, height):
    player = Player(start_x=50, start_y=height // 2)
    rock = Rock(200, 300)
    torn = Torn(400, 200)
    box1 = Box(600, 500)

    fase_atual = 0
    enemies = spawnar_fase(fase_atual, width, height)

    props = [rock, torn]
    boxes = [box1]
    entities = [player] + boxes + enemies

    return {
        "player": player,
        "rock": rock,
        "torn": torn,
        "box1": box1,
        "enemies": enemies,
        "things": props + entities,
        "fase_atual": fase_atual,
        "width": width,
        "height": height,
        "limite_esquerdo": 0,  # avança e nunca mais recua
        "largura_mundo": LARGURA_FASE * len(FASES),
        "viewport_minimapa": (600, 20, 780, 160),
        "vitoria": False,
        "aguardando_transicao": False,
        "tempo_transicao": 0.0,
    }

def atualizar_partida(partida, tela, dt, keys):
    player = partida["player"]
    rock = partida["rock"]
    torn = partida["torn"]
    box1 = partida["box1"]
    enemies = partida["enemies"]
    things = partida["things"]
    limits = (partida["limite_esquerdo"], 0, partida["largura_mundo"], partida["height"])

    for enemy in enemies:
        others = [rock] + [i for i in enemies if i is not enemy]  # sem o player aqui
        enemy.update(dt, target=player.get_position(), solid_entities=others, bounds=limits)

    player.update(dt=dt, keys=keys, solid_entities=[rock] if player.is_dashing else [rock] + enemies, bounds=limits)
    box1.update(dt)

    tela.fill((30, 30, 45))

    janela_camera = calcular_camera(player, partida["width"], partida["height"], partida["largura_mundo"])
    camera_x = janela_camera[0]

    renderizeBeings(things, tela=tela, camera_x=camera_x)

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

    enemies[:] = removeBeings(enemies)
    things[:] = removeBeings(things)

    tem_proxima_fase = partida["fase_atual"] + 1 < len(FASES)
    fim_da_fase = (partida["fase_atual"] + 1) * LARGURA_FASE

    if not enemies and not partida["vitoria"] and not partida["aguardando_transicao"]:
        if tem_proxima_fase:
            partida["aguardando_transicao"] = True
            print("Area liberada! Siga em frente.")
        else:
            partida["vitoria"] = True
            print("VITORIA!")

    if partida["aguardando_transicao"]:
        zona = (fim_da_fase - 40, 0, 40, partida["height"])
        player_box = get_world_hitbox(player)

        if check_aabb_collision(*player_box, *zona):
            proxima_fase = partida["fase_atual"] + 1
            novos_inimigos = spawnar_fase(proxima_fase, partida["width"], partida["height"])

            partida["fase_atual"] = proxima_fase
            enemies.extend(novos_inimigos)
            things.extend(novos_inimigos)
            partida["aguardando_transicao"] = False
            partida["tempo_transicao"] = 0.0
            # nunca trava além da posição real do player, evita deadlock de colisão
            partida["limite_esquerdo"] = max(partida["limite_esquerdo"], player.x - 20)
            print(f"Fase {proxima_fase} iniciada!")
        else:
            partida["tempo_transicao"] += dt
            centro_y_player = player.y + player.height / 2
            desenhar_seta_transicao(tela, zona, camera_x, centro_y_player, partida["tempo_transicao"])

    # PARA VER HITBOXES, APAGAR ANTES DE BOTAR NO ORIGINAL PQ NÃO PODEMOS USAR FUNÇÕES DO PYGAME
    # for thing in things:
    #     pygame.draw.rect(tela,(0, 0, 0),(thing.x + thing.hitbox[0],thing.y + thing.hitbox[1],thing.hitbox[2],thing.hitbox[3]),2)

    # Minimapa
    desenhar_minimapa(tela, things, janela_camera, partida["viewport_minimapa"],
                       cor_fundo=(10, 10, 20), cor_borda=(255, 255, 255))

    return "vitoria" if partida["vitoria"] else "playing"

def runGame():
    pygame.init()
    width, height = 800, 600
    tela = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Zombots")
    clock = pygame.time.Clock()

    menu = Menu(width, height)
    intro = Intro(width, height)
    telas_info = {
        "controls": InfoScreen(width, height, "CONTROLS", [
            "SETAS: MOVER",
            "X: ATACAR",
            "S: DESVIAR (DASH)",
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
        "vitoria": InfoScreen(width, height, "VITORIA!", [
            "VOCE DERROTOU O CHEFE FINAL",
            "",
            "ESC: VOLTAR AO MENU",
        ]),
    }

    # Estados possíveis: "menu", "playing", "paused", "controls", "credits", "settings"
    estado = "intro"
    intro.open()
    partida = None

    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time em segundos

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

            elif estado == "intro":
                if intro.handle_event(evento) == "skip":
                    estado = "menu"
                    menu.open()

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
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_x:
                    partida["player"].start_attack()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_s:
                    partida["player"].start_dash()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado = "menu"
                    menu.open()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                    estado = "paused"
                    # Desenhado uma vez só: o frame congelado fica no buffer e o
                    # tela.fill de atualizar_partida() apaga o texto ao despausar
                    desenhar_texto_centralizado(tela, "PAUSED", width // 2, height // 2,
                                                (255, 255, 255), escala=6)

                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_RSHIFT:
                    partida["player"].start_dash()

            elif estado == "paused":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                    estado = "playing"

            elif estado in telas_info:
                if telas_info[estado].handle_event(evento) == "back":
                    estado = "menu"
                    menu.open()

        if estado == "intro":
            intro.draw(tela, dt)
        elif estado == "menu":
            menu.draw(tela)
        elif estado == "playing":
            keys = pygame.key.get_pressed()
            resultado = atualizar_partida(partida, tela, dt, keys)
            if resultado == "vitoria":
                estado = "vitoria"
                telas_info["vitoria"].open()
        elif estado in telas_info:
            telas_info[estado].draw(tela)
        pygame.display.flip()

def desenhar_seta_transicao(tela, zona, camera_x, centro_y_player, tempo, cor=(255, 255, 0)):
    zona_x, zona_y, zona_w, zona_h = zona
    zona_x -= camera_x

    bob = math.sin(tempo * 6) * 8  # balanço horizontal
    intensidade = 0.6 + 0.4 * math.sin(tempo * 8)  # pulso de brilho
    cor_pulsada = tuple(int(c * intensidade) for c in cor)

    ponta_x = zona_x + zona_w - 10 + bob

    seta = [
        (zona_x + 10 + bob, centro_y_player - 30),
        (zona_x + 10 + bob, centro_y_player + 30),
        (ponta_x, centro_y_player),
    ]
    scanline_fill(tela, seta, cor_pulsada)
    desenhar_poligono(tela, seta, cor_pulsada)

def calcular_camera(player, width, height, largura_mundo):
    centro_x = player.x + player.width / 2
    camera_x = centro_x - width / 2
    camera_x = max(0, min(camera_x, max(0, largura_mundo - width)))
    return (camera_x, 0, camera_x + width, height)

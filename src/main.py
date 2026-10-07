import pygame
import math
import random
from src.game.entities.Player import Player
from src.game.props.Rock import Rock
from src.game.props.Torn import Torn
from src.game.entities.Enemy import Enemy
from src.game.entities.Villain import Professor, MrBlack
from src.game.entities.Box import Box

from src.engine.sprite import draw_sprite_scaled
from src.engine.rendering import desenhar_poligono, scanline_fill, desenhar_minimapa, janela_com_zoom
from src.game.mechanics.Physics import check_aabb_collision, get_world_hitbox

from src.ui.Menu import Menu
from src.ui.InfoScreen import InfoScreen
from src.ui.Intro import Intro
from src.ui.BarraVida import desenhar_barra_vida, desenhar_barra_especial
from src.engine.fonte import desenhar_texto_centralizado, desenhar_texto
from src.ui.CharacterSelect import CharacterSelect
from src.engine.background import Cenario, ZONAS_JOGAVEIS, escurecer
from assets.sprites.entities.EnemySprite import get_enemy_animations, ENEMY_ANIMATIONS, get_villain_animations, VILLAIN_ANIMATIONS

DURACAO_FADE = 0.5
DURACAO_TITULO = 2.5

# índice da fase -> segunda onda, que entra quando restam <= quando_restam inimigos da primeira
ONDAS_EXTRAS = {
    0: {"tipos": ("zombie",), "lado": "esquerda", "quando_restam": 1},
    1: {"tipos": ("zombie", "robot"), "lado": "esquerda", "quando_restam": 1},
    2: {"tipos": ("zombie", "bobie"), "lado": "esquerda", "quando_restam": 1},
    3: {"tipos": ("robot", "zombie"), "lado": "esquerda", "quando_restam": 2},
}

def renderizeBeings(beings, tela, camera_x=0):
    for being in beings:

        if hasattr(being, "sprite") and hasattr(being.sprite, "matrix"):
            espelhar = getattr(being, "flip_x", False)
            off_x, off_y, altura = being.sprite_box() if hasattr(being, "sprite_box") else (0, 0, being.height)
            draw_sprite_scaled(tela, being.sprite.matrix, int(being.x + off_x - camera_x), int(being.y + off_y),
                                altura, flip_x=espelhar)
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
   # o vilão derrotado fica na lista até terminar de cair
   return [being for being in beings if getattr(being, "alive", True) or getattr(being, "playing_death", False)]

def updateBeing(entities):
    pass # Acho que não vai dar pra fazer esse.

MIN_INIMIGOS_REGULARES = 2
MAX_INIMIGOS_REGULARES = 5


def calcular_bordas(camera_x, width, fim_fase):
    return {
        "esquerda": camera_x - Enemy.WIDTH,
        "direita": min(camera_x + width, fim_fase - Enemy.WIDTH),
    }

def x_de_spawn(bordas, lado, i):
    if lado == "ambos":
        lado = "esquerda" if i % 2 else "direita"
    return bordas[lado]

def gerar_inimigos_regulares(bordas, zona_y, tipos, lado="direita"):
    min_y, max_y = zona_y
    y_min = min_y - Enemy.HITBOX[1]
    y_max = max_y - Enemy.HITBOX[1] - Enemy.HITBOX[3]
    faixa = max(0, y_max - y_min)
    espacamento = Enemy.HITBOX[3]
    capacidade = 1 + faixa // espacamento
    maximo = min(MAX_INIMIGOS_REGULARES, capacidade)
    minimo = min(maximo, max(MIN_INIMIGOS_REGULARES, len(tipos)))
    quantidade = random.randint(minimo, maximo)

    espaco_livre = faixa - (quantidade - 1) * espacamento
    offsets = sorted(random.randint(0, espaco_livre) for _ in range(quantidade))
    posicoes_y = [y_min + o + i * espacamento for i, o in enumerate(offsets)]
    random.shuffle(posicoes_y)

    inimigos = [Enemy(start_x=x_de_spawn(bordas, lado, i), start_y=y,
                  enemy_type=tipos[i % len(tipos)], damage=5)
            for i, y in enumerate(posicoes_y)]
    for i, inimigo in enumerate(inimigos):
        inimigo.slot_x = 28 if i % 2 == 0 else -28  # cada um mira um lado do player
    return inimigos

def fase_1(bordas, zona_y):
    return gerar_inimigos_regulares(bordas, zona_y, ("zombie", "zombot"), lado="direita")

def fase_2(bordas, zona_y):
    return gerar_inimigos_regulares(bordas, zona_y, ("zombie", "robot"), lado="direita")  # troque por "esquerda" ou "ambos"

def fase_3(bordas, zona_y):
    return gerar_inimigos_regulares(bordas, zona_y, ("zombie", "robot", "bobie"))

def fase_4(bordas, zona_y):
    return gerar_inimigos_regulares(bordas, zona_y, ("zombie", "robot", "robot"))

def fase_5(bordas, zona_y):
    return [Professor(start_x=bordas["direita"], start_y=zona_y[0])]

def fase_6(bordas, zona_y):
    return [MrBlack(start_x=bordas["direita"], start_y=zona_y[0])]

LARGURA_PADRAO = 900  # fases ainda sem cenário
FASES = [fase_1, fase_2, fase_3, fase_4, fase_5, fase_6]

def spawnar_fase(indice_fase, bordas, zonas):
    if indice_fase < len(FASES):
        return FASES[indice_fase](bordas, zonas[indice_fase])
    return []  # não há mais fases -> vitória

def nova_partida(width, height, personagem="apolo"):
    cenarios = [Cenario(i, height) for i in range(len(ZONAS_JOGAVEIS))]
    larguras = [c.largura for c in cenarios] + [LARGURA_PADRAO] * (len(FASES) - len(cenarios))
    offsets = [sum(larguras[:i]) for i in range(len(larguras))]

    zonas = [(c.zona_topo - Enemy.HITBOX[3], c.zona_base) for c in cenarios]
    zonas += [zonas[-1]] * (len(FASES) - len(zonas))  # fases sem cenário reaproveitam a última zona

    pes_y = (cenarios[0].zona_topo + cenarios[0].zona_base) // 2

    player = Player(start_x=50, start_y=pes_y - 110, character=personagem)
    rock = Rock(200, pes_y - 40)
    torn = Torn(400, pes_y - 60)
    box1 = Box(600, pes_y)

    fase_atual = 0
    bordas = calcular_bordas(0, width, larguras[0])
    enemies = spawnar_fase(fase_atual, bordas, zonas)

    props = [rock, torn]
    boxes = [box1]
    entities = [player] + boxes + enemies

    return {
        "player": player,
        "rock": rock,
        "torn": torn,
        "box1": box1,
        "enemies": enemies,
        "projeteis": [],
        "things": props + entities,
        "fase_atual": fase_atual,
        "width": width,
        "height": height,
        "cenarios": cenarios,
        "larguras": larguras,
        "offsets": offsets,
        "zonas": zonas,
        "limite_esquerdo": 0,  # avança e nunca mais recua
        "largura_mundo": sum(larguras),
        "viewport_minimapa": (600, 20, 780, 155),  # 180x135 = mesma proporção 4:3 da tela
        "zoom": 1.0,
        "vitoria": False,
        "aguardando_transicao": False,
        "tempo_transicao": 0.0,
        "transicao": None,
        "titulo": {"texto": "FASE 1", "tempo": 0.0},
        "onda_extra": ONDAS_EXTRAS.get(fase_atual),
    }

ZOOM_MIN, ZOOM_MAX, ZOOM_PASSO = 1.0, 4.0, 1.25

def ajustar_zoom(partida, fator=None, reset=False):
    """Zoom do minimapa (a tela principal não é afetada)."""
    if reset:
        partida["zoom"] = 1.0
    else:
        partida["zoom"] = max(ZOOM_MIN, min(ZOOM_MAX, partida["zoom"] * fator))

def desenhar_cena(partida, tela):
    fase = partida["fase_atual"]
    x_ini = partida["offsets"][fase]
    x_fim = x_ini + partida["larguras"][fase]
    janela = calcular_camera(partida["player"], partida["width"], partida["height"], x_ini, x_fim)
    camera_x = janela[0]

    for cen, off in zip(partida["cenarios"], partida["offsets"]):
        cen.desenhar(tela, off, camera_x)
    seres = sorted(partida["things"], key=lambda s: s.y + getattr(s, "height", 0))  # quem está mais abaixo (pés) fica na frente
    renderizeBeings(seres, tela=tela, camera_x=camera_x)
    return janela, camera_x

def desenhar_hud(partida, tela, janela_camera=None):
    player = partida["player"]
    desenhar_barra_vida(tela, 20, 20, player.health, player.max_health)
    desenhar_barra_especial(tela, 20, 68, player.special_progress, player.special_ready)

    fase = partida["fase_atual"]
    zoom = partida["zoom"]
    largura, altura = partida["width"], partida["height"]
    x_ini = partida["offsets"][fase]
    x_fim = x_ini + partida["larguras"][fase]

    # Window do minimapa: centrada no jogador, tamanho = tela / zoom (escala),
    # deslocada junto com ele (translação) e mantida dentro da fase atual.
    centro = (player.x + player.width / 2, player.y + player.height / 2)
    janela_mini = janela_com_zoom(centro, zoom, largura, altura, (x_ini, 0, x_fim, altura))

    fundo = None
    if fase < len(partida["cenarios"]):
        cen = partida["cenarios"][fase]
        u0 = (janela_mini[0] - x_ini) / cen.largura
        u1 = (janela_mini[2] - x_ini) / cen.largura
        v0 = janela_mini[1] / altura
        v1 = janela_mini[3] / altura
        fundo = (cen.matriz.transpose(1, 0, 2), u0, u1, v0, v1)  # surfarray (largura, altura) -> (altura, largura)

    desenhar_minimapa(tela, partida["things"], janela_mini, partida["viewport_minimapa"],
                      cor_fundo=(10, 10, 20), cor_borda=(255, 255, 255), fundo=fundo)

    vx0, vy0, vx1, vy1 = partida["viewport_minimapa"]
    desenhar_texto_centralizado(tela, f"ZOOM {zoom:.1f}X", (vx0 + vx1) // 2, vy1 + 14,
                                (235, 235, 245), escala=2)

def desenhar_titulo(partida, tela, dt):
    t = partida["titulo"]
    if t is None:
        return
    t["tempo"] += dt
    if t["tempo"] >= DURACAO_TITULO:
        partida["titulo"] = None
        return

    entrada = min(1.0, t["tempo"] / 0.4)
    y = -30 + 110 * entrada                    # translação: desce do topo até y = 80
    escala = round(9 - 4 * entrada)            # escala: 9x -> 5x
    saida = max(0.0, (t["tempo"] - (DURACAO_TITULO - 0.6)) / 0.6)
    brilho = 1 - saida                         # fade-out nos últimos 0,6 s

    cx = tela.get_width() // 2
    sombra = tuple(int(c * brilho) for c in (10, 10, 25))
    cor = tuple(int(c * brilho) for c in (255, 220, 60))
    desenhar_texto_centralizado(tela, t["texto"], cx + 4, int(y) + 4, sombra, escala)
    desenhar_texto_centralizado(tela, t["texto"], cx, int(y), cor, escala)

def entrar_na_proxima_fase(partida):
    player = partida["player"]
    proxima = partida["fase_atual"] + 1
    x_ini = partida["offsets"][proxima]
    x_fim = x_ini + partida["larguras"][proxima]

    player.x = x_ini + 50  # ponta esquerda da nova fase
    min_y = partida["zonas"][proxima][0]
    player.y = max(player.y, min_y - player.hitbox[1])  # a zona da nova fase pode começar mais embaixo
    partida["limite_esquerdo"] = x_ini
    partida["projeteis"].clear()

    camera_x = calcular_camera(player, partida["width"], partida["height"], x_ini, x_fim)[0]
    bordas = calcular_bordas(camera_x, partida["width"], x_fim)
    novos = spawnar_fase(proxima, bordas, partida["zonas"])

    partida["fase_atual"] = proxima
    partida["enemies"].extend(novos)
    partida["things"].extend(novos)
    partida["aguardando_transicao"] = False
    partida["tempo_transicao"] = 0.0
    partida["titulo"] = {"texto": f"FASE {proxima + 1}", "tempo": 0.0}
    partida["onda_extra"] = ONDAS_EXTRAS.get(proxima)

def atualizar_transicao(partida, tela, dt):
    tr = partida["transicao"]
    tr["tempo"] += dt

    if tr["etapa"] == "saindo":
        if tr["tempo"] >= DURACAO_FADE:
            entrar_na_proxima_fase(partida)
            tr["etapa"], tr["tempo"] = "entrando", 0.0
    elif tr["tempo"] >= DURACAO_FADE:
        partida["transicao"] = None

    janela, _ = desenhar_cena(partida, tela)
    desenhar_hud(partida, tela, janela)

    if partida["transicao"]:
        p = min(1.0, tr["tempo"] / DURACAO_FADE)
        escurecer(tela, 1 - p if tr["etapa"] == "saindo" else p)

    desenhar_titulo(partida, tela, dt)  # por cima do fade, para o texto não escurecer
    return "playing"

def atualizar_partida(partida, tela, dt, keys):
    if partida["transicao"]:
        return atualizar_transicao(partida, tela, dt)

    player = partida["player"]
    rock = partida["rock"]
    torn = partida["torn"]
    box1 = partida["box1"]
    enemies = partida["enemies"]
    things = partida["things"]
    fase = partida["fase_atual"]
    min_y, max_y = partida["zonas"][fase]
    fim_da_fase = partida["offsets"][fase] + partida["larguras"][fase]

    limits_player = (partida["limite_esquerdo"], min_y, fim_da_fase, max_y)
    limits = (None, min_y, fim_da_fase, max_y)  # borda esquerda aberta: inimigo pode nascer fora da tela à esquerda
    limits_proj = (0, 0, fim_da_fase, partida["height"])

    for enemy in enemies:
        others = [rock] + [i for i in enemies if i is not enemy and i.alive]  # sem o player aqui
        alvo = (player.x + getattr(enemy, "slot_x", 0), player.y)
        enemy.update(dt, target=alvo, solid_entities=others, bounds=limits)

    player.update(dt=dt, keys=keys, solid_entities=[rock] if player.is_dashing else [rock] + [e for e in enemies if e.alive], bounds=limits_player)
    box1.update(dt)

    # Verifica contato após o movimento; o primeiro frame do ataque já será desenhado.
    for enemy in enemies:
        enemy.try_attack(player)

    janela_camera, camera_x = desenhar_cena(partida, tela)

    player_box = get_world_hitbox(player)
    torn_box = get_world_hitbox(torn)
    box_box = get_world_hitbox(box1)

    if check_aabb_collision(*player_box, *torn_box):
        player.receive_damage(torn.damage)

    if check_aabb_collision(*player_box, *box_box):
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
                    enemy.apply_knockback(kx, ky)

        if box1.alive:
            box_box = get_world_hitbox(box1)
            if check_aabb_collision(*attack_box, *box_box):
                box1.receive_damage(player.damage)
                player.has_hit = True

    # ---- Projéteis do ataque especial (Hadouken) ----
    projeteis = partida["projeteis"]
    for proj in projeteis:
        proj.update(dt, bounds=limits_proj)
        proj_box = get_world_hitbox(proj)

        if check_aabb_collision(*proj_box, *get_world_hitbox(rock)):
            proj.alive = False  # a pedra bloqueia o projétil
            continue

        for enemy in enemies:
            if enemy.alive and id(enemy) not in proj.atingidos:
                if check_aabb_collision(*proj_box, *get_world_hitbox(enemy)):
                    proj.atingidos.add(id(enemy))  # atravessa, mas fere cada inimigo uma vez
                    enemy.receive_damage(proj.damage)
                    enemy.apply_knockback(proj.vx * 400, proj.vy * 400)

        if box1.alive and check_aabb_collision(*proj_box, *get_world_hitbox(box1)):
            box1.receive_damage(proj.damage)

    for proj in projeteis:
        if proj.alive:
            proj.draw(tela, camera_x)
    projeteis[:] = [p for p in projeteis if p.alive]

    # Fazendo um teste de remoção
    removeBeing(object=box1, beings=things, condition=box1.alive, message="Quebraste a caixa")

    enemies[:] = removeBeings(enemies)
    things[:] = removeBeings(things)

    onda = partida["onda_extra"]
    if onda and len(enemies) <= onda["quando_restam"]:
        partida["onda_extra"] = None
        bordas = calcular_bordas(camera_x, partida["width"], fim_da_fase)
        novos = gerar_inimigos_regulares(bordas, partida["zonas"][fase], onda["tipos"], onda["lado"])
        enemies.extend(novos)
        things.extend(novos)

    tem_proxima_fase = fase + 1 < len(FASES)

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
            partida["transicao"] = {"etapa": "saindo", "tempo": 0.0}
        else:
            partida["tempo_transicao"] += dt
            centro_y_player = player.y + player.height / 2
            desenhar_seta_transicao(tela, zona, camera_x, centro_y_player, partida["tempo_transicao"])

    desenhar_hud(partida, tela, janela_camera)
    desenhar_titulo(partida, tela, dt)

    return "vitoria" if partida["vitoria"] else "playing"

def runGame():
    pygame.init()
    width, height = 800, 600
    tela = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Zombots")
    clock = pygame.time.Clock()

    for tipo in ENEMY_ANIMATIONS:  # carrega as sprites uma vez, para o primeiro spawn não congelar
        get_enemy_animations(tipo)
    for tipo in VILLAIN_ANIMATIONS:
        get_villain_animations(tipo)

    menu = Menu(width, height)
    intro = Intro(width, height)
    character_select = CharacterSelect(width, height)
    telas_info = {
        "controls": InfoScreen(width, height, "CONTROLS", [
            "SETAS: MOVER",
            "X: ATACAR",
            "Z: DASH",
            "C: ATAQUE ESPECIAL",
            "+ / - OU RODA: ZOOM DO MINIMAPA",
            "0: RESETAR ZOOM",
            "P: PAUSAR",
            "ESC: VOLTAR AO MENU",
        ]),
        "credits": InfoScreen(width, height, "CREDITS", [
            "GABRIEL MARQUES",
            "DAVI JANNSEN",
            "APOLO VICTOR",
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
        dt = min(clock.tick(60) / 1000.0, 1 / 30)  # evita saltos grandes de movimento quando o FPS cai

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
                    estado = "character_select"
                    character_select.open()
                elif acao == "exit":
                    running = False
                elif acao in telas_info:
                    estado = acao
                    telas_info[estado].open()

            elif estado == "character_select":
                resultado = character_select.handle_event(evento)
                if resultado == "voltar":
                    estado = "menu"
                    menu.open()
                elif resultado is not None:
                    partida = nova_partida(width, height, personagem=resultado)
                    estado = "playing"

            elif estado == "playing":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_x:
                    partida["player"].start_attack()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_c:
                    projetil = partida["player"].start_special()
                    if projetil is not None:
                        partida["projeteis"].append(projetil)
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_z:
                    partida["player"].start_dash()
                elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    ajustar_zoom(partida, ZOOM_PASSO)
                elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    ajustar_zoom(partida, 1 / ZOOM_PASSO)
                elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_0, pygame.K_KP0):
                    ajustar_zoom(partida, reset=True)
                elif evento.type == pygame.MOUSEWHEEL and evento.y != 0:
                    ajustar_zoom(partida, ZOOM_PASSO if evento.y > 0 else 1 / ZOOM_PASSO)
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado = "menu"
                    menu.open()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                    estado = "paused"
                    desenhar_texto_centralizado(tela, "PAUSED", width // 2, height // 2,
                                                (255, 255, 255), escala=6)

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
        elif estado == "character_select":
            character_select.draw(tela)
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

def calcular_camera(player, width, height, x_min, x_max):
    centro_x = player.x + player.width / 2
    camera_x = centro_x - width / 2
    camera_x = max(x_min, min(camera_x, max(x_min, x_max - width)))
    return (camera_x, 0, camera_x + width, height)
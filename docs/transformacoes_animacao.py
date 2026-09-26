import pygame
import sys
import math
import random

pygame.init()

# =====================================================
# CONFIGURAÇÃO
# =====================================================

LARGURA = 800
ALTURA = 600

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Nave 2D - Transformações e Colisão AABB")

clock = pygame.time.Clock()

# =====================================================
# CORES
# =====================================================

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

CEU = (8, 10, 30)

AZUL = (40, 160, 255)
AZUL_ESCURO = (20, 70, 130)

AMARELO = (255, 220, 80)
LARANJA = (255, 120, 30)

CINZA = (45, 48, 65)
CINZA_ESCURO = (25, 28, 40)

VERDE = (60, 230, 100)
VERMELHO = (255, 60, 60)


# =====================================================
# 1. PIXEL
# =====================================================

def setPixel(superficie, x, y, cor):
    x = int(x)
    y = int(y)

    if 0 <= x < superficie.get_width() and \
       0 <= y < superficie.get_height():

        superficie.set_at((x, y), cor)


# =====================================================
# 2. BRESENHAM
# =====================================================

def bresenham(superficie, x0, y0, x1, y1, cor):

    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)

    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = abs(y1 - y0)

    ystep = 1 if y0 < y1 else -1

    d = 2 * dy - dx
    y = y0

    for x in range(x0, x1 + 1):

        if steep:
            setPixel(superficie, y, x, cor)
        else:
            setPixel(superficie, x, y, cor)

        if d > 0:
            y += ystep
            d -= 2 * dx

        d += 2 * dy


# =====================================================
# 3. DESENHO DE POLÍGONO
# =====================================================

def desenhar_poligono(superficie, pontos, cor):

    n = len(pontos)

    for i in range(n):

        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]

        bresenham(
            superficie,
            x0, y0,
            x1, y1,
            cor
        )


# =====================================================
# 4. SCANLINE FILL
# =====================================================

def scanline_fill(superficie, pontos, cor):

    ys = [p[1] for p in pontos]

    y_min = max(0, int(min(ys)))
    y_max = min(superficie.get_height() - 1, int(max(ys)))

    n = len(pontos)

    for y in range(y_min, y_max + 1):

        intersecoes = []

        for i in range(n):

            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]

            # Ignora arestas horizontais
            if y0 == y1:
                continue

            # Garante y0 < y1
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            # Verifica se a scanline cruza a aresta
            if y < y0 or y >= y1:
                continue

            x = x0 + \
                (y - y0) * \
                (x1 - x0) / \
                (y1 - y0)

            intersecoes.append(x)

        intersecoes.sort()

        # Preenche entre pares de interseções
        for i in range(0, len(intersecoes), 2):

            if i + 1 < len(intersecoes):

                x_inicio = int(intersecoes[i])
                x_fim = int(intersecoes[i + 1])

                for x in range(x_inicio, x_fim + 1):
                    setPixel(superficie, x, y, cor)


# =====================================================
# 5. MATRIZES HOMOGÊNEAS 2D
# =====================================================

def identidade():

    return [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]


def translacao(tx, ty):

    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]


def escala(sx, sy):

    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]


def rotacao(theta):

    c = math.cos(theta)
    s = math.sin(theta)

    return [
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ]


def multiplica_matrizes(a, b):

    r = [[0] * 3 for _ in range(3)]

    for i in range(3):
        for j in range(3):
            for k in range(3):

                r[i][j] += a[i][k] * b[k][j]

    return r

# =====================================================
# 6. APLICAÇÃO DA TRANSFORMAÇÃO
# =====================================================

def aplica_transformacao(m, pontos):

    novos = []

    for x, y in pontos:

        v = [x, y, 1]

        x_novo = (
            m[0][0] * v[0] +
            m[0][1] * v[1] +
            m[0][2]
        )

        y_novo = (
            m[1][0] * v[0] +
            m[1][1] * v[1] +
            m[1][2]
        )

        novos.append((x_novo, y_novo))

    return novos

# =====================================================
# 7. AABB
# =====================================================

def calcular_aabb(pontos):
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    
    return min(xs), min(ys), max(xs), max(ys)

def colisao_aabb(a, b):
   ax1, ay1, ax2, ay2 = a
   bx1, by1, bx2, by2 = b
   
   return (
   ax1 < bx2 and
   ax2 > bx1 and
   ay1 < by2 and
   ay2 > by1
   )

def desenhar_aabb(superficie, aabb, cor):

    x1, y1, x2, y2 = aabb

    pontos = [
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2)
    ]

    desenhar_poligono(superficie, pontos, cor)

# =====================================================
# 8. FUNÇÃO AUXILIAR PARA RETÂNGULOS
# =====================================================

def retangulo_para_poligono(x, y, largura, altura):

    return [
        (x, y),
        (x + largura, y),
        (x + largura, y + altura),
        (x, y + altura)
    ]

# =====================================================
# 9. CENÁRIO
# =====================================================

# Estrelas geradas apenas uma vez
random.seed(10)

estrelas = []

for i in range(70):

    estrelas.append((
        random.randint(0, LARGURA - 1),
        random.randint(0, 320)
    ))


# Prédios
predios = [
    (0,   450, 100, 150),
    (130, 390, 100, 210),
    (270, 470, 110, 130),
    (420, 410, 110, 190),
    (580, 455, 90, 145),
    (710, 370, 90, 230)
]

# =====================================================
# 10. DESENHO DO CENÁRIO
# =====================================================

def desenhar_cenario(superficie):

    superficie.fill(CEU)

    # -------------------------------------------------
    # Estrelas
    # -------------------------------------------------

    for x, y in estrelas:

        setPixel(superficie, x, y, BRANCO)

        # Algumas estrelas ficam maiores
        if (x + y) % 5 == 0:

            setPixel(superficie, x + 1, y, BRANCO)
            setPixel(superficie, x - 1, y, BRANCO)
            setPixel(superficie, x, y + 1, BRANCO)
            setPixel(superficie, x, y - 1, BRANCO)

    # -------------------------------------------------
    # Lua
    # -------------------------------------------------

    pygame.draw.circle(
        superficie,
        (230, 230, 190),
        (680, 90),
        35
    )

    pygame.draw.circle(
        superficie,
        CEU,
        (695, 80),
        30
    )

    # -------------------------------------------------
    # Prédios
    # -------------------------------------------------

    for indice, (x, y, w, h) in enumerate(predios):

        pontos = retangulo_para_poligono(x, y, w, h)

        cor_predio = CINZA if indice % 2 == 0 else CINZA_ESCURO

        scanline_fill(
            superficie,
            pontos,
            cor_predio
        )

        desenhar_poligono(
            superficie,
            pontos,
            (80, 85, 110)
        )

        # ---------------------------------------------
        # Janelas
        # ---------------------------------------------

        for janela_y in range(y + 20, y + h - 15, 30):

            for janela_x in range(x + 15, x + w - 10, 25):

                # Algumas janelas ficam apagadas
                if (janela_x + janela_y) % 4 != 0:

                    janela = retangulo_para_poligono(
                        janela_x,
                        janela_y,
                        8,
                        12
                    )

                    scanline_fill(
                        superficie,
                        janela,
                        AMARELO
                    )


# =====================================================
# 11. MODELO DA NAVE
# =====================================================
#
# IMPORTANTE:
#
# A nave NÃO está posicionada na tela.
#
# Ela existe em COORDENADAS LOCAIS,
# centrada aproximadamente na origem.
#
# =====================================================

nave_modelo = [
    (0, -25),
    (28, 12),
    (15, 10),
    (10, 20),
    (-10, 20),
    (-15, 10),
    (-28, 12)
]


# Cockpit também em coordenadas locais
cockpit_modelo = [
    (-9, -5),
    (0, -15),
    (9, -5),
    (6, 4),
    (-6, 4)
]


# Chama local
chama_modelo = [
    (-8, 18),
    (0, 35),
    (8, 18)
]


# =====================================================
# 12. ESTADO DA NAVE
# =====================================================

x_nave = 400
y_nave = 250

vx = 0
vy = 0

aceleracao = 0.18
velocidade_maxima = 4.0

friccao = 0.97

angulo = 0
tempo = 0

mostrar_aabb = False

# =====================================================
# 13. LOOP PRINCIPAL
# =====================================================

rodando = True

while rodando:

    # =================================================
    # INPUT
    # =================================================

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:
                rodando = False

            # Liga/desliga visualização das AABBs
            if evento.key == pygame.K_h:
                mostrar_aabb = not mostrar_aabb


    teclas = pygame.key.get_pressed()


    # =================================================
    # UPDATE - MOVIMENTO
    # =================================================
    if teclas[pygame.K_LEFT]:
        vx -= aceleracao
    
    if teclas[pygame.K_RIGHT]:
        vx += aceleracao
    
    if teclas[pygame.K_UP]:
        vy -= aceleracao
    
    if teclas[pygame.K_DOWN]:
        vy += aceleracao            
    
    # Limitar velocidade
    vx = max(-velocidade_maxima, min(velocidade_maxima, vx))
    vy = max(-velocidade_maxima, min(velocidade_maxima, vy))

    # Guardamos posição anterior
    x_anterior = x_nave
    y_anterior = y_nave
    
    # Atualização da posição
    x_nave += vx
    y_nave += vy

    # Fricção
    vx *= friccao
    vy *= friccao

    # =================================================
    # ANIMAÇÃO
    # =================================================
    tempo += 0.05
    angulo_alvo = vx * 0.06
    angulo = (angulo_alvo - angulo) * 0.08
    escala_animada = 1.0 + 0.025*math.sin(tempo*3)

    # =================================================
    # TRANSFORMAÇÃO DA NAVE
    # =================================================
    #
    # Como o modelo está na origem:
    #
    #      Modelo
    #        ↓
    #      Escala
    #        ↓
    #      Rotação
    #        ↓
    #      Translação
    #        ↓
    #       Mundo
    #
    # Com vetores coluna:
    #
    # P' = T · R · S · P
    #
    # =================================================
    M = identidade()
    M = multiplica_matrizes(
        escala(escala_animada, escala_animada),
        M
        )
    M = multiplica_matrizes(
        rotacao(angulo),
        M
        )
        
    M = multiplica_matrizes(
        translacao(x_nave, y_nave),
        M
        )        
    
    nave_transformada = aplica_transformacao(
        M,
        nave_modelo
    )


    cockpit_transformado = aplica_transformacao(
        M,
        cockpit_modelo
    )


    # =================================================
    # ANIMAÇÃO DA CHAMA
    # =================================================
    intensidade_chama = (1.0+0.25*math.sin(tempo*10))
    
    M_chama_local = escala(1, intensidade_chama)
    chama_animada = aplica_transformacao(M_chama_local, chama_modelo)
    chama_transformada = aplica_transformacao(M, chama_animada)   
    

    # A chama recebe uma transformação própria
    # antes da transformação da nave.

    
    # =================================================
    # AABB DA NAVE
    # =================================================

    aabb_nave = calcular_aabb(
        nave_transformada
    )

    # =================================================
    # COLISÃO COM AS BORDAS DA TELA
    # =================================================
    x1, y1, x2, y2 = aabb_nave
    colidiu = False
     
    if x1 < 0 or x2 >= LARGURA:
        colidiu = True
     
    if y1 < 0 or y2 >= ALTURA:
        colidiu = True    

    # =================================================
    # COLISÃO COM OS PRÉDIOS
    # =================================================

    for x, y, w, h in predios:

        aabb_predio = (
            x,
            y,
            x + w,
            y + h
        )

        if colisao_aabb(
            aabb_nave,
            aabb_predio
        ):
            colidiu = True
            break

    # =================================================
    # RESPOSTA À COLISÃO
    # =================================================
    #
    # Solução propositalmente simples:
    #
    # volta para a posição anterior
    # e rebate a velocidade.
    #
    # =================================================

    if colidiu:

        x_nave = x_anterior
        y_nave = y_anterior

        vx *= -0.5
        vy *= -0.5

        # Recalcula transformação após corrigir posição

        M = identidade()

        M = multiplica_matrizes(
            escala(
                escala_animada,
                escala_animada
            ),
            M
        )

        M = multiplica_matrizes(
            rotacao(angulo),
            M
        )

        M = multiplica_matrizes(
            translacao(
                x_nave,
                y_nave
            ),
            M
        )

        nave_transformada = aplica_transformacao(
            M,
            nave_modelo
        )

        cockpit_transformado = aplica_transformacao(
            M,
            cockpit_modelo
        )

        chama_transformada = aplica_transformacao(
            M,
            chama_animada
        )

        aabb_nave = calcular_aabb(
            nave_transformada
        )


    # =================================================
    # RENDERIZAÇÃO
    # =================================================

    desenhar_cenario(tela)


    # -------------------------------------------------
    # Chama
    # -------------------------------------------------

    scanline_fill(
        tela,
        chama_transformada,
        LARANJA
    )

    desenhar_poligono(
        tela,
        chama_transformada,
        AMARELO
    )


    # -------------------------------------------------
    # Corpo da nave
    # -------------------------------------------------

    scanline_fill(
        tela,
        nave_transformada,
        AZUL_ESCURO
    )

    desenhar_poligono(
        tela,
        nave_transformada,
        BRANCO
    )


    # -------------------------------------------------
    # Cockpit
    # -------------------------------------------------

    scanline_fill(
        tela,
        cockpit_transformado,
        AZUL
    )

    desenhar_poligono(
        tela,
        cockpit_transformado,
        BRANCO
    )


    # =================================================
    # DEBUG - AABBs
    # =================================================

    if mostrar_aabb:

        # AABB da nave
        desenhar_aabb(
            tela,
            aabb_nave,
            VERDE
        )

        # AABB dos prédios
        for x, y, w, h in predios:

            aabb_predio = (
                x,
                y,
                x + w,
                y + h
            )

            desenhar_aabb(
                tela,
                aabb_predio,
                VERMELHO
            )


    # =================================================
    # TEXTO
    # =================================================

    fonte = pygame.font.Font(None, 24)

    texto = fonte.render(
        "SETAS: mover | H: AABB | ESC: sair",
        True,
        BRANCO
    )

    tela.blit(
        texto,
        (15, 15)
    )


    # =================================================
    # FINAL DO FRAME
    # =================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()
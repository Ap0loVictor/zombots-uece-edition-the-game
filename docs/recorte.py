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
FPS = 60

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption(
    "Nave 2D - Transformações, AABB, Viewports e Clipping"
)

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
# CLIPPING ATUAL DAS VIEWPORTS
# =====================================================

clip_atual = None


# =====================================================
# 1. PIXEL
# =====================================================

def setPixel(superficie, x, y, cor):

    global clip_atual

    x = int(x)
    y = int(y)

    # Limites físicos da tela
    if not (
        0 <= x < superficie.get_width()
        and
        0 <= y < superficie.get_height()
    ):
        return

    # Clipping opcional das viewports
    if clip_atual is not None:

        xmin, ymin, xmax, ymax = clip_atual

        if (
            x < xmin
            or x > xmax
            or y < ymin
            or y > ymax
        ):
            return

    superficie.set_at(
        (x, y),
        cor
    )


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
            setPixel(
                superficie,
                y,
                x,
                cor
            )
        else:
            setPixel(
                superficie,
                x,
                y,
                cor
            )

        if d > 0:
            y += ystep
            d -= 2 * dx

        d += 2 * dy


# =====================================================
# 3. CLIPPING DE LINHAS - COHEN-SUTHERLAND
# =====================================================

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def codigo_regiao(
    x, y,
    xmin, ymin,
    xmax, ymax
):

    codigo = INSIDE

    if x < xmin:
        codigo |= LEFT

    elif x > xmax:
        codigo |= RIGHT

    # No Pygame, Y cresce para baixo
    if y < ymin:
        codigo |= TOP

    elif y > ymax:
        codigo |= BOTTOM

    return codigo


def cohen_sutherland(
    x0, y0,
    x1, y1,
    xmin, ymin,
    xmax, ymax
):

    c0 = codigo_regiao(
        x0, y0,
        xmin, ymin,
        xmax, ymax
    )

    c1 = codigo_regiao(
        x1, y1,
        xmin, ymin,
        xmax, ymax
    )

    while True:

        # ---------------------------------------------
        # ACEITAÇÃO TRIVIAL
        # Os dois pontos estão dentro
        # ---------------------------------------------

        if not (c0 | c1):

            return (
                True,
                x0, y0,
                x1, y1
            )

        # ---------------------------------------------
        # REJEIÇÃO TRIVIAL
        # Os dois pontos estão fora do mesmo lado
        # ---------------------------------------------

        if c0 & c1:

            return (
                False,
                0, 0,
                0, 0
            )

        # Escolhe uma extremidade externa
        c_out = c0 if c0 else c1

        # ---------------------------------------------
        # INTERSEÇÃO COM O TOPO
        # ---------------------------------------------

        if c_out & TOP:

            x = (
                x0
                + (x1 - x0)
                * (ymin - y0)
                / (y1 - y0)
            )

            y = ymin

        # ---------------------------------------------
        # INTERSEÇÃO COM A BASE
        # ---------------------------------------------

        elif c_out & BOTTOM:

            x = (
                x0
                + (x1 - x0)
                * (ymax - y0)
                / (y1 - y0)
            )

            y = ymax

        # ---------------------------------------------
        # INTERSEÇÃO COM A DIREITA
        # ---------------------------------------------

        elif c_out & RIGHT:

            y = (
                y0
                + (y1 - y0)
                * (xmax - x0)
                / (x1 - x0)
            )

            x = xmax

        # ---------------------------------------------
        # INTERSEÇÃO COM A ESQUERDA
        # ---------------------------------------------

        else:

            y = (
                y0
                + (y1 - y0)
                * (xmin - x0)
                / (x1 - x0)
            )

            x = xmin

        # ---------------------------------------------
        # Substitui o ponto externo pela interseção
        # ---------------------------------------------

        if c_out == c0:

            x0 = x
            y0 = y

            c0 = codigo_regiao(
                x0, y0,
                xmin, ymin,
                xmax, ymax
            )

        else:

            x1 = x
            y1 = y

            c1 = codigo_regiao(
                x1, y1,
                xmin, ymin,
                xmax, ymax
            )


def desenhar_linha_recortada(
    superficie,
    x0, y0,
    x1, y1,
    janela,
    cor
):

    xmin, ymin, xmax, ymax = janela

    visivel, rx0, ry0, rx1, ry1 = cohen_sutherland(
        x0, y0,
        x1, y1,
        xmin, ymin,
        xmax, ymax
    )

    if visivel:

        bresenham(
            superficie,
            rx0, ry0,
            rx1, ry1,
            cor
        )


# =====================================================
# 4. DESENHO DO POLÍGONO
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
# 5. SCANLINE FILL
# =====================================================

def scanline_fill(superficie, pontos, cor):

    ys = [p[1] for p in pontos]

    y_min = max(
        0,
        int(min(ys))
    )

    y_max = min(
        superficie.get_height() - 1,
        int(max(ys))
    )

    n = len(pontos)

    for y in range(y_min, y_max + 1):

        intersecoes = []

        for i in range(n):

            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]

            if y0 == y1:
                continue

            if y0 > y1:
                x0, y0, x1, y1 = (
                    x1, y1,
                    x0, y0
                )

            if y < y0 or y >= y1:
                continue

            x = (
                x0
                + (y - y0)
                * (x1 - x0)
                / (y1 - y0)
            )

            intersecoes.append(x)

        intersecoes.sort()

        for i in range(
            0,
            len(intersecoes),
            2
        ):

            if i + 1 < len(intersecoes):

                x_inicio = int(
                    intersecoes[i]
                )

                x_fim = int(
                    intersecoes[i + 1]
                )

                for x in range(
                    x_inicio,
                    x_fim + 1
                ):

                    setPixel(
                        superficie,
                        x,
                        y,
                        cor
                    )


# =====================================================
# 6. MATRIZES HOMOGÊNEAS 2D
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

    r = [
        [0] * 3
        for _ in range(3)
    ]

    for i in range(3):
        for j in range(3):
            for k in range(3):

                r[i][j] += (
                    a[i][k]
                    * b[k][j]
                )

    return r


# =====================================================
# 7. APLICAÇÃO DA TRANSFORMAÇÃO
# =====================================================

def aplica_transformacao(m, pontos):

    novos = []

    for x, y in pontos:

        v = [x, y, 1]

        x_novo = (
            m[0][0] * v[0]
            + m[0][1] * v[1]
            + m[0][2]
        )

        y_novo = (
            m[1][0] * v[0]
            + m[1][1] * v[1]
            + m[1][2]
        )

        novos.append(
            (x_novo, y_novo)
        )

    return novos


# =====================================================
# 8. JANELA -> VIEWPORT
# =====================================================

def janela_viewport(janela, viewport):

    Wxmin, Wymin, Wxmax, Wymax = janela
    Vxmin, Vymin, Vxmax, Vymax = viewport

    sx = (
        (Vxmax - Vxmin)
        / (Wxmax - Wxmin)
    )

    sy = (
        (Vymax - Vymin)
        / (Wymax - Wymin)
    )

    M = identidade()

    # Janela -> origem
    M = multiplica_matrizes(
        translacao(
            -Wxmin,
            -Wymin
        ),
        M
    )

    # Escala
    M = multiplica_matrizes(
        escala(
            sx,
            sy
        ),
        M
    )

    # Origem -> viewport
    M = multiplica_matrizes(
        translacao(
            Vxmin,
            Vymin
        ),
        M
    )

    return M


# =====================================================
# 9. AABB
# =====================================================

def calcular_aabb(pontos):

    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]

    return (
        min(xs),
        min(ys),
        max(xs),
        max(ys)
    )


def colisao_aabb(a, b):

    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    return (
        ax1 < bx2
        and ax2 > bx1
        and ay1 < by2
        and ay2 > by1
    )


def desenhar_aabb(
    superficie,
    aabb,
    cor
):

    x1, y1, x2, y2 = aabb

    pontos = [
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2)
    ]

    desenhar_poligono(
        superficie,
        pontos,
        cor
    )


# =====================================================
# 10. RETÂNGULO COMO POLÍGONO
# =====================================================

def retangulo_para_poligono(
    x,
    y,
    largura,
    altura
):

    return [
        (x, y),
        (x + largura, y),
        (x + largura, y + altura),
        (x, y + altura)
    ]


# =====================================================
# 11. PREENCHER REGIÃO COM SETPIXEL
# =====================================================

def preencher_regiao(
    superficie,
    xmin,
    ymin,
    xmax,
    ymax,
    cor
):

    for y in range(
        int(ymin),
        int(ymax) + 1
    ):

        for x in range(
            int(xmin),
            int(xmax) + 1
        ):

            setPixel(
                superficie,
                x,
                y,
                cor
            )


# =====================================================
# 12. CENÁRIO
# =====================================================

random.seed(10)

estrelas = []

for i in range(70):

    estrelas.append((
        random.randint(
            0,
            LARGURA - 1
        ),

        random.randint(
            0,
            320
        )
    ))


predios = [
    (0,   450, 100, 150),
    (130, 390, 100, 210),
    (270, 470, 110, 130),
    (420, 410, 110, 190),
    (580, 455, 90, 145),
    (710, 370, 90, 230)
]


# =====================================================
# 13. DESENHO DO CENÁRIO
# =====================================================

def desenhar_cenario(superficie):

    superficie.fill(CEU)

    # -------------------------------------------------
    # ESTRELAS
    # -------------------------------------------------

    for x, y in estrelas:

        setPixel(
            superficie,
            x,
            y,
            BRANCO
        )

        if (x + y) % 5 == 0:

            setPixel(
                superficie,
                x + 1,
                y,
                BRANCO
            )

            setPixel(
                superficie,
                x - 1,
                y,
                BRANCO
            )

            setPixel(
                superficie,
                x,
                y + 1,
                BRANCO
            )

            setPixel(
                superficie,
                x,
                y - 1,
                BRANCO
            )

    # -------------------------------------------------
    # LUA - RASTERIZAÇÃO MANUAL
    # -------------------------------------------------

    cx_lua = 680
    cy_lua = 90
    raio_lua = 35

    for y in range(
        cy_lua - raio_lua,
        cy_lua + raio_lua + 1
    ):

        for x in range(
            cx_lua - raio_lua,
            cx_lua + raio_lua + 1
        ):

            dx = x - cx_lua
            dy = y - cy_lua

            if (
                dx * dx
                + dy * dy
                <= raio_lua * raio_lua
            ):

                setPixel(
                    superficie,
                    x,
                    y,
                    (230, 230, 190)
                )

    # Sombra da lua

    cx_sombra = 695
    cy_sombra = 80
    raio_sombra = 30

    for y in range(
        cy_sombra - raio_sombra,
        cy_sombra + raio_sombra + 1
    ):

        for x in range(
            cx_sombra - raio_sombra,
            cx_sombra + raio_sombra + 1
        ):

            dx = x - cx_sombra
            dy = y - cy_sombra

            if (
                dx * dx
                + dy * dy
                <= raio_sombra * raio_sombra
            ):

                setPixel(
                    superficie,
                    x,
                    y,
                    CEU
                )

    # -------------------------------------------------
    # PRÉDIOS
    # -------------------------------------------------

    for indice, (x, y, w, h) in enumerate(
        predios
    ):

        pontos = retangulo_para_poligono(
            x,
            y,
            w,
            h
        )

        cor_predio = (
            CINZA
            if indice % 2 == 0
            else CINZA_ESCURO
        )

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

        # Janelas

        for janela_y in range(
            y + 20,
            y + h - 15,
            30
        ):

            for janela_x in range(
                x + 15,
                x + w - 10,
                25
            ):

                if (
                    janela_x
                    + janela_y
                ) % 4 != 0:

                    janela = (
                        retangulo_para_poligono(
                            janela_x,
                            janela_y,
                            8,
                            12
                        )
                    )

                    scanline_fill(
                        superficie,
                        janela,
                        AMARELO
                    )


# =====================================================
# 14. MODELOS DA NAVE
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


cockpit_modelo = [
    (-9, -5),
    (0, -15),
    (9, -5),
    (6, 4),
    (-6, 4)
]


chama_modelo = [
    (-8, 18),
    (0, 35),
    (8, 18)
]


# =====================================================
# 15. VIEWPORTS
# =====================================================

viewport_minimapa = (
    20,
    60,
    220,
    210
)


viewport_zoom = (
    580,
    60,
    780,
    210
)


janela_mundo = (
    0,
    0,
    LARGURA,
    ALTURA
)


# =====================================================
# 16. JANELA PARA DEMONSTRAÇÃO DO CLIPPING
# =====================================================

janela_clipping = (
    280,
    250,
    520,
    350
)


# =====================================================
# 17. DESENHO DA VIEWPORT
# =====================================================

def desenhar_viewport(
    superficie,
    matriz_viewport,
    nave,
    cockpit,
    chama,
    viewport,
    cor_borda
):

    global clip_atual

    Vxmin, Vymin, Vxmax, Vymax = viewport

    # =================================================
    # ATIVA CLIPPING DA VIEWPORT
    # =================================================

    clip_atual = viewport

    # =================================================
    # FUNDO
    # =================================================

    preencher_regiao(
        superficie,
        Vxmin,
        Vymin,
        Vxmax,
        Vymax,
        CEU
    )

    # =================================================
    # PRÉDIOS
    # =================================================

    for indice, (x, y, w, h) in enumerate(
        predios
    ):

        predio = retangulo_para_poligono(
            x,
            y,
            w,
            h
        )

        predio_view = aplica_transformacao(
            matriz_viewport,
            predio
        )

        cor = (
            CINZA
            if indice % 2 == 0
            else CINZA_ESCURO
        )

        scanline_fill(
            superficie,
            predio_view,
            cor
        )

        desenhar_poligono(
            superficie,
            predio_view,
            (100, 105, 130)
        )

    # =================================================
    # CHAMA
    # =================================================

    chama_view = aplica_transformacao(
        matriz_viewport,
        chama
    )

    scanline_fill(
        superficie,
        chama_view,
        LARANJA
    )

    desenhar_poligono(
        superficie,
        chama_view,
        AMARELO
    )

    # =================================================
    # NAVE
    # =================================================

    nave_view = aplica_transformacao(
        matriz_viewport,
        nave
    )

    scanline_fill(
        superficie,
        nave_view,
        AZUL_ESCURO
    )

    desenhar_poligono(
        superficie,
        nave_view,
        BRANCO
    )

    # =================================================
    # COCKPIT
    # =================================================

    cockpit_view = aplica_transformacao(
        matriz_viewport,
        cockpit
    )

    scanline_fill(
        superficie,
        cockpit_view,
        AZUL
    )

    desenhar_poligono(
        superficie,
        cockpit_view,
        BRANCO
    )

    # =================================================
    # DESATIVA CLIPPING
    # =================================================

    clip_atual = None

    # =================================================
    # BORDA DA VIEWPORT
    # =================================================

    borda = [
        (Vxmin, Vymin),
        (Vxmax, Vymin),
        (Vxmax, Vymax),
        (Vxmin, Vymax)
    ]

    desenhar_poligono(
        superficie,
        borda,
        cor_borda
    )


# =====================================================
# 18. ESTADO DA NAVE
# =====================================================

x_nave = 400
y_nave = 250

vx = 0
vy = 0

aceleracao = 0.28
velocidade_maxima = 8.0

friccao = 0.99

angulo = 0
tempo = 0

mostrar_aabb = False


# =====================================================
# 19. LOOP PRINCIPAL
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

            if evento.key == pygame.K_h:
                mostrar_aabb = (
                    not mostrar_aabb
                )

    teclas = pygame.key.get_pressed()


    # =================================================
    # UPDATE
    # =================================================

    if teclas[pygame.K_LEFT]:
        vx -= aceleracao

    if teclas[pygame.K_RIGHT]:
        vx += aceleracao

    if teclas[pygame.K_UP]:
        vy -= aceleracao

    if teclas[pygame.K_DOWN]:
        vy += aceleracao


    # Limite de velocidade

    vx = max(
        -velocidade_maxima,
        min(
            velocidade_maxima,
            vx
        )
    )

    vy = max(
        -velocidade_maxima,
        min(
            velocidade_maxima,
            vy
        )
    )


    # Posição anterior

    x_anterior = x_nave
    y_anterior = y_nave


    # Movimento

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

    angulo += (
        angulo_alvo
        - angulo
    ) * 0.08


    escala_animada = (
        1.0
        + 0.025
        * math.sin(tempo * 3)
    )


    # =================================================
    # MODELAGEM DA NAVE
    # =================================================
    #
    # Pmundo = T * R * S * Plocal
    #
    # =================================================

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


    # =================================================
    # ANIMAÇÃO DA CHAMA
    # =================================================

    intensidade_chama = (
        1.0
        + 0.25
        * math.sin(tempo * 10)
    )


    M_chama_local = escala(
        1,
        intensidade_chama
    )


    chama_animada = aplica_transformacao(
        M_chama_local,
        chama_modelo
    )


    chama_transformada = aplica_transformacao(
        M,
        chama_animada
    )


    # =================================================
    # AABB
    # =================================================

    aabb_nave = calcular_aabb(
        nave_transformada
    )

    x1, y1, x2, y2 = aabb_nave

    colidiu = False


    # =================================================
    # COLISÃO COM AS BORDAS
    # =================================================

    if (
        x1 < 0
        or x2 >= LARGURA
    ):
        colidiu = True


    if (
        y1 < 0
        or y2 >= ALTURA
    ):
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

    if colidiu:

        x_nave = x_anterior
        y_nave = y_anterior

        vx *= -0.5
        vy *= -0.5


        # Recalcula transformação

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
    # RENDERIZAÇÃO PRINCIPAL
    # =================================================

    desenhar_cenario(tela)


    # -------------------------------------------------
    # CHAMA
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
    # NAVE
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
    # COCKPIT
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
    # EXEMPLO DE CLIPPING
    # =================================================
    #
    # A linha original seria:
    #
    # (150,320) -------------------- (650,270)
    #
    # Mas apenas o trecho que está dentro da janela
    # verde será enviado ao Bresenham.
    #
    # =================================================

    desenhar_linha_recortada(
        tela,

        150, 320,
        650, 270,

        janela_clipping,

        VERMELHO
    )


    # -------------------------------------------------
    # BORDA DA JANELA DE CLIPPING
    # -------------------------------------------------

    xmin, ymin, xmax, ymax = janela_clipping

    borda_clipping = [
        (xmin, ymin),
        (xmax, ymin),
        (xmax, ymax),
        (xmin, ymax)
    ]

    desenhar_poligono(
        tela,
        borda_clipping,
        VERDE
    )


    # =================================================
    # VIEWPORT 1 - MINIMAPA
    # =================================================

    M_minimapa = janela_viewport(
        janela_mundo,
        viewport_minimapa
    )


    desenhar_viewport(
        tela,
        M_minimapa,
        nave_transformada,
        cockpit_transformado,
        chama_transformada,
        viewport_minimapa,
        BRANCO
    )


    # =================================================
    # VIEWPORT 2 - ZOOM
    # =================================================

    largura_zoom = 100
    altura_zoom = 75


    janela_zoom = (

        x_nave
        - largura_zoom / 2,

        y_nave
        - altura_zoom / 2,

        x_nave
        + largura_zoom / 2,

        y_nave
        + altura_zoom / 2
    )


    # Matriz recalculada a cada frame

    M_zoom = janela_viewport(
        janela_zoom,
        viewport_zoom
    )


    desenhar_viewport(
        tela,
        M_zoom,
        nave_transformada,
        cockpit_transformado,
        chama_transformada,
        viewport_zoom,
        AMARELO
    )


    # =================================================
    # DEBUG - AABB
    # =================================================

    if mostrar_aabb:

        desenhar_aabb(
            tela,
            aabb_nave,
            VERDE
        )


        for x, y, w, h in predios:

            desenhar_aabb(
                tela,
                (
                    x,
                    y,
                    x + w,
                    y + h
                ),
                VERMELHO
            )


    # =================================================
    # TEXTOS
    # =================================================

    fonte = pygame.font.Font(
        None,
        24
    )

    fonte_pequena = pygame.font.Font(
        None,
        20
    )


    texto = fonte.render(
        "SETAS: mover | H: AABB | ESC: sair",
        True,
        BRANCO
    )

    tela.blit(
        texto,
        (15, 15)
    )


    # -------------------------------------------------
    # MINIMAPA
    # -------------------------------------------------

    titulo_minimapa = fonte_pequena.render(
        "MINIMAPA - MUNDO INTEIRO",
        True,
        BRANCO
    )

    tela.blit(
        titulo_minimapa,
        (
            viewport_minimapa[0],
            viewport_minimapa[1] - 20
        )
    )


    # -------------------------------------------------
    # ZOOM
    # -------------------------------------------------

    titulo_zoom = fonte_pequena.render(
        "ZOOM 2x - SEGUE A NAVE",
        True,
        AMARELO
    )

    tela.blit(
        titulo_zoom,
        (
            viewport_zoom[0],
            viewport_zoom[1] - 20
        )
    )


    # -------------------------------------------------
    # CLIPPING
    # -------------------------------------------------

    titulo_clipping = fonte_pequena.render(
        "COHEN-SUTHERLAND",
        True,
        VERDE
    )

    tela.blit(
        titulo_clipping,
        (
            janela_clipping[0],
            janela_clipping[1] - 20
        )
    )


    # =================================================
    # FINAL DO FRAME
    # =================================================

    pygame.display.flip()

    clock.tick(FPS)


pygame.quit()
sys.exit()
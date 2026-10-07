import numpy as np
import pygame

clip_atual = None  # (xmin, ymin, xmax, ymax) ou None

def setPixel(superficie, x, y, cor):
    global clip_atual
    x, y = int(x), int(y)

    if not (0 <= x < superficie.get_width() and 0 <= y < superficie.get_height()):
        return

    if clip_atual is not None:
        xmin, ymin, xmax, ymax = clip_atual
        if x < xmin or x > xmax or y < ymin or y > ymax:
            return
        
    superficie.set_at((x, y), cor)

def bresenham(superficie, x0, y0, x1, y1, cor):
    x0, y0 = int(x0), int(y0)
    x1, y1 = int(x1), int(y1)
    
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    ystep = 1 if dy >= 0 else -1
    dy = abs(dy)

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    y = y0
    for x in range(x0, x1 + 1):
        if steep:
            setPixel(superficie, y, x, cor)
        else:
            setPixel(superficie, x, y, cor)

        if d > 0:
            y += ystep
            d += incNE
        else:
            d += incE

def desenhar_poligono(superficie, pontos, cor_borda):
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        bresenham(superficie, x0, y0, x1, y1, cor_borda)

def scanline_fill(superficie, pontos, cor_preenchimento):
    if not pontos:
        return
        
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    n = len(pontos)

    for y in range(y_min, y_max):
        intersecoes_x = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]

            # Ignora arestas horizontais
            if y0 == y1:
                continue

            # Garante y0 < y1
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            # Regra Ymin <= y < Ymax
            if y < y0 or y >= y1:
                continue

            # Calcula interseção
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes_x.append(x)

        # Ordena interseções
        intersecoes_x.sort()

        # Preenche entre pares
        for i in range(0, len(intersecoes_x), 2):
            if i + 1 < len(intersecoes_x):
                x_inicio = int(round(intersecoes_x[i]))
                x_fim = int(round(intersecoes_x[i + 1]))

                for x in range(x_inicio, x_fim + 1):
                    setPixel(superficie, x, y, cor_preenchimento)

def scanline_texture(superficie, pontos, uvs, textura):
    """textura: matriz (altura, largura, 3|4); uvs em [0, 1], um por vértice."""
    th, tw = textura.shape[:2]
    largura, altura = superficie.get_size()
    n = len(pontos)
    y_min = int(min(p[1] for p in pontos))
    y_max = int(max(p[1] for p in pontos))

    pixels = pygame.surfarray.pixels3d(superficie)
    for y in range(max(0, y_min), min(altura, y_max)):
        intersecoes = []
        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]
            u0, v0 = uvs[i]
            u1, v1 = uvs[(i + 1) % n]
            if y0 == y1:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                u0, v0, u1, v1 = u1, v1, u0, v0
            if y < y0 or y >= y1:
                continue
            t = (y - y0) / (y1 - y0)
            intersecoes.append((x0 + t * (x1 - x0), u0 + t * (u1 - u0), v0 + t * (v1 - v0)))

        intersecoes.sort(key=lambda item: item[0])
        for i in range(0, len(intersecoes) - 1, 2):
            x_ini, u_ini, v_ini = intersecoes[i]
            x_fim, u_fim, v_fim = intersecoes[i + 1]
            if x_fim == x_ini:
                continue
            xs = np.arange(max(0, int(x_ini)), min(largura, int(x_fim) + 1))
            if xs.size == 0:
                continue
            t = (xs - x_ini) / (x_fim - x_ini)
            tx = np.clip(((u_ini + t * (u_fim - u_ini)) * (tw - 1)).astype(int), 0, tw - 1)
            ty = np.clip(((v_ini + t * (v_fim - v_ini)) * (th - 1)).astype(int), 0, th - 1)
            pixels[xs, y] = textura[ty, tx, :3]
    del pixels

def mundo_viewport(ponto, janela, viewport):
    Wxmin, Wymin, Wxmax, Wymax = janela
    Vxmin, Vymin, Vxmax, Vymax = viewport

    sx = (Vxmax - Vxmin) / (Wxmax - Wxmin)
    sy = (Vymax - Vymin) / (Wymax - Wymin)

    x, y = ponto
    return (x - Wxmin) * sx + Vxmin, (y - Wymin) * sy + Vymin

def transforma_poligono(pontos, janela, viewport):
    return [mundo_viewport(p, janela, viewport) for p in pontos]

def janela_com_zoom(centro, zoom, largura_base, altura_base, limites):
    """
    Janela do mundo centrada em `centro`, com tamanho (largura_base/zoom, altura_base/zoom).
    Zoom maior = janela menor = a mesma viewport mostra menos mundo, ampliado.
    A janela é deslocada (translação) para não sair de `limites` = (xmin, ymin, xmax, ymax).
    """
    w, h = largura_base / zoom, altura_base / zoom
    lx0, ly0, lx1, ly1 = limites
    x0 = max(lx0, min(centro[0] - w / 2, lx1 - w))
    y0 = max(ly0, min(centro[1] - h / 2, ly1 - h))
    return (x0, y0, x0 + w, y0 + h)

def desenhar_minimapa(superficie, beings, janela_mundo, viewport, cor_fundo, cor_borda, fundo=None):
    global clip_atual
    from src.engine.clipping import desenhar_poligono_recortado

    Vxmin, Vymin, Vxmax, Vymax = viewport
    clip_atual = viewport

    Wxmin, Wymin, Wxmax, Wymax = janela_mundo
    sy = (Vymax - Vymin) / (Wymax - Wymin)

    if fundo is None:
        pixels = pygame.surfarray.pixels3d(superficie)
        pixels[Vxmin:Vxmax + 1, Vymin:Vymax + 1] = cor_fundo
        del pixels
    else:
        textura, u0, u1, v0, v1 = fundo
        quad = [(Vxmin, Vymin), (Vxmax, Vymin), (Vxmax, Vymax + 1), (Vxmin, Vymax + 1)]
        scanline_texture(superficie, quad, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], textura)

        pixels = pygame.surfarray.pixels3d(superficie)
        area = pixels[Vxmin:Vxmax + 1, Vymin:Vymax + 1]
        np.multiply(area, 0.6, out=area, casting="unsafe")  # escurece o cenário para os bonecos aparecerem
        del area, pixels

    for being in beings:
        # fora da janela do mundo: nem entra no pipeline (importante com zoom alto)
        bw, bh = getattr(being, "width", 0), getattr(being, "height", 0)
        if being.x + bw < Wxmin or being.x > Wxmax or being.y + bh < Wymin or being.y > Wymax:
            continue
        if hasattr(being, "sprite") and hasattr(being.sprite, "matrix"):
            from src.engine.sprite import draw_sprite_scaled  # import local evita ciclo com rendering.py
            vx, vy = mundo_viewport((being.x, being.y), janela_mundo, viewport)
            altura_minimapa = max(1, round(being.height * sy))
            draw_sprite_scaled(superficie, being.sprite.matrix, int(vx), int(vy), altura_minimapa)
        else:
            for parte in being.get_polygons():
                vertices_view = transforma_poligono(parte["vertices"], janela_mundo, viewport)
                scanline_fill(superficie, vertices_view, parte["color"])
                desenhar_poligono_recortado(superficie, vertices_view, parte["color"], viewport)

    clip_atual = None  # fora disso, o resto da cena seria recortado também

    borda = [(Vxmin, Vymin), (Vxmax, Vymin), (Vxmax, Vymax), (Vxmin, Vymax)]
    desenhar_poligono(superficie, borda, cor_borda)
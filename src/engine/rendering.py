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

def mundo_viewport(ponto, janela, viewport):
    Wxmin, Wymin, Wxmax, Wymax = janela
    Vxmin, Vymin, Vxmax, Vymax = viewport

    sx = (Vxmax - Vxmin) / (Wxmax - Wxmin)
    sy = (Vymax - Vymin) / (Wymax - Wymin)

    x, y = ponto
    return (x - Wxmin) * sx + Vxmin, (y - Wymin) * sy + Vymin

def transforma_poligono(pontos, janela, viewport):
    return [mundo_viewport(p, janela, viewport) for p in pontos]

def desenhar_minimapa(superficie, beings, janela_mundo, viewport, cor_fundo, cor_borda):
    global clip_atual

    Vxmin, Vymin, Vxmax, Vymax = viewport
    clip_atual = viewport

    for y in range(Vymin, Vymax + 1):
        for x in range(Vxmin, Vxmax + 1):
            setPixel(superficie, x, y, cor_fundo)

    for being in beings:
        for parte in being.get_polygons():
            vertices_view = transforma_poligono(parte["vertices"], janela_mundo, viewport)
            scanline_fill(superficie, vertices_view, parte["color"])
            desenhar_poligono(superficie, vertices_view, parte["color"])

    clip_atual = None  # fora disso, o resto da cena seria recortado também

    borda = [(Vxmin, Vymin), (Vxmax, Vymin), (Vxmax, Vymax), (Vxmin, Vymax)]
    desenhar_poligono(superficie, borda, cor_borda)
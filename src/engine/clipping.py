from src.engine.rendering import bresenham

# Códigos de região (Cohen-Sutherland)
INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def codigo_regiao(x, y, xmin, ymin, xmax, ymax):
    codigo = INSIDE
    if x < xmin:
        codigo |= LEFT
    elif x > xmax:
        codigo |= RIGHT
    # Y cresce para baixo na tela
    if y < ymin:
        codigo |= TOP
    elif y > ymax:
        codigo |= BOTTOM
    return codigo


def cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    """Retorna (visivel, x0, y0, x1, y1) com o segmento recortado na janela."""
    c0 = codigo_regiao(x0, y0, xmin, ymin, xmax, ymax)
    c1 = codigo_regiao(x1, y1, xmin, ymin, xmax, ymax)

    while True:
        if not (c0 | c1):          # aceitação trivial
            return True, x0, y0, x1, y1
        if c0 & c1:                # rejeição trivial
            return False, 0, 0, 0, 0

        c_out = c0 if c0 else c1

        if c_out & TOP:
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
            y = ymin
        elif c_out & BOTTOM:
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
            y = ymax
        elif c_out & RIGHT:
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
            x = xmax
        else:  # LEFT
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
            x = xmin

        if c_out == c0:
            x0, y0 = x, y
            c0 = codigo_regiao(x0, y0, xmin, ymin, xmax, ymax)
        else:
            x1, y1 = x, y
            c1 = codigo_regiao(x1, y1, xmin, ymin, xmax, ymax)


def desenhar_linha_recortada(superficie, x0, y0, x1, y1, janela, cor):
    """janela = (xmin, ymin, xmax, ymax)"""
    xmin, ymin, xmax, ymax = janela
    visivel, rx0, ry0, rx1, ry1 = cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax)
    if visivel:
        bresenham(superficie, rx0, ry0, rx1, ry1, cor)


def desenhar_poligono_recortado(superficie, pontos, cor, janela):
    """Contorno de polígono em que cada aresta passa pelo Cohen-Sutherland."""
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        desenhar_linha_recortada(superficie, x0, y0, x1, y1, janela, cor)

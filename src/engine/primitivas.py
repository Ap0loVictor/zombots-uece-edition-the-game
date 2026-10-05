from src.engine.rendering import setPixel


def _simetria_circulo(superficie, cx, cy, x, y, cor):
    # Um ponto calculado no 1º octante vira 8 pontos (simetria)
    for px, py in ((x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)):
        setPixel(superficie, cx + px, cy + py, cor)


def circulo(superficie, cx, cy, raio, cor):
    """Circunferência pelo algoritmo do Ponto Médio (Bresenham para círculos)."""
    cx, cy, raio = int(cx), int(cy), int(raio)
    x = 0
    y = raio
    d = 1 - raio  # parâmetro de decisão inicial

    while x <= y:
        _simetria_circulo(superficie, cx, cy, x, y, cor)
        if d < 0:
            d += 2 * x + 3            # escolhe E
        else:
            d += 2 * (x - y) + 5      # escolhe SE
            y -= 1
        x += 1


def _simetria_elipse(superficie, cx, cy, x, y, cor):
    # Um ponto do 1º quadrante vira 4 pontos (simetria)
    setPixel(superficie, cx + x, cy + y, cor)
    setPixel(superficie, cx - x, cy + y, cor)
    setPixel(superficie, cx + x, cy - y, cor)
    setPixel(superficie, cx - x, cy - y, cor)


def elipse(superficie, cx, cy, rx, ry, cor):
    """Elipse (eixos alinhados) pelo algoritmo do Ponto Médio, em 2 regiões."""
    cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
    if rx <= 0 or ry <= 0:
        setPixel(superficie, cx, cy, cor)
        return

    rx2, ry2 = rx * rx, ry * ry
    x, y = 0, ry

    # ---- Região 1: inclinação |m| < 1 (anda em x) ----
    d1 = ry2 - rx2 * ry + 0.25 * rx2
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y
    while dx < dy:
        _simetria_elipse(superficie, cx, cy, x, y, cor)
        x += 1
        dx += 2 * ry2
        if d1 < 0:
            d1 += dx + ry2
        else:
            y -= 1
            dy -= 2 * rx2
            d1 += dx - dy + ry2

    # ---- Região 2: inclinação |m| >= 1 (anda em y) ----
    d2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        _simetria_elipse(superficie, cx, cy, x, y, cor)
        y -= 1
        dy -= 2 * rx2
        if d2 > 0:
            d2 += rx2 - dy
        else:
            x += 1
            dx += 2 * ry2
            d2 += dx - dy + rx2

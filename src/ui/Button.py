from src.engine.rendering import desenhar_poligono
from src.engine.fonte import desenhar_texto_centralizado
from src.engine.fill import scanline_fill_gradiente


class Button:
    """
    Botão retangular: preenchido com scanline e contornado com Bresenham.
    """

    def __init__(self, x, y, width, height, text, action):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action  # Valor devolvido ao Menu quando o botão é ativado
        self.selected = False

    def contains(self, pos):
        px, py = pos
        return (
            self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )

    def get_vertices(self):
        x1, y1 = self.x, self.y
        x2 = x1 + self.width
        y2 = y1 + self.height
        return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

    def draw(self, tela):
        if self.selected:
            # color = (20, 160, 75)
            color = ((70, 230, 120), (10, 110, 50)) 
            border_color = (100, 255, 140)
            text_color = (255, 255, 255)
        else:
            # color = (25, 40, 75)
            color = ((60, 85, 140), (15, 25, 50))  
            border_color = (120, 150, 200)
            text_color = (190, 200, 220)

        vertices = self.get_vertices()
        topo, base = color
        scanline_fill_gradiente(tela, vertices, [topo, topo, base, base])
        desenhar_poligono(tela, vertices, border_color)

        desenhar_texto_centralizado(
            tela,
            self.text,
            self.x + self.width // 2,
            self.y + self.height // 2,
            text_color,
            escala=2,
        )

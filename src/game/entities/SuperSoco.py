import math

from src.engine.transformacoes import translacao, rotacao, escala, multiplica_matrizes, aplica_transformacao
from src.engine.fill import scanline_fill_gradiente
from src.engine.primitivas import elipse

DIRECOES = {
    "right": (1, 0), "left": (-1, 0),
    "up": (0, -1), "down": (0, 1),
}



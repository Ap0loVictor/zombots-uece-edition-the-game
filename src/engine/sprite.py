import pygame
import numpy as np
from src.engine import rendering
from src.engine.rendering import setPixel

_ESCALADOS = {}

def load_png_matrix(path):
    image = pygame.image.load(path).convert_alpha()
    rgb = pygame.surfarray.array3d(image)        # (largura, altura, 3)
    alpha = pygame.surfarray.array_alpha(image)  # (largura, altura)
    return np.ascontiguousarray(np.dstack((rgb, alpha)).transpose(1, 0, 2))  # (altura, largura, 4)

def draw_sprite(surface, matrix, pos_x, pos_y):
    height, width, _ = matrix.shape

    surface_width = surface.get_width()
    surface_height = surface.get_height()

    start_x = max(0, -pos_x)
    start_y = max(0, -pos_y)

    end_x = min(width, surface_width - pos_x)
    end_y = min(height, surface_height - pos_y)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            color = matrix[y, x]

            if color[3] == 0:
                continue

            setPixel(surface,pos_x + x,pos_y + y,color)



def _escalar_sprite(matrix, target_height, flip_x):
    chave = (id(matrix), target_height, flip_x)
    if chave not in _ESCALADOS:
        h, w, _ = matrix.shape
        escala = target_height / h
        tw = round(w * escala)
        ys = np.minimum(h - 1, (np.arange(target_height) / escala).astype(int))
        xs = np.minimum(w - 1, (np.arange(tw) / escala).astype(int))
        if flip_x:
            xs = xs[::-1]
        _ESCALADOS[chave] = (matrix, matrix[np.ix_(ys, xs)])  # guarda a matriz original para o id não ser reaproveitado
    return _ESCALADOS[chave][1]

def draw_sprite_scaled(surface, matrix, pos_x, pos_y, target_height, flip_x=False):
    if matrix.shape[0] == 0 or target_height <= 0:
        return

    sprite = _escalar_sprite(matrix, target_height, flip_x)
    th, tw = sprite.shape[:2]

    min_x, min_y = 0, 0
    max_x, max_y = surface.get_width(), surface.get_height()
    clip = rendering.clip_atual  # o minimapa recorta o desenho pelo viewport
    if clip is not None:
        cxmin, cymin, cxmax, cymax = clip
        min_x, min_y = max(min_x, int(cxmin)), max(min_y, int(cymin))
        max_x, max_y = min(max_x, int(cxmax) + 1), min(max_y, int(cymax) + 1)

    x0, y0 = max(0, min_x - pos_x), max(0, min_y - pos_y)
    x1, y1 = min(tw, max_x - pos_x), min(th, max_y - pos_y)
    if x0 >= x1 or y0 >= y1:
        return

    recorte = sprite[y0:y1, x0:x1]
    opaco = (recorte[..., 3] > 0).T
    pixels = pygame.surfarray.pixels3d(surface)
    destino = pixels[pos_x + x0:pos_x + x1, pos_y + y0:pos_y + y1]
    destino[opaco] = recorte[..., :3].transpose(1, 0, 2)[opaco]
    del pixels
import pygame
import numpy as np
from src.engine.rendering import setPixel

def load_png_matrix(path):
    image = pygame.image.load(path).convert_alpha()

    width = image.get_width()
    height = image.get_height()

    matrix = np.zeros((height, width, 4), dtype=np.uint8)   

    for y in range(height):
        for x in range(width):
            matrix[y, x] = image.get_at((x, y))
    
    return matrix

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

def draw_sprite_scaled(surface, matrix, pos_x, pos_y, target_height):
    original_height, original_width, _ = matrix.shape

    if original_height == 0 or target_height <= 0:
        return

    scale_factor = target_height / original_height
    target_width = round(original_width * scale_factor)

    surface_width = surface.get_width()
    surface_height = surface.get_height()

    start_x = max(0, -pos_x)
    start_y = max(0, -pos_y)

    end_x = min(target_width, surface_width - pos_x)
    end_y = min(target_height, surface_height - pos_y)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):

            src_x = min(
                original_width - 1,
                int(x / scale_factor)
            )
            src_y = min(
                original_height - 1,
                int(y / scale_factor)
            )

            color = matrix[src_y, src_x]

            if color[3] == 0:
                continue

            setPixel(
                surface,
                pos_x + x,
                pos_y + y,
                tuple(map(int, color))
            )
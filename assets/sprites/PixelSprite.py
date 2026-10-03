from src.engine.sprite import load_png_matrix

class PixelSprite:
    def __init__(self, path):
        self.matrix = load_png_matrix(path)
        self.width = self.matrix.shape[1]
        self.height = self.matrix.shape[0]
from src.engine.sprite import load_png_matrix

class PixelSprite:
    def __init__(self, path):
        self.matrix = load_png_matrix(path)
        self.width = self.matrix.shape[1]
        self.height = self.matrix.shape[0]


class SpriteFrame:
    """Um frame individual recortado de uma sprite sheet (mesma interface mínima de PixelSprite)."""
    def __init__(self, matrix):
        self.matrix = matrix
        self.height, self.width = matrix.shape[:2]


def load_sprite_sheet_frames(path, frame_count):
    sheet = PixelSprite(path)
    frame_width = sheet.width // frame_count
    return [
        SpriteFrame(sheet.matrix[:, i * frame_width:(i + 1) * frame_width])
        for i in range(frame_count)
    ]
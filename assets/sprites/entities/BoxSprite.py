from assets.sprites.sprite import Sprite

BOX_COLOR = (241, 195, 56) # Alçafrão

BOX_POLYGON = [
    (0, 0),
    (25, 0),
    (25, 25),
    (0, 25)
]

class BoxSprite(Sprite):
    def __init__(self):
        super().__init__()
        self.parts = [
            {"name": "body", "vertices": BOX_POLYGON, "color": BOX_COLOR}
        ]

    def get_world_polygons(self, origin_x, origin_y):

        world_polygons = []
        for part in self.parts:
            transformed_vertices = []
            for vx, vy in part["vertices"]:
                wx = origin_x + vx
                wy = origin_y + vy
                transformed_vertices.append((wx, wy))
            
            world_polygons.append({
                "name": part["name"],
                "vertices": transformed_vertices,
                "color": part["color"]
            })
        return world_polygons

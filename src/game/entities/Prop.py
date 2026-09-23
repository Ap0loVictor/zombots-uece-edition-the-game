# Class to generalize non-living objects or NPCs.
class Prop:
    def __init__(self, spawn_x, spawn_y, width, height, hitbox):
        
        self.x = spawn_x
        self.y = spawn_y
        self.width = width
        self.height = height
        
        self.hitbox = hitbox


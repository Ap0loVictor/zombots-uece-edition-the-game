# Class to generalize living objects, NPCs or players.
class Entity:
    def __init__(self, spawn_x, spawn_y, width, height, health, hitbox=None):
        self.x = spawn_x
        self.y = spawn_y
        
        self.width = width
        self.height = height
        
        self.hitbox = hitbox # (offset_x, offset_y, width, height) ex: hitbox=(2, 4, 44, 12)
        
        self.health = health
        self.max_health = health
        self.alive = True

    def receive_damage(self, damage):
        self.health -= damage
        if self.health < 1:
            self.health = 0
            self.alive = False
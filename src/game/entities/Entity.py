# Class to generalize living objects, NPCs or players.
class Entity:
    def __init__(self, spawn_x, spawn_y, width, height, health):
        self.x = spawn_x
        self.y = spawn_y
        self.width = width
        self.height = height

        self.health = health
        self.max_health = health
        self.alive = True
    def recive_damage(self, damage):
        self.health = self.health - damage
        if self.health < 1:
            self.alive = False
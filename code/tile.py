import pygame
from settings import *


# Accepts graphics oof various sizes.
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        y_offset = HITBOX_OFFSET[sprite_type]
        self.image = surface
        # Resizes rect if object
        if sprite_type == "object":
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)
        # change the size of the hit-box of the tile.
        # top and bottom are a bit shorter, that way
        # it looks like the player is behind the tile.
        # shrinks 5 px up and 5 px down.
        self.hitbox = self.rect.inflate(0, y_offset)

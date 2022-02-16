import pygame
from settings import *
from tile import Tile
from player import Player
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade


class Level:
    def __init__(self):
        # get the display surface
        self.player = None
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        # sprite group setup
        # group for sprites that will be drawn
        self.visible_sprites = YSortCameraGroup()
        # group for sprites that the player can collide with
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        # weapons
        self.attack_sprites = pygame.sprite.Group()
        # enemies
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):
        layouts = {
            "boundary": import_csv_layout("../map/map_FloorBlocks.csv"),
            "grass": import_csv_layout("../map/map_Grass.csv"),
            "object": import_csv_layout("../map/map_Objects.csv"),
            # enemies and player
            "entities": import_csv_layout("../map/map_Entities.csv")
        }

        graphics = {
            "grass": import_folder("../graphics/Grass"),
            "objects": import_folder("../graphics/objects")
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != "-1":  # there is something
                        # position * tilesize
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        if style == "boundary":
                            Tile((x, y), [self.obstacle_sprites], "invisible")

                        if style == "grass":
                            # create grass style
                            random_grass_image = choice(graphics["grass"])
                            # Grass is visible and collidable
                            Tile(
                                (x, y),
                                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                "grass",
                                random_grass_image)

                        if style == "object":
                            # create object tile
                            surf = graphics["objects"][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], "object", surf)

                        if style == "entities":
                            # Spawn player
                            if col == "394":
                                self.player = Player(
                                    (x, y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                            else:  # spawn enemies
                                if col == "390":
                                    monster_name = "bamboo"
                                elif col == "391":
                                    monster_name = 'spirit'
                                elif col == "392":
                                    monster_name = "raccoon"
                                else:
                                    monster_name = "squid"
                                Enemy(monster_name,
                                      (x, y),
                                      [self.visible_sprites,
                                       self.attackable_sprites],
                                      self.obstacle_sprites,
                                      self.damage_player,
                                      self.trigger_death_particles,
                                      self.add_exp)

    def create_magic(self, style, strength, cost):
        if style == "heal":
            self.magic_player.heal(
                self.player,
                strength,
                cost,
                [self.visible_sprites]
            )

        if style == "flame":
            self.magic_player.flame(
                self.player,
                cost,
                [self.visible_sprites,
                 self.attack_sprites]
            )

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        # If you have a weapon out, remove it.
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        # check if anything is in attack sprite
        if self.attack_sprites:
            # cycle all attack sprites
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                # check if they are colliding with attackable sprites
                if collision_sprites:  # there is collision
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == "grass":
                            # get grass position
                            pos = target_sprite.rect.center
                            # get grass offset
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])

                            # Destroy attackable sprite
                            target_sprite.kill()
                        else:
                            # what the player is doing, what attack are we using
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        # timer after player is hit,
        # so we can't attack player
        # multiple times in 1 attack
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            # spawn particles
            self.animation_player.create_particles(
                attack_type,
                self.player.rect.center,
                [self.visible_sprites]
            )

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(
            particle_type, pos, self.visible_sprites
        )

    def add_exp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    # update and draw the game
    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            # display menu
            self.upgrade.display()
        else:
            # run the game
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()


# Put player right in the middle of the window.
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        # put player in middle
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load("../graphics/tilemap/ground.png").convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    # We draw the image in the rect of the sprite
    # We can use a vector2 to offset the
    # rect and thus blit the image somewhere else
    # offset vector is our camera and control
    # where are the sprites going to be drawn.
    # Each sprite gets a hit-box for the collision.
    # The drawing function needs to know the order
    # of the sprites.
    def custom_draw(self, player):
        # getting the offset for the camera
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        # order sprites by y instead when they were created
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        # get enemy sprites from sprites
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, "sprite_type") and sprite.sprite_type == "enemy"]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)

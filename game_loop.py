from functools import lru_cache

import pygame
import sys
import time
import random

from pygame import Surface, image

from entities.base_entity import BaseDrop
from scripts import (
    readable_classes,
    config,
)
from entities import player, enemy
from scripts.readable_classes import XYFloat
from scripts.pygame_utils import calculate_pathing, tile_background, default_font
from ui.overlay import Overlay
from weapons.weapons import Pistol
from weapons.base_weapon import BaseEffect


class Game:
    def __init__(self):
        # Display window
        self.game_screen: pygame.display = pygame.display.set_mode(
            (config.WINDOW_SIZE.x, config.WINDOW_SIZE.y)
        )

        # Smaller resolution display that will be up scaled to our window
        self.game_display: pygame.surface = pygame.Surface(
            (config.DISPLAY_SIZE.x, config.DISPLAY_SIZE.y)
        )

        # Window name
        pygame.display.set_caption("Python Survivors")

        # Player inputs
        # self.camera_movement: readable_classes.DirectionBool = (
        #     readable_classes.DirectionBool(False, False, False, False)
        # )
        self.player_input: readable_classes.DirectionBool = (
            readable_classes.DirectionBool(False, False, False, False)
        )
        self.previous_player_input: readable_classes.DirectionBool = (
            readable_classes.DirectionBool(False, False, False, False)
        )

        # Entities
        self.player = player.Player(
            location=self.get_screen_center(),
        )
        self.enemies: list[enemy.Enemy] = []
        self.drops: list[BaseDrop] = []

        # Camera
        self.scroll: readable_classes.XYFloat = readable_classes.XYFloat(0, 0)
        self.zoom: float = 2.0

        # Tile Map
        self.level = 0
        # self.load_level()

        # Framerate
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.framerate: int = 240
        self.last_time: float = time.time()
        self.delta_time: float = time.time()
        self.total_time: float = 0
        self.framerate_font = default_font(40)

        self.overlay: Overlay = Overlay(self.game_display, self.player)

        self.paused = False

    def load_level(self):
        ...
        # self.tile_map.load(f"data/maps/{self.level}.json")
        # if len(self.tile_map.tiles) == 0:
        #     self.tile_map.generate(self.grid_size)

    def display_framerate(self):
        rate_text = self.framerate_font.render(
            str(round(self.clock.get_fps(), 2)), True, (0, 0, 0)
        )
        self.game_display.blit(rate_text, (0, 0))

    def calculate_delta_time(self):
        now = time.time()
        self.delta_time = now - self.last_time
        self.last_time = now
        self.total_time += self.delta_time

    # def calculate_camera(self) -> readable_classes.XYInt:
    #     self.scroll.x += (self.camera_movement.right - self.camera_movement.left) * 2
    #     self.scroll.x = max(
    #         min(self.scroll.x, config.DISPLAY_SIZE.x),
    #         # -self.tile_size
    #         - (
    #             self.game_display.get_width() / 2 * self.zoom
    #             # - self.game_display.get_width() / 2 * self.zoom
    #         ),
    #     )
    #     self.scroll.y += (self.camera_movement.down - self.camera_movement.up) * 2
    #     render_scroll = readable_classes.XYInt(int(self.scroll.x), int(self.scroll.y))
    #     return render_scroll

    def get_screen_center(self) -> XYFloat:
        return XYFloat(
            self.game_display.get_width() / 2, self.game_display.get_height() / 2
        )

    def get_user_input(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Click
                # case pygame.MOUSEBUTTONDOWN:
                #     match event.button:
                #         case 1:  # Left click
                #             self.player_input.left_click = True
                #         case 3:  # Right click
                #             self.player_input.right_click = True
                # case 4:  # Sroll Up
                #     self.zoom = self.zoom * 2.0 if self.zoom < 4.0 else 4.0
                # case 5:  # Scroll down
                #     self.zoom = self.zoom / 2.0 if self.zoom > 1.0 else 1.0

                # case pygame.MOUSEBUTTONUP:
                #     match event.button:
                #         case 1:  # Left click
                #             self.player_input.left_click = False
                #         case 3:  # Right click
                #             self.player_input.right_click = False

                # Key Press
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LEFT | pygame.K_a:
                            self.player_input.left = True
                            self.player.flip_surface = False
                        case pygame.K_RIGHT | pygame.K_d:
                            self.player_input.right = True
                            self.player.flip_surface = True
                        case pygame.K_UP | pygame.K_w | pygame.K_SPACE:
                            self.player_input.up = True
                        case pygame.K_DOWN | pygame.K_s:
                            self.player_input.down = True
                        # case pygame.K_o:
                        #     self.framerate = 60 if not self.framerate == 60 else 240
                        case pygame.K_g:
                            self.player.weapon_slots[0].effects.append(
                                BaseEffect(
                                    damage_flat_bonus=1,
                                    damage_multiplier=5,
                                )
                            )
                        case pygame.K_ESCAPE:
                            self.paused = not self.paused
                        # case pygame.K_SPACE:
                        #     self.player

                # Key Release
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_LEFT | pygame.K_a:
                            self.player_input.left = False
                        case pygame.K_RIGHT | pygame.K_d:
                            self.player_input.right = False
                        case pygame.K_UP | pygame.K_w | pygame.K_SPACE:
                            self.player_input.up = False
                        case pygame.K_DOWN | pygame.K_s:
                            self.player_input.down = False

    def draw_screen(self):
        self.game_screen.blit(
            pygame.transform.scale(self.game_display, self.game_screen.get_size()),
            (0, 0),
        )
        pygame.display.update()

    def update_player(self):
        # Move player
        if self.player_input.left:
            self.player.location.x -= self.player.speed * self.delta_time
        if self.player_input.right:
            self.player.location.x += self.player.speed * self.delta_time
        if self.player_input.up:
            self.player.location.y -= self.player.speed * self.delta_time
        if self.player_input.down:
            self.player.location.y += self.player.speed * self.delta_time


    def update_enemies(self):
        for enemy_character in self.enemies:
            new_location = calculate_pathing(
                enemy_character.location,
                self.player.location,
                enemy_character.speed,
                self.delta_time,
            )

            if enemy_character.location.x < new_location.x:
                enemy_character.flip_surface = True
            else:
                enemy_character.flip_surface = False

            enemy_character.location = new_location

            if enemy_character.get_rect().colliderect(self.player.get_rect()):
                self.player.health -= 1

    def update_drops(self):
        for drop in self.drops.copy():
            if drop.get_rect().colliderect(self.player.get_rect()):
                drop.pickup(self.player)
                self.drops.remove(drop)
                continue

    def create_enemies(self):
        safe_area = 200
        while len(self.enemies) < 30:
            while new_location := XYFloat(
                random.randint(0, config.DISPLAY_SIZE.x),
                random.randint(0, config.DISPLAY_SIZE.y),
            ):
                if (
                    new_location.x < self.player.location.x - safe_area
                    or new_location.x > self.player.location.x + safe_area
                ) and (
                    new_location.y < self.player.location.y - safe_area
                    or new_location.y > self.player.location.y + safe_area
                ):
                    break
            self.enemies.append(enemy.Enemy(location=new_location, health=2))

    @lru_cache
    def create_background(self) -> Surface:
        return tile_background(
            image.load("assets/background_brick.png"), alternate_rows=True
        )

    def draw_everything(self):
        for drop in self.drops:
            self.game_display.blit(drop.surface, drop.location.to_tuple())

        for enemy_character in self.enemies:
            self.game_display.blit(
                enemy_character.surface, enemy_character.location.to_tuple()
            )

        for weapon in self.player.weapon_slots:
            weapon.update(
                self.delta_time if not self.paused else 0,
                self.player.location_center,
                self.enemies,
                self.game_display,
                self.drops,
            )

        self.game_display.blit(self.player.surface, self.player.location.to_tuple())

        self.overlay.update()

    def run(self):
        self.player.weapon_slots.append(Pistol())

        while True:
            self.create_enemies()

            self.calculate_delta_time()

            # Clear the screen
            self.game_display.fill((255, 255, 255))
            self.game_display.blit(
                self.create_background(),
                (0, 0),
            )

            # Get player input
            self.previous_player_input = self.player_input.copy()
            self.get_user_input()

            # Update all entities
            if not self.paused:
                self.update_drops()
                self.update_enemies()
                self.update_player()

            # Draw everything
            self.draw_everything()
            if self.player.health <= 0:
                break

            self.display_framerate()
            self.draw_screen()
            self.clock.tick(self.framerate)

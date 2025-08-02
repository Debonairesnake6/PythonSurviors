import pygame.transform
from pygame import Surface, FRect
from entities.enemy import Enemy
from scripts.readable_classes import XYFloat
from scripts.pygame_utils import (
    calculate_pathing,
    calculate_distance,
    location_reached,
    line_set_distance,
)
from scripts.animation import Animation
from entities.base_entity import BaseDrop
from icecream import ic
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.player import Player
    from scripts.collision_system import WeaponCollisionHelper


class BaseEffect:
    def __init__(
        self,
        damage_flat_bonus: float = None,
        damage_multiplier: float = None,
        ammo_speed_flat_bonus: float = None,
        ammo_speed_multiplier: float = None,
    ):
        self.damage_flat_bonus = damage_flat_bonus
        self.damage_multiplier = damage_multiplier
        self.ammo_speed_flat_bonus = ammo_speed_flat_bonus
        self.ammo_speed_multiplier = ammo_speed_multiplier


class BaseAmmo:
    def __init__(
        self,
        target_location: XYFloat,
        current_location: XYFloat,
        base_damage: float,
        base_ammo_speed: float,
        surface: Surface,
        effects: list[BaseEffect],
        size: float = 1,
    ):
        self.base_damage = base_damage
        self.base_ammo_speed = base_ammo_speed
        self.surface = pygame.transform.scale(surface, (size * XYFloat.from_tuple(surface.get_size())).to_tuple())
        self.base_surface = surface.copy()
        self._base_surface_size = surface.get_size()
        self.effects = effects

        self.target_location = target_location
        self.current_location = current_location - XYFloat.from_tuple(self.surface.get_size()) / 2
        self.size = size

    @property
    def damage(self) -> float:
        damage = self.base_damage
        for effect in self.effects:
            if effect.damage_flat_bonus is not None:
                damage += effect.damage_flat_bonus

        for effect in self.effects:
            if effect.damage_multiplier is not None:
                damage *= effect.damage_multiplier

        return damage

    @property
    def ammo_speed(self) -> float:
        ammo_speed = self.base_ammo_speed
        for effect in self.effects:
            if effect.ammo_speed_flat_bonus is not None:
                ammo_speed += effect.ammo_speed_flat_bonus

        for effect in self.effects:
            if effect.ammo_speed_multiplier is not None:
                ammo_speed *= effect.ammo_speed_multiplier

        return ammo_speed


    def location_reached(self, delta_time: float) -> bool:
        """
        Update the projectile location
        :param delta_time:
        :return: If the projectile arrived at the target
        """
        if location_reached(
            self.current_location,
            self.target_location,
            self.base_ammo_speed,
            delta_time,
        ):
            return True

        self.current_location = calculate_pathing(
            self.current_location,
            self.target_location,
            self.base_ammo_speed,
            delta_time,
        )

        return False

    def get_rect(self) -> FRect:
        return FRect(self.current_location.to_tuple(), self.surface.get_rect().size)

    def effect_enemy(self, enemy: Enemy):
        ic(f"Hit: {enemy.__class__.__name__}\t|\tDamage: {self.damage}")
        enemy.health -= self.damage


class BaseWeapon:
    def __init__(
        self,
        cooldown: float,
        attack_range: float,
        damage_multiplier: float,
        ammo_speed_multiplier: float,
        icon: Surface,
        ammo: BaseAmmo,
        effects: list[BaseEffect],
    ):
        self.cooldown = cooldown
        self.current_cooldown = cooldown

        self.attack_range = attack_range

        self.damage_multiplier = damage_multiplier

        self.ammo_speed_multiplier = ammo_speed_multiplier

        self.icon = icon

        self.ammo = ammo
        self.ammo_instance = ammo(XYFloat(0, 0), XYFloat(0, 0))
        self.active_ammo: list[BaseAmmo] = []
        self.damage_text: list[Animation] = []

        self.effects: list[BaseEffect] = effects

    def update(
        self,
        delta_time: float,
        player: "Player",
        enemies: list[Enemy],
        game_display: Surface,
        drops: list[BaseDrop],
    ) -> None:
        """Legacy update method - kept for backwards compatibility"""
        if self.current_cooldown > 0:
            self.current_cooldown = max(self.current_cooldown - delta_time, 0)
        else:
            self.fire_weapon(player.location_center, enemies)

        for ammo in self.active_ammo.copy():
            game_display.blit(ammo.surface, ammo.current_location)

            if delta_time == 0:
                continue
            elif ammo.location_reached(delta_time):
                self.active_ammo.remove(ammo)
            elif enemy := self.hit_enemy(ammo, enemies):
                self.active_ammo.remove(ammo)

                ammo.effect_enemy(enemy)

                damage_animation = enemy.damage_font.render(
                    str(ammo.damage), True, (0, 0, 0)
                )
                self.damage_text.append(
                    Animation(damage_animation, 0.25, location=enemy.location)
                )

                if enemy.health <= 0:
                    if drop := enemy.die():
                        drops.append(drop)
                    enemies.remove(enemy)
                    player.kills += 1

        for animation in self.damage_text.copy():
            if next_frame := animation.next_frame(delta_time):
                game_display.blit(next_frame, animation.location.to_tuple())
            else:
                self.damage_text.remove(animation)

    def update_with_collision_system(
            self,
            delta_time: float,
            player: "Player",
            enemies: list[Enemy],
            game_display: Surface,
            drops: list[BaseDrop],
            collision_helper: "WeaponCollisionHelper",
    ) -> None:
        """New update method using the collision system"""
        # Handle weapon cooldown and firing
        if self.current_cooldown > 0:
            self.current_cooldown = max(self.current_cooldown - delta_time, 0)
        else:
            self.fire_weapon(player, enemies)

        # Register all active ammo with the collision system
        collision_helper.register_ammo(self.active_ammo)

        # Update ammo positions and render them
        for ammo in self.active_ammo.copy():
            game_display.blit(ammo.surface, ammo.current_location.to_tuple())

            if delta_time == 0:
                continue

            # Check if ammo has reached its target location
            if ammo.location_reached(delta_time):
                self.active_ammo.remove(ammo)
                continue

        # Process collisions after all weapons have registered their ammo
        # This is called once per frame in the game loop
        if collision_helper.all_ammo:  # Only process if there's ammo to check
            collision_results = collision_helper.process_all_collisions()

            # Handle collision results
            for ammo, enemy in collision_results.items():
                if ammo in self.active_ammo:  # Make sure this weapon owns this ammo
                    self.handle_ammo_hit(ammo, enemy, enemies, drops, player)

        # Update damage text animations
        for animation in self.damage_text.copy():
            if next_frame := animation.next_frame(delta_time):
                game_display.blit(next_frame, animation.location.to_tuple())
            else:
                self.damage_text.remove(animation)

    def handle_ammo_hit(
            self,
            ammo: BaseAmmo,
            enemy: Enemy,
            enemies: list[Enemy],
            drops: list[BaseDrop],
            player: "Player"
    ):
        """Handle what happens when ammo hits an enemy"""
        self.active_ammo.remove(ammo)

        ammo.effect_enemy(enemy)

        # Create damage text animation
        damage_animation = enemy.damage_font.render(
            str(int(ammo.damage)), True, (0, 0, 0)
        )
        self.damage_text.append(
            Animation(damage_animation, 0.25, location=enemy.location)
        )

        # Handle enemy death
        if enemy.health <= 0:
            if drop := enemy.die():
                drops.append(drop)
            if enemy in enemies:
                enemies.remove(enemy)
                player.kills += 1

    @staticmethod
    def hit_enemy(ammo: BaseAmmo, enemies: list[Enemy]) -> Enemy | None:
        """Legacy collision detection - kept for backwards compatibility"""
        for enemy in enemies:
            if ammo.get_rect().colliderect(enemy.get_rect()):
                return enemy
        return None

    def fire_weapon(self, player: 'Player', enemies: list[Enemy]):
        player_location = player.location_center
        if target_location := self.get_closest_enemy_location(player_location, enemies):
            self.current_cooldown = self.cooldown
            # noinspection PyCallingNonCallable
            new_projectile = self.ammo(
                target_location=line_set_distance(
                    player_location.copy(),
                    target_location.copy(),
                    self.attack_range,
                ),
                current_location=player_location.copy(),
                effects=self.effects,
                size=player.ammo_size,
            )
            new_projectile.base_damage *= self.damage_multiplier
            new_projectile.base_ammo_speed *= self.ammo_speed_multiplier
            self.active_ammo.append(new_projectile)

    def get_closest_enemy_location(
        self, player_location: XYFloat, enemies: list[Enemy]
    ) -> XYFloat | None:
        closest_enemy: Enemy | None = None

        for enemy in enemies:
            if (
                calculate_distance(player_location.copy(), enemy.location_center)
                > self.attack_range
            ):
                continue
            if closest_enemy is None:
                closest_enemy = enemy
                continue

            if calculate_distance(player_location, enemy.location) < calculate_distance(
                player_location, closest_enemy.location
            ):
                closest_enemy = enemy

        if closest_enemy is not None:
            return closest_enemy.location_center
        return None
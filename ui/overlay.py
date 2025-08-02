from functools import lru_cache

from pygame import Surface
from entities.base_entity import BaseEntity
from scripts.readable_classes import XYFloat, XYInt, PlayerMouse
from scripts.pygame_utils import create_surface, create_font_surface, time_to_string, calculate_inner_picture_size
from scripts.config import DISPLAY_SIZE
from typing import TYPE_CHECKING, Callable
import random

if TYPE_CHECKING:
    from entities.player import Player


class BaseUIElement(BaseEntity):
    def __init__(
        self,
        name: str,
        surface: Surface = None,
        location: XYFloat = None,
        player: "Player" = None,
        logging: bool = False,
        parent_location: XYFloat = None,
    ):
        super().__init__(surface, location, logging, name=name)
        self.player = player
        self.base_surface = self.surface
        self.layers: list[BaseUIElement] = []
        self.parent_location = parent_location if parent_location else XYFloat(0, 0)

    @property
    def absolute_location(self):
        return self.parent_location + self.location

    @property
    def full_surface(self):
        return self.surface

    @full_surface.setter
    def full_surface(self, surface: Surface):
        self.surface = surface

    @full_surface.getter
    def full_surface(self):
        try:
            new_surface = self.base_surface.copy()
        except AttributeError:
            return self.surface
        for layer in self.layers:
            new_surface.blit(layer.full_surface, layer.location)
        return new_surface

    def update(self, *args, **kwargs):
        for layer in self.layers:
            layer.update()

    def clicked(self, *args, **kwargs):
        return False


class HotBarUIElement(BaseUIElement):
    def __init__(
            self,
            size: XYInt = XYInt(50, 50),
            title_text: str = "NOT YET IMPLEMENTED",
            parent_location: XYFloat = None,
            location: XYFloat = XYFloat(0, 0),
            player: "Player" = None,
            name: str = None,
            **kwargs,
    ):
        self.size = size
        self.title_text = title_text
        self.base_surface = self.background().surface.copy()
        self.player = player
        self.update()

        super().__init__(name, self.base_surface, location, player, parent_location=parent_location)

    def update(
        self,
        *args,
        **kwargs,
    ):
        self.layers = [
            self.background(),
            self.title(),
            self.amount(),
        ]

    @lru_cache
    def background(self) -> BaseUIElement:
        background_surface = create_surface(size=self.size, colour=(100, 100, 100))
        return BaseUIElement(surface=background_surface, location=XYFloat(0, 0),
                             name=self.name if hasattr(self, 'name') else None)

    @lru_cache
    def title_surface(self):
        return create_font_surface(
            text=self.title_text, size=35, colour=(200, 200, 200)
        )

    @lru_cache
    def title(self) -> BaseUIElement:
        font_surface = self.title_surface()
        location = XYFloat(
            self.background().surface.get_width() // 2 - font_surface.get_width() // 2,
            self.background().surface.get_height() // 3 - font_surface.get_height(),
        )
        return BaseUIElement(
            surface=font_surface,
            location=location,
            name=self.name if hasattr(self, 'name') else None,
        )

    def amount_surface(self) -> Surface:
        return create_font_surface(
            text=self.determine_amount(), size=45, colour=(200, 200, 200)
        )

    def amount(self) -> BaseUIElement:
        amount_surface = self.amount_surface()
        location = XYFloat(
            self.background().surface.get_width() // 2
            - amount_surface.get_width() // 2,
            self.background().surface.get_height() // 2
            - amount_surface.get_height() // 4,
        )
        return BaseUIElement(surface=amount_surface, location=location, logging=False,
                             name=self.name if hasattr(self, 'name') else None)

    def determine_amount(self) -> str:
        return "NOT IMPLEMENTED"


class Experience(HotBarUIElement):
    def determine_amount(self) -> str:
        return f"{self.player.experience}/{self.player.next_level_experience}"


class Money(HotBarUIElement):
    def determine_amount(self) -> str:
        return str(self.player.money)


class Level(HotBarUIElement):
    def determine_amount(self) -> str:
        return str(self.player.level)


class Resources(BaseUIElement):
    def __init__(self, location: XYFloat, player: "Player"):
        size = XYInt(
            DISPLAY_SIZE.x // 3,
            DISPLAY_SIZE.y // 10,
        )
        surface = create_surface(size=size, colour=(0, 0, 0))
        super().__init__("Resources", surface, location, player)

        self.create_money()
        self.create_experience()
        self.create_level()

    def create_money(self):
        self.layers.append(
            Money(
                size=XYInt(
                    (self.surface.size[0] - 10) // 3 - 5,
                    self.surface.size[1] - 10,
                ),
                title_text="Money",
                location=XYFloat(5, 5),
                player=self.player,
            )
        )

    def create_experience(self):
        self.layers.append(
            Experience(
                size=XYInt(
                    (self.surface.size[0] - 10) // 3,
                    self.surface.size[1] - 10,
                ),
                title_text="Experience",
                location=XYFloat(
                    (self.surface.size[0] - 10) // 3 + 5,
                    5,
                ),
                player=self.player,
            )
        )

    def create_level(self):
        self.layers.append(
            Level(
                size=XYInt(
                    (self.surface.size[0] - 10) // 3 - 5,
                    self.surface.size[1] - 10,
                ),
                title_text="Level",
                location=XYFloat(
                    ((self.surface.size[0] - 10) // 3) * 2 + 10,
                    5,
                ),
                player=self.player,
            )
        )


class PauseMenu(BaseUIElement):
    def __init__(self):
        self.text_surface = create_font_surface(
            text="Paused", size=400, colour=(0, 0, 0)
        )
        surface = create_surface(
            size=XYInt.from_tuple(self.text_surface.get_size()),
        )
        location = XYFloat(
            (DISPLAY_SIZE.x - surface.get_width()) // 2,
            (DISPLAY_SIZE.y - surface.get_height()) // 2,
        )
        super().__init__("PauseMenu", surface, location)

        self.add_paused_text()

    def add_paused_text(self):
        self.layers = [
            BaseUIElement(
                surface=self.text_surface,
                location=XYFloat(
                    (self.surface.get_width() - self.text_surface.get_width()) // 2,
                    (self.surface.get_height() - self.text_surface.get_height()) // 2,
                ),
                name=self.name,
            )
        ]


class TimeClock(BaseUIElement):
    def __init__(self, location: XYFloat):
        size = XYInt(
            DISPLAY_SIZE.x // 10,
            DISPLAY_SIZE.y // 20,
        )
        surface = create_surface(
            size=size,
        )
        super().__init__("TimeClock", surface, location)
        self.logging = False

    @staticmethod
    @lru_cache(maxsize=1)
    def _cached_surface(total_time: float):
        return create_font_surface(
            text=time_to_string(total_time), size=40, colour=(0, 0, 0)
        )

    @lru_cache(maxsize=1)
    def _cached_element(self, text_surface: Surface):
        return BaseUIElement(
                surface=text_surface,
                location=XYFloat(
                    (self.surface.get_width() - text_surface.get_width()) // 2,
                    0,
                ),
                name=self.name,
            )

    @lru_cache(maxsize=10)
    def update(self, *args, total_time: float = 0, **kwargs):
        text_surface = self._cached_surface(total_time)
        self.layers = [
            self._cached_element(text_surface),
        ]


class Button(HotBarUIElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LevelOption(Button):
    def __init__(self, size: XYInt, location: XYFloat, player: 'Player', parent_location: XYFloat, **kwargs):
        self.reward: Callable | None = None
        self.reward_description: str = ""
        self.player = player

        # Generate the reward and get title_text
        self.determine_amount()

        # Now call parent with all required arguments
        super().__init__(
            size=size,
            title_text=self.title_text,
            location=location,
            player=player,
            parent_location=parent_location,
            **kwargs
        )

    def determine_amount(self) -> str:
        if not self.reward_description:
            return self.get_random_reward()
        return self.reward_description

    def get_random_reward(self):
        # Calculate scaling bonuses based on player level
        level_multiplier = 1 + (self.player.level - 1) * 0.1  # 10% more per level

        # Get current stats for before/after display
        current_attack_speed = self.player.weapon_slots[0].cooldown if self.player.weapon_slots else 1.0
        current_move_speed = self.player.speed
        current_ammo_size = self.player.ammo_size
        current_health = self.player.health

        # Calculate bonuses
        attack_speed_bonus = 0.20 + (0.05 * level_multiplier)  # 15-20%+ scaling
        move_speed_bonus = 0.08 + (0.02 * level_multiplier)  # 8-10%+ scaling
        ammo_size_bonus = 0.20 + (0.03 * level_multiplier)  # 12-15%+ scaling
        health_bonus = max(1, int(level_multiplier))  # +1 health minimum, scales with level
        damage_bonus = 0.2 + (0.1 * level_multiplier)  # 20-30%+ scaling
        range_bonus = 0.1 + (0.05 * level_multiplier)  # 10-15%+ scaling

        # Calculate after values
        new_attack_speed = current_attack_speed / (1 + attack_speed_bonus)
        new_move_speed = current_move_speed * (1 + move_speed_bonus)
        new_ammo_size = current_ammo_size * (1 + ammo_size_bonus)
        new_health = current_health + health_bonus

        def atk_speed():
            for weapon in self.player.weapon_slots:
                weapon.cooldown /= (1 + attack_speed_bonus)

        def mov_speed():
            self.player.speed *= (1 + move_speed_bonus)

        def ammo_size():
            self.player.ammo_size *= (1 + ammo_size_bonus)

        def max_health():
            self.player.health += health_bonus

        def damage():
            for weapon in self.player.weapon_slots:
                weapon.damage_multiplier *= (1 + damage_bonus)

        def attack_range():
            for weapon in self.player.weapon_slots:
                weapon.attack_range *= (1 + range_bonus)

        rewards = {
            'Attack Speed': {
                'title': 'Attack',
                'description': f'+{attack_speed_bonus * 100:.0f}% Speed\n{current_attack_speed:.2f}s → {new_attack_speed:.2f}s',
                'function': atk_speed
            },
            'Movement Speed': {
                'title': 'Movement',
                'description': f'+{move_speed_bonus * 100:.0f}% Speed\n{current_move_speed:.0f} → {new_move_speed:.0f}',
                'function': mov_speed
            },
            'Ammo Size': {
                'title': 'Ammo',
                'description': f'+{ammo_size_bonus * 100:.0f}% Size\n{current_ammo_size:.1f}x → {new_ammo_size:.1f}x',
                'function': ammo_size
            },
            'Max Health': {
                'title': 'Health',
                'description': f'+{health_bonus} Max HP\n{current_health} → {new_health}',
                'function': max_health
            },
            'Damage': {
                'title': 'Damage',
                'description': f'+{damage_bonus * 100:.0f}% Damage\nAll weapons',
                'function': damage
            },
            'Attack Range': {
                'title': 'Range',
                'description': f'+{range_bonus * 100:.0f}% Range\nAll weapons',
                'function': attack_range
            }
        }

        reward_name = random.choice(list(rewards.keys()))
        reward_data = rewards[reward_name]

        self.title_text = reward_data['title']
        self.reward = reward_data['function']
        self.reward_description = reward_data['description']
        return reward_data['description']


class LevelMenu(BaseUIElement):
    def __init__(self, player: 'Player'):
        self.border = 5
        self.rows = 1
        size = XYInt(
            DISPLAY_SIZE.x // 2,
            DISPLAY_SIZE.y // 2,
        )
        location = XYFloat(
            DISPLAY_SIZE.x // 4,
            DISPLAY_SIZE.y // 4,
        )
        surface = create_surface(size=size, colour=(0, 0, 0))
        super().__init__("LevelMenu", surface, location, player)
        self.choice_made = False

    def get_option(self):
        size = calculate_inner_picture_size(
                parent_size=XYInt.from_tuple(self.surface.get_size()),
                rows=self.rows,
                columns=self.player.level_options,
                border=self.border,
            )
        return LevelOption(
            size=size,
            location=XYFloat(
                self.border + self.border * len(self.layers) + len(self.layers) * size.x,
                self.border
            ),
            player=self.player,
            parent_location=self.location,
        )

    def determine_options(self, level: int):
        # Remove @lru_cache to generate fresh options each level
        self.layers = []
        for _ in range(self.player.level_options):
            self.layers.append(self.get_option())

    def update(self, *args, **kwargs):
        # Only generate options if we don't have any (first time showing menu)
        if not self.layers:
            self.determine_options(int(self.player.level))
        super().update()

    def clicked(self, location: XYInt, *args, **kwargs):
        for option in self.layers:
            if option.absolute_location.x <= location.x <= option.absolute_location.x + option.size.x:
                if option.absolute_location.y <= location.y <= option.absolute_location.y + option.size.y:
                    self.choice_made = True
                    self.player.recently_leveled_up = False
                    option.reward()
                    return True
        return False


class Kills(BaseUIElement):
    def __init__(self, location: XYFloat):
        size = XYInt(
            DISPLAY_SIZE.x,
            DISPLAY_SIZE.y // 20,
        )
        surface = create_surface(size=size)
        super().__init__("Kills", surface, location)
        self._location = location.copy()

    @staticmethod
    @lru_cache(maxsize=1)
    def _cached_surface(kills: int):
        return create_font_surface(
            text=f"Kills: {kills}", size=40, colour=(0, 0, 0)
        )

    @lru_cache(maxsize=1)
    def _cached_element(self, text_surface: Surface):
        return BaseUIElement(
            surface=text_surface,
            location=XYFloat(
                0,
                (self.surface.get_height() - text_surface.get_height()) // 2,
            ),
            name=self.name,
        )

    def update(self, *args, kills: int = 0, **kwargs):
        text_surface = self._cached_surface(kills)
        self.location.x = self._location.x - text_surface.get_width()
        self.layers = [
            self._cached_element(text_surface),
        ]


class Overlay:
    def __init__(
        self,
        game_display: Surface,
        player: "Player",
        paused: bool,
    ):
        self.game_display = game_display
        self.player = player
        self.previously_paused = paused
        self.previously_level_up = False

        self.pause_menu: PauseMenu = PauseMenu()
        self.level_menu: LevelMenu | None = None

        self.layers: list[BaseUIElement] = []
        self.add_resources()
        self.add_time_clock()
        self.add_kills()

    def add_resources(self):
        self.layers.append(
            Resources(
                location=XYFloat(
                    DISPLAY_SIZE.x / 3,
                    (DISPLAY_SIZE.y / 10) * 8.75,
                ),
                player=self.player,
            )
        )

    def add_time_clock(self):
        self.layers.append(
            TimeClock(
                location=XYFloat(
                    (DISPLAY_SIZE.x - DISPLAY_SIZE.x // 10) // 2,
                    0,
                ),
            )
        )

    def add_kills(self):
        self.layers.append(
            Kills(
                location=XYFloat(
                    DISPLAY_SIZE.x,
                    0,
                ),
            )
        )

    def update(self, paused: bool, total_time: float, kills: int, player_mouse: PlayerMouse):
        if player_mouse.left_click:
            self.click(player_mouse.mouse_position)

        # If the player is choosing an option when leveling up
        if self.player.recently_leveled_up and (not self.level_menu or self.level_menu not in self.layers):
            # Create fresh menu for new level options
            self.level_menu = LevelMenu(self.player)
            self.layers.append(self.level_menu)
            paused = True
        elif self.level_menu in self.layers and self.level_menu.choice_made:
            paused = False
            self.level_menu.choice_made = False
            self.layers.remove(self.level_menu)
            self.level_menu = None  # Clear so fresh options are generated next time
            self.player.recently_leveled_up = False

        # If pause is manually toggled
        elif paused and not self.previously_paused:
            self.layers.append(self.pause_menu)
        elif not paused and self.pause_menu in self.layers:
            self.layers.remove(self.pause_menu)
        self.previously_paused = paused

        for layer in self.layers:
            layer.update(total_time=total_time, kills=kills)
            if layer.logging:
                layer.log()
            self.game_display.blit(layer.full_surface, layer.location)

        return paused

    def click(self, location: XYFloat):
        for layer in self.layers:
            if layer.clicked(location):
                return True
        return False

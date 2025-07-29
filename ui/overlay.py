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
        self, location: XYFloat, player: "Player", size: XYInt, title_text: str, parent_location: XYFloat = None, name: str = None,
    ):
        self.location: XYFloat = location
        self.player = player
        self.size = size
        self.title_text = title_text
        self.base_surface = self.background().surface.copy()
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
        # super().update()

    @lru_cache
    def background(self) -> BaseUIElement:
        background_surface = create_surface(size=self.size, colour=(100, 100, 100))
        return BaseUIElement(surface=background_surface, location=self.location, name=self.name if 'name' in dir(self) else None)

    @lru_cache
    def title_surface(self):
        return create_font_surface(
            text=self.title_text, size=35, colour=(200, 200, 200)
        )

    @lru_cache
    def title(self) -> BaseUIElement:
        font_surface = self.title_surface()
        location = XYFloat(
            self.background().surface.get_width() // 2 - font_surface.get_width() // 2,  # todo take into consideration the amount image
            self.background().surface.get_height() // 3 - font_surface.get_height(),
        )
        return BaseUIElement(
            surface=font_surface,
            location=location,
            name=self.name if 'name' in dir(self) else None,
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
        return BaseUIElement(surface=amount_surface, location=location, logging=False, name=self.name if 'name' in dir(self) else None)

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
                location=XYFloat(
                    5,
                    5,
                ),
                player=self.player,
                size=XYInt(
                    (self.surface.size[0] - 10) // 3 - 5,
                    self.surface.size[1] - 10,
                ),
                title_text="Money",
            )
        )

    def create_experience(self):
        self.layers.append(
            Experience(
                location=XYFloat(
                    (self.surface.size[0] - 10) // 3 + 5,
                    5,
                ),
                player=self.player,
                size=XYInt(
                    (self.surface.size[0] - 10) // 3,
                    self.surface.size[1] - 10,
                ),
                title_text="Experience",
            )
        )

    def create_level(self):
        self.layers.append(
            Level(
                location=XYFloat(
                    ((self.surface.size[0] - 10) // 3) * 2 + 10,
                    5,
                ),
                player=self.player,
                size=XYInt(
                    (self.surface.size[0] - 10) // 3 - 5,
                    self.surface.size[1] - 10,
                ),
                title_text="Level",
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
    def __init__(self, parent_location: XYFloat, *args, **kwargs):
        super().__init__(*args, **kwargs, parent_location=parent_location)


class LevelOption(Button):
    def __init__(self, *args, **kwargs):
        self.reward: Callable | None = None
        self.reward_description: str = ""
        self.determine_amount()
        super().__init__(*args, **kwargs, title_text=self.title_text)

    def determine_amount(self) -> str:
        if not self.reward_description:
            return self.get_random_reward()
        return self.reward_description

    def get_random_reward(self):
        def atk_speed():
            for cnt in range(len(self.player.weapon_slots)):
                self.player.weapon_slots[cnt].cooldown /= 1.3

        def mov_speed():
            self.player.speed *= 1.1

        def ammo_size():
            for cnt in range(len(self.player.weapon_slots)):
                self.player.ammo_size *= 1.1

        rewards = {
            'Attack\t+30%\nAttack\nSpeed': atk_speed,
            'Movement\t+10%\nMovement\nSpeed': mov_speed,
            'Attack\t+10%\nAmmo\nSize': ammo_size,
        }
        reward_name = random.choice(list(rewards.keys()))
        self.title_text = reward_name.split('\t')[0]
        self.reward = rewards[reward_name]
        self.reward_description = reward_name.split('\t')[-1]
        return reward_name.split('\t')[-1]


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

    @lru_cache(maxsize=1)
    def determine_options(self, _: int):
        self.layers = []
        for _ in range(self.player.level_options):
            self.layers.append(self.get_option())

    def update(self, *args, **kwargs):
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
        self.level_menu: LevelMenu = LevelMenu(self.player)

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
        if self.player.recently_leveled_up and self.level_menu not in self.layers:
            self.layers.append(self.level_menu)
            paused = True
        elif self.level_menu in self.layers and self.level_menu.choice_made:
            paused = False
            self.level_menu.choice_made = False
            self.layers.remove(self.level_menu)
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

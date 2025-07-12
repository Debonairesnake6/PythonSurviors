from functools import lru_cache

from pygame import Surface

from entities.player import Player
from entities.base_entity import BaseEntity
from scripts.readable_classes import XYFloat, XYInt
from scripts.pygame_utils import create_surface, create_font_surface
from scripts.config import DISPLAY_SIZE


class BaseUIElement(BaseEntity):
    def __init__(
        self,
        surface: Surface = None,
        location: XYFloat = None,
        player: Player = None,
        logging: bool = True,
    ):
        super().__init__(surface, location, logging)
        self.player = player
        self.base_surface = self.surface
        self.layers: list[BaseUIElement] = []

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

    def update(self):
        for layer in self.layers:
            layer.update()


class HotBarUIElement(BaseUIElement):
    def __init__(self, location: XYFloat, player: Player, size: XYInt, title_text: str):
        self.location = location
        self.player = player
        self.size = size
        self.title_text = title_text
        self.base_surface = self.background().surface.copy()
        self.update()

        super().__init__(self.base_surface, location, player)

    def update(self):
        self.layers = [
            self.background(),
            self.title(),
            self.amount(),
        ]
        # super().update()

    @lru_cache
    def background(self) -> BaseUIElement:
        background_surface = create_surface(size=self.size, colour=(100, 100, 100))
        return BaseUIElement(surface=background_surface, location=self.location)

    @lru_cache
    def title(self) -> BaseUIElement:
        font_surface = create_font_surface(
            text=self.title_text, size=35, colour=(200, 200, 200)
        )
        location = XYFloat(
            self.background().surface.get_width() // 2 - font_surface.get_width() // 2,
            self.background().surface.get_height() // 2
            - font_surface.get_height() // 4 * 4,
        )
        return BaseUIElement(
            surface=font_surface,
            location=location,
        )

    def amount(self) -> BaseUIElement:
        amount_surface = create_font_surface(
            text=self.determine_amount(), size=45, colour=(200, 200, 200)
        )
        location = XYFloat(
            self.background().surface.get_width() // 2
            - amount_surface.get_width() // 2,
            self.background().surface.get_height() // 2
            - amount_surface.get_height() // 4,
        )
        return BaseUIElement(surface=amount_surface, location=location, logging=False)

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
    def __init__(self, location: XYFloat, player: Player):
        size = XYInt(
            DISPLAY_SIZE.x // 3,
            DISPLAY_SIZE.y // 10,
        )
        surface = create_surface(size=size, colour=(0, 0, 0))
        super().__init__(surface, location, player)

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


class Overlay:
    def __init__(
        self, game_display: Surface, player: Player, layers: list[BaseUIElement] = None
    ):
        self.game_display = game_display
        self.player = player
        self.layers = layers
        if self.layers is None:
            self.layers: list[BaseUIElement] = []

        self.layers.append(
            Resources(
                location=XYFloat(
                    DISPLAY_SIZE.x / 3,
                    (DISPLAY_SIZE.y / 10) * 8.75,
                ),
                player=self.player,
            )
        )

    def update(self):
        for layer in self.layers:
            layer.update()
            self.game_display.blit(layer.full_surface, layer.location)

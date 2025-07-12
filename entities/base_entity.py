from abc import abstractmethod, ABC
import random
from scripts.readable_classes import XYFloat, XYInt
from scripts.pygame_utils import create_surface, default_font
from pygame import Surface, FRect
from pygame.transform import flip
from scripts.config import BASE_SPEED
from typing import TYPE_CHECKING
from icecream import ic

if TYPE_CHECKING:
    from entities.player import Player


class BaseEntity:
    def __init__(
        self,
        surface: Surface = None,
        location: XYFloat = None,
        logging: bool = True,
    ):
        if location:
            self.location = location
        else:
            self.location = XYFloat(0, 0)

        if surface:
            self.surface = surface
        else:
            self.surface = create_surface(colour=(0, 0, 0), size=XYInt(20, 20))

        if logging:
            ic(
                f"Entity: {self.__class__.__name__}\t|\tLocation: {self.location}\t|\tSize: {self.surface.get_size()}"
            )

    def get_rect(self) -> FRect:
        return FRect(self.location.to_tuple(), self.surface.get_rect().size)

    @property
    def location_center(self) -> XYFloat:
        return self.location + XYFloat(
            self.surface.get_width() / 2, self.surface.get_height() / 2
        )


class BaseSprite(BaseEntity):
    def __init__(
        self,
        location: XYFloat = None,
        surface: Surface = None,
        speed: float = None,
        health: float = None,
    ):
        if speed:
            self.speed = speed
        else:
            self.speed = BASE_SPEED

        if health:
            self.health = health
        else:
            self.health = 1

        self.flip_surface: bool = False
        self.damage_font = default_font(50)

        super().__init__(surface, location)

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return id(self) == id(other)

    def __getattribute__(self, item: str):
        if item != "surface":
            return super().__getattribute__(item)
        if self.flip_surface:
            return flip(super().__getattribute__(item), True, False)
        return super().__getattribute__(item)


class BaseDrop(BaseEntity):
    def __init__(self, surface: Surface, location: XYFloat = None):
        super().__init__(surface, location)

    def pickup(self, player: "Player"):
        raise NotImplementedError()

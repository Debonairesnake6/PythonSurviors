from entities.base_entity import BaseDrop
from pygame import Surface, image
from random import choice
from scripts.readable_classes import XYFloat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.player import Player


class Money(BaseDrop):
    def __init__(self, location: XYFloat):
        surface: Surface = image.load("assets/money.png")
        super().__init__(surface, location)

    def pickup(self, player: "Player"):
        player.money += 1


class MoneyPile(BaseDrop):
    def __init__(self, location: XYFloat):
        surface: Surface = image.load("assets/money_pile.png")
        super().__init__(surface, location)

    def pickup(self, player: "Player"):
        player.money += 5


class Experience(BaseDrop):
    def __init__(self, location: XYFloat):
        surface: Surface = image.load("assets/experience.png")
        super().__init__(surface, location)

    def pickup(self, player: "Player"):
        player.experience += 1


class ExperiencePile(BaseDrop):
    def __init__(self, location: XYFloat):
        surface: Surface = image.load("assets/experience_pile.png")
        super().__init__(surface, location)

    def pickup(self, player: "Player"):
        player.experience += 5


DEFAULT_DROP_TABLE: dict[type[BaseDrop], int] = {
    None: 10,
    Money: 3,
    MoneyPile: 1,
    Experience: 6,
    ExperiencePile: 1,
}


def get_drop(drop_table: dict = None) -> type[BaseDrop] | None:
    if drop_table is None:
        drop_table = DEFAULT_DROP_TABLE

    items = []
    for drop, weight in drop_table.items():
        for count in range(weight):
            items.append(drop)
    return choice(items)

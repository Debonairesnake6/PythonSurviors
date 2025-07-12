from scripts.readable_classes import XYFloat, XYInt
from entities.base_entity import BaseSprite
from entities.drops import DEFAULT_DROP_TABLE, get_drop
from pygame import Surface, image
from scripts.pygame_utils import create_surface
from scripts.config import BASE_SPEED


class Enemy(BaseSprite):
    def __init__(
        self,
        location: XYFloat,
        surface: Surface = None,
        speed: float = None,
        health: float = None,
        drop_table: dict = None,
    ):

        if surface is None:
            # surface = create_surface(colour=(255, 0, 0), size=XYInt(20, 20))
            surface = image.load("assets/enemy.png")

        if speed is None:
            speed = 0.6 * BASE_SPEED

        if drop_table is None:
            drop_table = DEFAULT_DROP_TABLE

        super().__init__(location, surface, speed, health)

        self.drop_table = drop_table

    def die(self):
        if drop := get_drop(self.drop_table):
            return drop(self.location_center)
        return None

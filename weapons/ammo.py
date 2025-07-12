from scripts.readable_classes import XYFloat, XYInt
from weapons.base_weapon import BaseAmmo, BaseEffect
from pygame import Surface, image
from scripts.config import BASE_SPEED
from scripts.pygame_utils import create_surface


class Normal(BaseAmmo):
    def __init__(
        self,
        target_location: XYFloat,
        current_location: XYFloat,
        base_damage: float = 1,
        base_ammo_speed: float = BASE_SPEED * 5,
        surface: Surface = None,
        effects: list[BaseEffect] = None,
    ):
        if surface is None:
            surface = image.load("assets/ammo.png")

        if effects is None:
            effects = []

        super().__init__(
            target_location,
            current_location,
            base_damage,
            base_ammo_speed,
            surface,
            effects,
        )

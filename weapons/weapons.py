from scripts.readable_classes import XYFloat, XYInt
from weapons.base_weapon import BaseAmmo, BaseWeapon, BaseEffect
from weapons.ammo import Normal
from pygame import Surface
from scripts.pygame_utils import create_surface


class Pistol(BaseWeapon):
    def __init__(
        self,
        cooldown: float = 0.5,
        attack_range: float = 500,
        damage_multiplier: float = 3,
        ammo_speed_multiplier: float = 1,
        icon: Surface = None,
        ammo: BaseAmmo = Normal,
        effects: list[BaseEffect] = None,
    ):
        if icon is None:
            icon = create_surface((30, 30, 30), XYInt(15, 15))

        if effects is None:
            effects = []

        super().__init__(
            cooldown,
            attack_range,
            damage_multiplier,
            ammo_speed_multiplier,
            icon,
            ammo,
            effects,
        )


# Todo
#  - Have base weapons (bow, pistol, shotgun, grenade, etc.)
#  - Have base ammo (fire, poison, explosive, blunt, etc.)
#  - Have effects (damage, size, frequency, debuffs, etc.)

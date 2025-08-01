from scripts.readable_classes import XYFloat
from entities.base_entity import BaseSprite
from pygame import Surface, image
from weapons.base_weapon import BaseWeapon


class Player(BaseSprite):
    def __init__(
        self,
        location: XYFloat,
        surface: Surface = None,
        speed: float = None,
        health: int = 1,
    ):
        if surface is None:
            surface = image.load("assets/player.png")
        super().__init__(location, surface, speed, health)

        self.weapon_slots: list[BaseWeapon] = []
        self.money = 0
        self._experience = 0
        self.level_scaling = 1.3
        self._level: int = 1
        self.next_level_experience: int = 5
        self.kills: int = 0
        self.recently_leveled_up: bool = False
        self.level_options: int = 3
        self.ammo_size: float = 1

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value: int):
        if value > 0:
            self.recently_leveled_up = True
        self._level = value

    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, value):
        self._experience = value
        self.check_level_up()

    def check_level_up(self):
        if self._experience >= self.next_level_experience:
            self.level += 1
            self._experience -= self.next_level_experience
            self.next_level_experience = int(
                self.next_level_experience * self.level_scaling
            )
            return True
        return False

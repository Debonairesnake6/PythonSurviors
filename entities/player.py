from scripts.readable_classes import XYFloat, XYInt
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
        self.level: int = 1
        self.next_level_experience: int = 5

    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, value):
        self._experience = value
        if self._experience >= self.next_level_experience:
            self.level += 1
            self._experience -= self.next_level_experience
            self.next_level_experience = int(
                self.next_level_experience * self.level_scaling
            )

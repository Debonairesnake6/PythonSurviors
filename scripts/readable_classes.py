from dataclasses import dataclass
from typing import overload, override

from pygame import Vector2


@dataclass(slots=True)
class XYInt:
    x: int = 0
    y: int = 0

    def __setattr__(self, key, value):
        if not isinstance(value, int):
            self.__setattr__(key, int(value))
        else:
            super(XYInt, self).__setattr__(key, value)

    def __json__(self):
        return {"x": self.x, "y": self.y}

    def __add__(self, other: "XYInt"):
        return XYInt(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "XYInt"):
        return XYInt(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int | float):
        return XYInt(int(self.x * other), int(self.y * other))

    def __truediv__(self, other: int | float):
        return XYInt(int(self.x / other), int(self.y / other))

    def __hash__(self):
        return hash(f"{self.x};{self.y}")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.x + self.y < other.x + other.y

    def __gt__(self, other):
        return self.x + self.y > other.x + other.y

    def to_tuple(self) -> tuple:
        return self.x, self.y

    def to_float(self) -> "XYFloat":
        return XYFloat(self.x, self.y)

    @staticmethod
    def from_tuple(value: tuple[int, int]) -> "XYInt":
        return XYInt(value[0], value[1])

    def __copy__(self):
        return XYInt(self.x, self.y)


@dataclass(slots=True)
class XYFloat(Vector2):

    # noinspection PyMissingConstructor
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __setattr__(self, key, value):
        if not isinstance(value, float):
            self.__setattr__(key, float(value))
        else:
            super(XYFloat, self).__setattr__(key, value)

    def __json__(self):
        return {"x": self.x, "y": self.y}

    def to_tuple(self) -> tuple:
        return self.x, self.y

    def to_int(self) -> XYInt:
        return XYInt(int(self.x), int(self.y))

    def __add__(self, other: "XYFloat"):
        return XYFloat(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "XYFloat"):
        return XYFloat(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int | float):
        return XYFloat(float(self.x * other), float(self.y * other))

    def __truediv__(self, other: int | float):
        return XYFloat(float(self.x / other), float(self.y / other))

    def __hash__(self):
        return hash(f"{self.x};{self.y}")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.x + self.y < other.x + other.y

    def __gt__(self, other):
        return self.x + self.y > other.x + other.y

    @staticmethod
    def from_tuple(value: tuple[float, float]) -> "XYFloat":
        return XYFloat(value[0], value[1])

    def copy(self) -> "XYFloat":
        return XYFloat(self.x, self.y)


@dataclass(slots=True)
class DirectionBool:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False

    def copy(self):
        return DirectionBool(self.left, self.right, self.up, self.down)


@dataclass(slots=True)
class DirectionInt:
    left: int = 0
    right: int = 0
    up: int = 0
    down: int = 0


@dataclass(slots=True)
class CurrentMaxInt:
    current: int
    max: int


@dataclass(slots=True)
class PlayerInput:
    left_click: bool = False
    right_click: bool = False

    def copy(self):
        return PlayerInput(self.left_click, self.right_click)

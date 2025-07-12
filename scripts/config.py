from typing import TYPE_CHECKING
from scripts.readable_classes import XYInt

if TYPE_CHECKING:
    from entities.player import Player

WINDOW_SIZE: XYInt = XYInt(1920, 1080)
# DISPLAY_SIZE: XYInt = XYInt(1280, 720)
DISPLAY_SIZE: XYInt = XYInt(1920, 1080)
BASE_SPEED = 100.0
PLAYER: "Player" = None

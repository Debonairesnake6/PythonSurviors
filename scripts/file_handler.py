import json
import os
import pygame
from functools import lru_cache

BASE_IMAGE_PATH = "data/images/"


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json__"):
            if callable(obj.__json__):
                return obj.__json__()
            else:
                return obj.__json__
        return super(CustomJSONEncoder, self).default(obj)


@lru_cache
def load_image(
    path: str,
    transparent_colour: tuple[int, int, int] = None,
    width: float = None,
    height: float = None,
    nonce: str = None,
) -> pygame.Surface:
    img: pygame.Surface = pygame.image.load(f"{BASE_IMAGE_PATH}{path}").convert_alpha()
    if transparent_colour:
        img.set_colorkey(transparent_colour)
    if width or height:
        img = pygame.transform.scale(
            img,
            (
                width if width else img.get_width(),
                height if height else img.get_height(),
            ),
        )
    return img


@lru_cache
def load_images(
    path: str,
    colour_key: tuple[int, int, int] = None,
    width: float = None,
    height: float = None,
) -> list[pygame.Surface]:
    images = []
    for img_name in sorted(os.listdir(f"{BASE_IMAGE_PATH}{path}")):
        if not img_name.endswith(".png"):
            continue
        images.append(
            load_image(
                f"{path}/{img_name}",
                transparent_colour=colour_key,
                width=width,
                height=height,
            )
        )
    return images

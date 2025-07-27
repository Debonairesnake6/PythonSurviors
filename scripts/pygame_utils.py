import math
from pygame import Surface, SRCALPHA, mouse, font, math as pmath, image
from scripts.readable_classes import XYInt, XYFloat
from scripts import config
from functools import lru_cache
from icecream import ic


@lru_cache
def create_surface(colour: tuple = None, size: XYInt = XYInt(80, 80)) -> Surface:
    new_surface: Surface = Surface((size.x, size.y), SRCALPHA)
    if colour is not None:
        new_surface.fill(colour)
    return new_surface


def get_relative_mouse_pos(surface: Surface) -> tuple[int, int]:
    mouse_pos = list(mouse.get_pos())
    mouse_pos[0] = mouse_pos[0] / (config.WINDOW_SIZE.x / surface.get_width())
    mouse_pos[1] = mouse_pos[1] / (config.WINDOW_SIZE.y / surface.get_height())
    return mouse_pos[0], mouse_pos[1]


def get_selected_mask(size: XYInt, alpha: int = 10) -> Surface:
    new_surface = create_surface(
        colour=(255, 255, 255),
        size=size,
    )
    new_surface.set_alpha(alpha)
    return new_surface


@lru_cache
def create_font_surface(
    text: str, colour: tuple[int, int, int] = (255, 255, 255), size: int = 20
) -> Surface:
    return default_font(size).render(text, True, colour)


def calculate_pathing(
    current_location: XYFloat,
    target_location: XYFloat,
    projectile_speed: float,
    delta_time: float,
) -> XYFloat:
    next_location = pmath.Vector2(current_location.to_tuple()).move_towards(
        pmath.Vector2(target_location.to_tuple()), projectile_speed * delta_time
    )
    return XYFloat(next_location.x, next_location.y)


def calculate_distance(
    current_location: XYFloat,
    target_location: XYFloat,
) -> float:
    return (
        (current_location.x - target_location.x) ** 2
        + (current_location.y - target_location.y) ** 2
    ) ** 0.5


def line_set_distance(
    current_location: XYFloat,
    target_location: XYFloat,
    distance: float,
) -> XYFloat:
    current_distance = calculate_distance(current_location, target_location)
    inverse_fraction_multiplier = distance / current_distance

    target_location = target_location.copy()
    target_location.x = current_location.x + (
        (target_location.x - current_location.x) * inverse_fraction_multiplier
    )  # inverse_fraction_multiplier
    target_location.y = current_location.y + (
        (target_location.y - current_location.y) * inverse_fraction_multiplier
    )
    return target_location


def location_reached(
    current_location: XYFloat,
    target_location: XYFloat,
    speed: float,
    delta_time: float,
):
    next_location = calculate_pathing(
        current_location.copy(),
        target_location,
        speed,
        delta_time,
    )
    if (
        current_location.x > next_location.x >= target_location.x
        or current_location.x < next_location.x <= target_location.x
    ):
        return False
    elif (
        current_location.y > next_location.y >= target_location.y
        or current_location.y < next_location.y <= target_location.y
    ):
        return False
    return True


@lru_cache
def tile_background(surface: Surface, alternate_rows: bool = False) -> Surface:
    tiles = XYInt(
        math.ceil(config.DISPLAY_SIZE.x / surface.get_width()),
        math.ceil(config.DISPLAY_SIZE.y / surface.get_height()),
    )
    background_surface = create_surface(
        size=XYInt(tiles.x * surface.get_width(), tiles.y * surface.get_height())
    )
    for x in range(tiles.x if not alternate_rows else tiles.x + 1):
        for y in range(tiles.y):
            background_surface.blit(
                surface,
                (
                    (
                        x * surface.get_width() - surface.get_width() / 2
                        if alternate_rows and y % 2 == 1
                        else x * surface.get_width()
                    ),
                    y * surface.get_height(),
                ),
            )
    background_surface.set_alpha(64)
    return background_surface


@lru_cache
def default_font(size: int = 20):
    return font.Font("assets/PythonSurvivorsFont.ttf", size)


def log(text: str):
    print(text)
    with open("logs/log.txt", "a") as file:
        file.write(f"{text}\n")


def configure_icecream():
    with open("logs/log.txt", "w") as file:
        file.write(f"")
    ic.configureOutput(
        prefix="Debug| ",
        outputFunction=log,
        includeContext=True,
    )


def time_to_string(time: float) -> str:
    seconds = time % 60
    minutes = math.floor(time / 60) % 60
    return f"{minutes:02.0f}:{seconds:02.0f}"


def calculate_inner_picture_size(parent_size: XYInt, rows: int, columns: int, border: int) -> XYInt:
    return XYInt(
        (parent_size.x - (columns + 1) * border) // columns,
        (parent_size.y - (rows + 1) * border) // rows,
    )

def surface_to_file(surface: Surface, name: str = "debug"):
    image.save(surface, f"logs/{name}.png")
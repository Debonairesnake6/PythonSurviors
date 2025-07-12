from pygame import Surface
from scripts.readable_classes import XYFloat


class Animation:

    def __init__(
        self,
        frames: list[Surface] | Surface,
        seconds: float,
        loop: bool = False,
        location: XYFloat = None,
    ):
        self.frames = frames
        if type(frames) == Surface:
            self.frames = [frames]
        self.seconds = seconds
        self.loop = loop
        self.location: XYFloat = location
        self.current_frame = 0

    def next_frame(self, delta_time: float):
        self.current_frame += delta_time

        if not self.loop and self.current_frame > self.seconds:
            return None
        else:
            return self.frames[int(self.current_frame % len(self.frames))]

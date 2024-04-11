from math import ceil
from time import time_ns

class Timer:
    def __init__(self, seconds: float):
        self.length = ceil(seconds * 1000000000)
        self.end_time = time_ns() + self.length

    def has_finished(self) -> bool:
        return time_ns() > self.end_time

    def reset(self):
        self.end_time = time_ns() + self.length


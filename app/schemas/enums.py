from enum import Enum


class GameMode(str, Enum):
    ORIGINAL = "original"
    DAILY = "daily"
    RAPID = "rapid"
    LYRICS = "lyrics"


class SubmittableGameMode(str, Enum):
    ORIGINAL = "original"
    DAILY = "daily"

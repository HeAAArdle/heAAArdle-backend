from enum import Enum


class GameMode(str, Enum):
    ORIGINAL = "original"
    DAILY = "daily"
    RAPID = "rapid"
    LYRICS = "lyrics"
    ARCHIVE = "archive"


class SubmittableGameMode(str, Enum):
    ORIGINAL = "original"
    DAILY = "daily"

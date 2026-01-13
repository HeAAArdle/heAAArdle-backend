from app.schemas.enums import GameMode

MODE_AUDIO_CLIP_LENGTH = {
    GameMode.ORIGINAL: 16,
    GameMode.DAILY: 16,
    GameMode.RAPID: 3,
    GameMode.ARCHIVE: 16,
}

MODE_MAXIMUM_ATTEMPTS = {
    GameMode.ORIGINAL: 6,
    GameMode.DAILY: 6,
    GameMode.RAPID: 1,
    GameMode.LYRICS: 1,
    GameMode.ARCHIVE: 6,
}

MODE_EXPIRES_IN_MINUTES = {
    GameMode.ORIGINAL: 16,
    GameMode.RAPID: 3,
    GameMode.LYRICS: 3,
    GameMode.ARCHIVE: 16,
}

# Game


class NoSongAvailable(Exception):
    pass


class DailyGameNotFound(Exception):
    pass


class UserAlreadyPlayedDailyGame(Exception):
    pass


class InvalidNumberOfAttempts(Exception):
    pass


class SessionNotFound(Exception):
    pass


class DuplicateSession(Exception):
    pass


# Archive


class InvalidYearOrMonth(Exception):
    pass

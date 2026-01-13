# Game


class ArchiveDateNotProvided(Exception):
    pass


class DateIsInTheFuture(Exception):
    pass


class DateProvided(Exception):
    pass


class NoSongAvailable(Exception):
    pass


class DailyGameNotFound(Exception):
    pass


class UserAlreadyPlayedTheDailyGame(Exception):
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

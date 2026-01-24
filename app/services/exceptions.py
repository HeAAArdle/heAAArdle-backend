# Game


class ArchiveDateNotProvided(Exception):
    pass


class DateIsTodayOrInTheFuture(Exception):
    pass


class DateProvided(Exception):
    pass


class NoSongAvailable(Exception):
    pass


class SongNotFound(Exception):
    pass


class DailyGameNotFound(Exception):
    pass


class UserAlreadyPlayedTheDailyGame(Exception):
    pass


class InvalidNumberOfAttempts(Exception):
    pass


class DuplicateSession(Exception):
    pass


# Archive


class InvalidYearOrMonth(Exception):
    pass


# Leaderboards

class LimitIsBelow1(Exception):
    pass


class UserNotOnLeaderboard(Exception):
    pass

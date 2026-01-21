from schemas.game import UserWins


def leaderboard_row_to_schema(row):
    """
    Maps a UserLeaderboard row to a UserWins schema.
    """
    return UserWins(
        username=row.username,
        wins=row.numberOfWins,
    )

import uuid
from sqlalchemy.orm import Session

from app.models.statistics import Statistics
from app.schemas.enums import GameMode


def update_statistics_after_game(
    db: Session, user_id: uuid.UUID, mode: GameMode, did_win: bool, guesses: int
) -> None:
    """
    Updates the statistics for a user after a game has been submitted.
    """

    try:
        stats = (
            db.query(Statistics)
            .filter(Statistics.userID == user_id, Statistics.mode == mode)
            .with_for_update()
            .one()
        )

        _increment_games_played(stats)
        _update_win_and_streaks(stats, did_win)
        _update_guess_distribution(stats, guesses)

        db.commit()
    except Exception:
        db.rollback()
        raise


def _increment_games_played(stats: Statistics) -> None:
    """
    Increments the total number of games played.
    """

    stats.gamesPlayed += 1


def _update_win_and_streaks(stats: Statistics, did_win: bool) -> None:
    """
    Updates win count and streaks based on whether the user won the game.
    """

    if did_win:
        stats.winCount += 1
        stats.currentStreak += 1

        if stats.currentStreak > stats.maximumStreak:
            stats.maximumStreak = stats.currentStreak
    else:
        stats.currentStreak = 0


def _update_guess_distribution(stats: Statistics, guesses: int) -> None:
    """
    Update the guess distribution based on the number of guesses taken to win.
    """

    if guesses < 1 or guesses > 6:
        raise ValueError("Guesses must be between 1 and 6.")

    if guesses == 1:
        stats.guesses1 += 1
    elif guesses == 2:
        stats.guesses2 += 1
    elif guesses == 3:
        stats.guesses3 += 1
    elif guesses == 4:
        stats.guesses4 += 1
    elif guesses == 5:
        stats.guesses5 += 1
    elif guesses == 6:
        stats.guesses6 += 1

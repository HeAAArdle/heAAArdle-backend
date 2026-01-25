# standard library
import uuid

# SQLAlchemy
from sqlalchemy.orm import Session

# models
from app.models.statistics import Statistics

# schemas
from app.schemas.enums import GameMode

# services
from app.services.game.game_validator import (
    assert_number_of_attempts_do_not_exceed_the_mode_maximum,
)


def update_statistics_after_game(
    db: Session, user_id: uuid.UUID, mode: GameMode, won: bool, guesses: int
):
    """
    Update a user's statistics after completing a game.

    Handles games played, win/loss counts, streaks, and guess distribution.
    """

    # Lock the user's statistics row for update to prevent race conditions
    stats = (
        db.query(Statistics)
        .filter(Statistics.userID == user_id, Statistics.mode == mode)
        .with_for_update()
        .one()
    )

    # Increment total games played
    _increment_games_played(stats)

    # Update wins and streaks depending on the outcome of the game
    _update_win_and_streaks(stats, won)

    # Update the guess distribution based on the number of guesses
    _update_guess_distribution(stats, guesses)


def _increment_games_played(stats: Statistics):
    """
    Increment the total number of games played by the user.
    """
    stats.gamesPlayed += 1


def _update_win_and_streaks(stats: Statistics, won: bool):
    """
    Update the user's win count and streaks after a game.
    """

    # If the user won, increase the win count and current streak
    if won:
        stats.winCount += 1
        stats.currentStreak += 1

        # Update maximum streak if exceeded
        if stats.currentStreak > stats.maximumStreak:
            stats.maximumStreak = stats.currentStreak

    # If the user lost, reset the current streak to zero
    else:
        stats.currentStreak = 0


def _update_guess_distribution(stats: Statistics, guesses: int):
    """
    Increment the counter for the number of guesses taken to win.
    """

    assert_number_of_attempts_do_not_exceed_the_mode_maximum(
        GameMode(stats.mode), guesses
    )

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

from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.statistics import Statistics

from app.schemas.game import SubmitGameRequest


def update_statistics(db: Session, payload: SubmitGameRequest):
    # Decompose payload
    user_id = payload.userID
    mode = payload.mode
    won = payload.won
    attempts = payload.attempts

    # Fetch existing statistics for the user and mode
    query = select(Statistics).where(
        Statistics.userID == user_id, Statistics.mode == mode
    )

    statistics = db.scalars(query).first()

    # Validate existence of a statistics record; if nonexistent, create a new statistics row
    if not statistics:
        statistics = Statistics(userID=user_id, mode=mode)

        db.add(statistics)

    # Increment the number of games played
    statistics.gamesPlayed += 1

    # Update win/loss and streaks
    if won:
        statistics.winCount += 1

        statistics.currentStreak += 1

        if statistics.currentStreak > statistics.maximumStreak:
            statistics.maximumStreak = statistics.currentStreak

        if attempts == 1:
            statistics.guesses1 += 1
        elif attempts == 2:
            statistics.guesses2 += 1
        elif attempts == 3:
            statistics.guesses3 += 1
        elif attempts == 4:
            statistics.guesses4 += 1
        elif attempts == 5:
            statistics.guesses5 += 1
        elif attempts == 6:
            statistics.guesses6 += 1

    else:
        statistics.currentStreak = 0

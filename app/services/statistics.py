from sqlalchemy.orm import Session

from app.models.statistics import Statistics

from app.schemas.game import SubmitGameRequest

def update_statistics(db: Session, payload: SubmitGameRequest):
    # Fetch existing statistics for the user and mode
    statistics = (
        db.query(Statistics)
        .filter(Statistics.userID == payload.userID, Statistics.mode == payload.mode)
        .first()
    )

    # Validate existence of a statistics record; if not, create a new statistics row
    if not statistics:
        statistics = Statistics(userID=payload.userID, mode=payload.mode)

        db.add(statistics)

    # Increment the number of games played
    statistics.gamesPlayed += 1

    # Update win/loss and streaks
    if payload.won:
        statistics.winCount += 1

        statistics.currentStreak += 1

        if statistics.currentStreak > statistics.maximumStreak:
            statistics.maximumStreak = statistics.currentStreak

        if payload.attempts == 1:
            statistics.guesses1 += 1
        elif payload.attempts == 2:
            statistics.guesses2 += 1
        elif payload.attempts == 3:
            statistics.guesses3 += 1
        elif payload.attempts == 4:
            statistics.guesses4 += 1
        elif payload.attempts == 5:
            statistics.guesses5 += 1
        elif payload.attempts == 6:
            statistics.guesses6 += 1

    else:
        statistics.currentStreak = 0

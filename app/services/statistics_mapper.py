from app.models.statistics import Statistics as StatisticsModel
from app.schemas.account import Statistics as StatisticsSchema

def dbstats_to_schemastats(stats: StatisticsModel) -> StatisticsSchema:
    gamesPlayed = stats.gamesPlayed
    win_percentage = (stats.winCount * 100 // gamesPlayed) if gamesPlayed > 0 else 0

    guess_distribution = (
        stats.guesses1,
        stats.guesses2,
        stats.guesses3,
        stats.guesses4,
        stats.guesses5,
        stats.guesses6,
    )

    return StatisticsSchema(
        gamesPlayed=stats.gamesPlayed,
        winCount=stats.winCount,
        winPercentage=win_percentage,
        currentStreak=stats.currentStreak,
        maximumStreak=stats.maximumStreak,
        guessDistribution=guess_distribution
    )
# standard library
import random

import uuid

from datetime import date as DateType

from dataclasses import dataclass

from typing import Optional

# SQLAlchemy
from sqlalchemy.orm import Session

# models
from app.models import *

# schemas
from app.schemas.game import StartGameRequest, SubmitGameRequest

from app.schemas.enums import GameMode as GameModeEnum

# websocket
from app.ws.session import sessions

# services
from app.services.game.game_domain import (
    get_expires_in_minutes_by_game_mode,
    get_audio_start_at_by_game_mode,
    get_maximum_attempts_by_game_mode,
)

from app.services.game.game_provider import get_daily_game

from app.services.game.game_validator import (
    assert_date_is_not_in_the_future,
    assert_game_session_is_unique,
    assert_date_is_not_given_for_non_archive_modes,
    assert_number_of_attempts_do_not_exceed_the_mode_maximum,
    assert_user_has_not_played_the_daily_game,
)

from app.services.song import get_random_song

from app.services.statistics import update_statistics

from app.services.leaderboard import update_leaderboard

# exceptions
from app.services.exceptions import (
    ArchiveDateNotProvided,
    SessionNotFound,
)

# utils
from app.api.v1.endpoints.enums import Result


@dataclass
class StartGameDTO:
    song: Song

    maximum_attempts: int

    expires_in_minutes: int

    audio_start_at: Optional[int] = None

    lyrics_answer: Optional[str] = None

    lyrics_given: Optional[str] = None

    date: Optional[DateType] = None


class GameMode:
    # Identifier for the concrete game mode
    mode: GameModeEnum

    def resolve(
        self, payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
    ) -> StartGameDTO:
        # Resolve a start-game request into a fully-initialized game session
        raise NotImplementedError


class FreePlayAudioGameMode(GameMode):
    def resolve(
        self, payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
    ) -> StartGameDTO:
        # Disallow date input for non-archive modes
        assert_date_is_not_given_for_non_archive_modes(payload.date)

        # Retrieve a random song from the database
        song = get_random_song(db)

        # Compute a valid audio clip starting position for the mode
        audio_start_at = get_audio_start_at_by_game_mode(self.mode, song.duration)

        # Resolve mode-specific gameplay constraints
        maximum_attempts = get_maximum_attempts_by_game_mode(self.mode)

        expires_in_minutes = get_expires_in_minutes_by_game_mode(self.mode)

        # Build the start-game response for free-play modes
        return StartGameDTO(
            song=song,
            audio_start_at=audio_start_at,
            maximum_attempts=maximum_attempts,
            expires_in_minutes=expires_in_minutes,
            date=None,
        )


class OriginalGameMode(FreePlayAudioGameMode):
    # Original mode uses free-play audio rules
    mode = GameModeEnum.ORIGINAL


class RapidGameMode(FreePlayAudioGameMode):
    # Rapid mode uses free-play audio rules with different constraints
    mode = GameModeEnum.RAPID


class DailyGameMode(GameMode):
    def resolve(
        self, payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
    ) -> StartGameDTO:
        # Disallow date input for non-archive modes
        assert_date_is_not_given_for_non_archive_modes(payload.date)

        # Daily games are always resolved against today's date
        today = DateType.today()

        date = today

        # Enforce the one-play-per-day rule for authenticated users
        if user_id is not None:
            assert_user_has_not_played_the_daily_game(db, user_id)

        # Get the daily game configuration for today
        daily_game = get_daily_game(db, date)

        # Compute a valid audio clip starting position for the daily mode
        audio_start_at = get_audio_start_at_by_game_mode(
            GameModeEnum.DAILY, daily_game.song.duration
        )

        # Resolve daily-mode gameplay constraints
        maximum_attempts = get_maximum_attempts_by_game_mode(GameModeEnum.DAILY)

        expires_in_minutes = get_expires_in_minutes_by_game_mode(GameModeEnum.DAILY)

        # Build the start-game response for the daily mode
        return StartGameDTO(
            song=daily_game.song,
            audio_start_at=audio_start_at,
            maximum_attempts=maximum_attempts,
            expires_in_minutes=expires_in_minutes,
            date=date,
        )


class LyricsGameMode(GameMode):
    LINES_TO_SHOW = 2
    MINIMUM_WORDS = 1
    MAXIMUM_WORDS = 2

    def resolve(
        self, payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
    ) -> StartGameDTO:
        # Disallow date input for non-archive modes

        assert_date_is_not_given_for_non_archive_modes(payload.date)

        song = get_random_song(db)

        lines = self._split_lyrics(song.lyrics)

        lyrics_start_at = self._get_lyrics_start_at(lines)

        displayed_lines = lines[lyrics_start_at : lyrics_start_at + self.LINES_TO_SHOW]

        # Pick the answer
        lyrics_answer = self._get_lyrics_answer(displayed_lines)

        # Mask the lyrics
        lyrics_given = self._get_lyrics_given(displayed_lines, lyrics_answer)

        # Resolve daily-mode gameplay constraints
        maximum_attempts = get_maximum_attempts_by_game_mode(GameModeEnum.LYRICS)

        expires_in_minutes = get_expires_in_minutes_by_game_mode(GameModeEnum.LYRICS)

        return StartGameDTO(
            song=song,
            lyrics_answer=lyrics_answer,
            lyrics_given=lyrics_given,
            maximum_attempts=maximum_attempts,
            expires_in_minutes=expires_in_minutes,
            date=None,
        )

    def _split_lyrics(self, raw: str) -> list[str]:
        # Split the raw lyrics string by semicolon, strip " " from each line, and discard empty lines
        return [line.strip() for line in raw.split(";") if line.strip()]

    def _get_lyrics_start_at(self, lines: list[str]) -> int:
        # Compute the maximum valid starting index so that LINES_TO_SHOW lines can still be displayed
        max_start_at = max(0, len(lines) - self.LINES_TO_SHOW)

        # Randomly choose a starting line index within bounds
        return random.randint(0, max_start_at)

    def _get_lyrics_answer(self, lines: list[str]) -> str:
        """
        Pick 1-2 contiguous words from the displayed lines.

        Contiguity may cross line boundaries.
        """

        # Flatten all words across all lines while preserving their positions
        # Each entry stores: (line_index, word_index, word)
        words: list[tuple[int, int, str]] = []

        # Iterate through each line and split it into words
        for line_index, line in enumerate(lines):
            for word_index, word in enumerate(line.split()):
                words.append((line_index, word_index, word))

        # Guard against empty input
        if not words:
            raise ValueError("No words available in lyrics.")

        # Randomly choose whether the answer is one or two words long
        answer_length = random.choice([1, 2])

        # If only one word exists overall, force a single-word answer
        if answer_length == 2 and len(words) < 2:
            answer_length = 1

        # Compute the highest valid start index for the chosen answer length
        maximum_start_index = len(words) - answer_length

        # Randomly select a starting index within the valid range
        start = random.randint(0, maximum_start_index)

        # Select the contiguous word slice (may span multiple lines)
        selected = words[start : start + answer_length]

        # Join and return only the word values as the final answer string
        return " ".join(word for _, _, word in selected)

    def _get_lyrics_given(self, lines: list[str], lyrics_answer: str) -> str:
        """
        Mask the answer words in the displayed lines.

        Mask format is one underscore per letter and two spaces between words.
        """

        # Split the answer string into individual words
        answer_words = lyrics_answer.split()

        # Determine how many contiguous words must be matched and masked
        answer_length = len(answer_words)

        # Split each lyric line into a mutable word list
        split_lines = [line.split() for line in lines]

        # Flatten all word positions across lines into one single list
        # Each entry stores: (line_index, word_index)
        positions: list[tuple[int, int]] = []

        for line_index, words in enumerate(split_lines):
            for word_index in range(len(words)):
                positions.append((line_index, word_index))

        # Placeholder for the positions where the answer is found
        answer_positions = None

        # Slide a window across the flattened word positions
        for i in range(len(positions) - answer_length + 1):
            candidate: list[str] = []

            # Collect contiguous words corresponding to the current window
            for j in range(answer_length):
                line_index, word_index = positions[i + j]

                candidate.append(split_lines[line_index][word_index])

            # Check if the candidate sequence exactly matches the answer
            if candidate == answer_words:
                answer_positions = positions[i : i + answer_length]
                break

        # Guard against answers not in the lines
        if answer_positions is None:
            raise ValueError("Lyrics answer not found in displayed lines.")

        # Replace each answer word with an underscore mask
        for idx, (line_index, word_index) in enumerate(answer_positions):
            word = split_lines[line_index][word_index]

            mask = " ".join("_" for _ in word)

            # Add an extra space between words if this is not the last word in the answer
            if idx < answer_length - 1:
                mask += "  "

            split_lines[line_index][word_index] = mask

        # Reconstruct each line by joining words with single spaces
        masked_lines = [" ".join(words) for words in split_lines]

        # Join lines back into a semicolon-delimited string a la db
        return ";".join(masked_lines)


class ArchiveGameMode(GameMode):
    def resolve(
        self, payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
    ) -> StartGameDTO:
        if payload.date is None:
            raise ArchiveDateNotProvided()

        # Determine which date the daily game should be loaded from
        today = DateType.today()

        date = payload.date

        assert_date_is_not_in_the_future(date, today)

        daily_game = get_daily_game(db, date)

        # Compute a valid audio clip starting position for the archive mode
        audio_start_at = get_audio_start_at_by_game_mode(
            GameModeEnum.ARCHIVE, daily_game.song.duration
        )

        # Resolve daily-mode gameplay constraints
        maximum_attempts = get_maximum_attempts_by_game_mode(GameModeEnum.ARCHIVE)

        expires_in_minutes = get_expires_in_minutes_by_game_mode(GameModeEnum.ARCHIVE)

        return StartGameDTO(
            song=daily_game.song,
            audio_start_at=audio_start_at,
            maximum_attempts=maximum_attempts,
            expires_in_minutes=expires_in_minutes,
            date=date,
        )


MODE_HANDLERS: dict[GameModeEnum, GameMode] = {
    GameModeEnum.ORIGINAL: OriginalGameMode(),
    GameModeEnum.RAPID: RapidGameMode(),
    GameModeEnum.DAILY: DailyGameMode(),
    GameModeEnum.LYRICS: LyricsGameMode(),
    GameModeEnum.ARCHIVE: ArchiveGameMode(),
}


def start_game_service(
    payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
) -> StartGameDTO:
    """
    Resolve a start-game request into the song, timing, and rule constraints
    for the selected game mode.
    """

    handler = MODE_HANDLERS[payload.mode]

    return handler.resolve(payload, db, user_id)


def submit_game_service(payload: SubmitGameRequest, db: Session, user_id: uuid.UUID):
    """
    Validate and persist a completed game session,
    updating user statistics and leaderboards when applicable.
    """

    # Decompose payload
    ws_game_session_id = payload.wsGameSessionID

    mode = payload.mode

    date = payload.date

    won = payload.won

    attempts = payload.attempts

    ##

    # Validation

    # Validate attempt count
    assert_number_of_attempts_do_not_exceed_the_mode_maximum(
        GameModeEnum(mode), attempts
    )

    # Get the WebSocket session from in-memory storage
    ws_game_session = sessions.get(ws_game_session_id)

    # Confirm that a WebSocket game session exists
    if not ws_game_session:
        raise SessionNotFound()

    # Prevent duplicate submissions
    assert_game_session_is_unique(db, ws_game_session_id)

    # Enforce daily-play restriction for authenticated users
    if mode == "daily" and user_id:
        assert_user_has_not_played_the_daily_game(db, user_id)

    ##

    # Persistence

    # Determine game result
    result = Result.win if won else Result.lose

    # Persist the game session in the database
    db_game_session = GameSession(
        wsGameSessionID=ws_game_session_id,
        userID=user_id,
        mode=mode,
        result=result,
        songID=ws_game_session.answer_song_id,
        date=date,
    )

    db.add(db_game_session)

    ##

    # Side-effects

    # Update stats and leaderboard if the user is logged in
    if user_id:
        update_statistics(payload, db, user_id)

        update_leaderboard(payload, db, user_id)

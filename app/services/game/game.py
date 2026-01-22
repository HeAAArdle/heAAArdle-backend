# standard library
import re

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

# services
from app.services.game.game_domain import (
    get_expires_in_minutes_by_game_mode,
    get_audio_start_at_by_game_mode,
    get_maximum_attempts_by_game_mode,
)

from app.services.game.game_provider import get_daily_game

from app.services.game.game_validator import (
    assert_date_is_not_today_or_in_the_future,
    assert_game_session_is_unique,
    assert_date_is_valid_for_non_archive_mode,
    assert_number_of_attempts_do_not_exceed_the_mode_maximum,
    assert_user_has_not_played_the_daily_game,
)

from app.services.song import get_random_song

from app.services.statistics.statistics_update import update_statistics_after_game

from app.services.leaderboards.leaderboards_update import update_leaderboards_after_game

# exceptions
from app.services.exceptions import ArchiveDateNotProvided

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
        assert_date_is_valid_for_non_archive_mode(payload.date)

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
        assert_date_is_valid_for_non_archive_mode(payload.date)

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
        assert_date_is_valid_for_non_archive_mode(payload.date)

        song = get_random_song(db)

        # Split semicolon-delimited raw lyrics
        lines = self._split_lyrics(song.lyrics)

        # Determine the starting line at random
        lyrics_start_at = self._get_lyrics_start_at(lines)

        # Derive the lines displayed to the user
        displayed_lines = lines[lyrics_start_at : lyrics_start_at + self.LINES_TO_SHOW]

        # Pick the answer
        lyrics_answer, answer_positions = self._get_lyrics_answer(displayed_lines)

        # Mask the lyrics
        lyrics_given = self._get_lyrics_given(
            displayed_lines, lyrics_answer, answer_positions
        )

        # Resolve lyrics-mode gameplay constraints
        maximum_attempts = get_maximum_attempts_by_game_mode(GameModeEnum.LYRICS)

        expires_in_minutes = get_expires_in_minutes_by_game_mode(GameModeEnum.LYRICS)

        # Build the start-game response for the lyrics mode
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

    def _get_lyrics_answer(self, lines: list[str]) -> tuple[str, list[tuple[int, int]]]:
        """
        Pick 1-2 contiguous words from the displayed lines.

        Contiguity may cross line boundaries.

        Returns:
            - answer text
            - list of (line_index, word_index) positions in flattened order
        """

        # Flatten all words across all lines while preserving their positions
        # Each entry stores: (line_index, word_index, word)
        words: list[tuple[int, int, str]] = []

        # Iterate through each line and split it into words
        for line_index, line in enumerate(lines):
            # Remove all non-letter characters from the line
            stripped_line = re.sub(r"[^a-zA-Z' ]", "", line)

            for word_index, word in enumerate(stripped_line.split()):
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

        answer_text = " ".join(word for _, _, word in selected)

        # Also return their corresponding positions
        answer_positions = [
            (line_index, word_index) for line_index, word_index, _ in selected
        ]

        return answer_text, answer_positions

    def _get_lyrics_given(
        self,
        lines: list[str],
        lyrics_answer: str,
        answer_positions: list[tuple[int, int]],
    ) -> str:
        """
        Mask the answer words in the displayed lines.

        Mask format is one underscore per letter and two spaces between words.
        """

        # Split the answer string into individual words
        answer_words = lyrics_answer.split()

        # Determine the number of words to mask
        answer_length = len(answer_words)

        # Validate that the provided positions match the number of words in the answer
        if len(answer_positions) != answer_length:
            raise ValueError("Answer positions length does not match answer length.")

        masked_lines = lines.copy()

        # Map from line index to a list of tuples containing (word index in line, position index in answer_positions)
        line_to_positions: dict[int, list[tuple[int, int]]] = {}

        for index, (line_index, word_index) in enumerate(answer_positions):
            # Append the word position and its order in the answer
            line_to_positions.setdefault(line_index, []).append((word_index, index))

        # Process each line independently
        for line_index, positions in line_to_positions.items():
            line = masked_lines[line_index]

            # Identify all word spans (letters and apostrophes) in the current line
            word_spans = [
                (m.start(), m.end(), m.group())
                for m in re.finditer(r"[A-Za-z'-]+", line)
            ]

            # Mask words starting from the end of the line to prevent shifting indices
            for word_index, answer_index in sorted(
                positions, key=lambda x: x[0], reverse=True
            ):
                if word_index >= len(word_spans):
                    raise IndexError("Word index out of bounds.")

                start, end, word = word_spans[word_index]

                # Replace each letter with an underscore and add spacing for readability
                mask = " ".join("_" for _ in word)

                # Add extra spacing if the next answer word is on the same line
                if answer_index < answer_length - 1:
                    next_line_index, _ = answer_positions[answer_index + 1]
                    if next_line_index == line_index:
                        mask += " "

                # Replace the original word with the generated mask
                line = line[:start] + mask + line[end:]

            # Update the masked line in the final output
            masked_lines[line_index] = line

        # Combine all lines into a single semicolon-delimited string for storage
        return "; ".join(masked_lines)


class ArchiveGameMode(GameMode):
    def resolve(
        self, payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
    ) -> StartGameDTO:
        # Disallow empty date input for archive mode
        if payload.date is None:
            raise ArchiveDateNotProvided()

        date = payload.date

        # Disallow non-archive date requests
        assert_date_is_not_today_or_in_the_future(date)

        # Get the daily game settings for the given date
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
    Resolve a start-game request into the song, timing, and rule constraints for the selected game mode.
    """

    handler = MODE_HANDLERS[payload.mode]

    return handler.resolve(payload, db, user_id)


def submit_game_service(
    payload: SubmitGameRequest, db: Session, user_id: uuid.UUID
):
    """
    Validate a completed game session and return the result.
    Persist the session and update user-related data only if the user is authenticated.
    """

    # Decompose payload
    ws_game_session_id = payload.wsGameSessionID

    songID = payload.songID

    mode = GameModeEnum(payload.mode)

    won = payload.won

    attempts = payload.attempts

    ##

    # Validation

    # Validate attempt count
    assert_number_of_attempts_do_not_exceed_the_mode_maximum(mode, attempts)

    # Prevent duplicate submissions
    assert_game_session_is_unique(db, ws_game_session_id)

    # Enforce one daily play per user for daily mode
    if mode == GameModeEnum.DAILY:
        assert_user_has_not_played_the_daily_game(db, user_id)

    ##

    # Result computation

    # Determine the game outcome
    result = Result.win if won else Result.lose

    # Assign date for daily games
    date = DateType.today() if mode == GameModeEnum.DAILY else None

    ##

    # Persistence

    try:
        # Persist the completed game session
        db_game_session = GameSession(
            wsGameSessionID=ws_game_session_id,
            userID=user_id,
            mode=mode,
            result=result,
            songID=songID,
            date=date,
        )

        db.add(db_game_session)

        ##

        # Side Effects

        # Update user statistics and leaderboard standings
        update_statistics_after_game(db, user_id, mode, won, attempts)

        update_leaderboards_after_game(db, user_id, mode)

        # Commit all database changes
        db.commit()

    except:
        # Roll back all changes if any persistence step fails
        db.rollback()

    return None

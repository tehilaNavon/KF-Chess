"""ELO rating math. Pure functions only: no database, no side effects.

Score convention: 1.0 = win, 0.5 = draw, 0.0 = loss.
"""

from __future__ import annotations

DEFAULT_RATING = 1200
K_FACTOR = 32

SCORE_WIN = 1.0
SCORE_DRAW = 0.5
SCORE_LOSS = 0.0


def expected_score(rating: int, opponent_rating: int) -> float:
    """Probability that a ``rating`` player beats an ``opponent_rating`` player."""
    return 1.0 / (1.0 + 10 ** ((opponent_rating - rating) / 400.0))


def updated_rating(
    rating: int,
    opponent_rating: int,
    score: float,
    k_factor: int = K_FACTOR,
) -> int:
    """Return the player's new rating after a game with the given ``score``."""
    expected = expected_score(rating, opponent_rating)
    return round(rating + k_factor * (score - expected))


def rating_delta(
    rating: int,
    opponent_rating: int,
    score: float,
    k_factor: int = K_FACTOR,
) -> int:
    """Return the change in rating (new - old) for the given ``score``."""
    return updated_rating(rating, opponent_rating, score, k_factor) - rating

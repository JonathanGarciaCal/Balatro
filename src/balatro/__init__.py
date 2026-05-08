"""balatro package (minimal API for notebooks).

This package is intended to be a local importable package used by notebooks
and small experiments. Keep logic here for reusability and testing.
"""
__all__ = [
    "data",
    "features",
    "models",
    "BalatroClient",
    "BalatroAPI",
    "BalatroSession",
    "Strategy",
    "GreedyStrategy",
    "RandomStrategy",
    "PlayCardsStrategy",
    "run_game_with_strategy",
    "Deck",
    "Stake",
    "Suit",
    "Rank",
    "Seal",
    "Enhancement",
    "Edition",
    "GameState",
    "__version__",
]
__version__ = "0.1.0"

from . import data, features, models
from .client import BalatroClient
from .api import BalatroAPI
from .session import BalatroSession
from .strategies import (
    Strategy,
    GreedyStrategy,
    RandomStrategy,
    PlayCardsStrategy,
    run_game_with_strategy,
)
from .types import (
    Deck,
    Stake,
    Suit,
    Rank,
    Seal,
    Enhancement,
    Edition,
    GameState,
)

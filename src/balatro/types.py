"""
Type hints and enums for the Balatro API SDK.

Defines GameState, Card, and game-related enums that match the OpenRPC schema.
"""

from typing import Any, Literal, TypedDict, Optional
from enum import Enum


# === Enums ===

class Deck(str, Enum):
    """Available starting decks."""
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    PURPLE = "PURPLE"
    BLACK = "BLACK"


class Stake(str, Enum):
    """Available stake levels."""
    WHITE = "WHITE"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    PURPLE = "PURPLE"
    BLACK = "BLACK"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class Suit(str, Enum):
    """Playing card suits."""
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"
    SPADES = "S"


class Rank(str, Enum):
    """Playing card ranks."""
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


class Seal(str, Enum):
    """Card seals (playing cards only)."""
    GOLD = "GOLD"
    RED = "RED"
    BLUE = "BLUE"
    PURPLE = "PURPLE"


class Enhancement(str, Enum):
    """Card enhancements (playing cards only)."""
    BONUS = "BONUS"
    MULT = "MULT"
    GLASS = "GLASS"
    STEEL = "STEEL"
    STONE = "STONE"
    GOLD = "GOLD"
    WILD = "WILD"


class Edition(str, Enum):
    """Card editions."""
    FOIL = "FOIL"
    HOLOGRAPHIC = "HOLOGRAPHIC"
    POLYCHROME = "POLYCHROME"
    NEGATIVE = "NEGATIVE"


# === TypedDicts ===

class Card(TypedDict, total=False):
    """Represents a card in the game."""
    key: str
    seal: Optional[str]
    enhancement: Optional[str]
    edition: Optional[str]
    eternal: bool
    perishable: Optional[int]
    rental: bool
    sell_value: Optional[int]
    name: str


class Hand(TypedDict, total=False):
    """Player's hand state."""
    cards: list[Card]
    size: int


class Shop(TypedDict, total=False):
    """Shop state during SHOP phase."""
    cards: list[Card]
    vouchers: list[dict[str, Any]]
    packs: list[dict[str, Any]]
    stock: dict[str, int]


class GameState(TypedDict, total=False):
    """Complete game state returned by most API methods."""
    state: Literal[
        "BLIND_SELECT",
        "SELECTING_HAND",
        "ROUND_EVAL",
        "SHOP",
        "GAME_OVER",
    ]
    seed: str
    ante_num: int
    round_num: int
    hand: Hand
    shop: Shop
    deck: dict[str, Any]
    jokers: list[Card]
    consumables: list[Card]
    vouchers: list[str]
    money: int
    chips: int
    mult: int
    won: bool
    score: int


class RPCError(TypedDict):
    """JSON-RPC error response."""
    code: int
    message: str
    data: Optional[dict[str, Any]]


class RPCResponse(TypedDict, total=False):
    """JSON-RPC response envelope."""
    jsonrpc: str
    result: Any
    error: RPCError
    id: int | str


class PathResult(TypedDict):
    """Result for file operations (save, load, screenshot)."""
    path: str


# === Error Codes ===

class ErrorCode(int, Enum):
    """JSON-RPC error codes."""
    INTERNAL_ERROR = -32000
    BAD_REQUEST = -32001
    INVALID_STATE = -32002
    NOT_ALLOWED = -32003


# === Helper Functions ===

def card_key_from_suit_rank(suit: Suit, rank: Rank) -> str:
    """Create a playing card key from suit and rank.
    
    Examples:
        card_key_from_suit_rank(Suit.HEARTS, Rank.ACE) -> "H_A"
        card_key_from_suit_rank(Suit.SPADES, Rank.KING) -> "S_K"
    """
    return f"{suit.value}_{rank.value}"


def parse_card_key(key: str) -> tuple[Optional[str], Optional[str]]:
    """Parse a card key into type and name.
    
    Returns (card_type, card_name) where:
    - card_type is "joker", "consumable", "voucher", or "playing"
    - card_name is the specific card identifier
    
    Examples:
        parse_card_key("j_joker") -> ("joker", "joker")
        parse_card_key("H_A") -> ("playing", "H_A")
        parse_card_key("c_fool") -> ("consumable", "fool")
    """
    if key.startswith("j_"):
        return ("joker", key[2:])
    elif key.startswith("c_"):
        return ("consumable", key[2:])
    elif key.startswith("v_"):
        return ("voucher", key[2:])
    elif "_" in key and len(key) == 3:  # Suit_Rank format
        return ("playing", key)
    return (None, None)

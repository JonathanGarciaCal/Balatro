"""
Session management for Balatro games.

Provides a higher-level abstraction for managing game sessions, including
state caching, validation, and context manager support.
"""

from typing import Optional, Callable, Any
import logging

from .api import BalatroAPI
from .types import GameState, Deck, Stake

logger = logging.getLogger(__name__)


class BalatroSession:
    """
    High-level session manager for a Balatro game.
    
    Handles game lifecycle, caches state, provides validation, and supports
    context manager usage. Recommended for most use cases that need more than
    raw API calls.
    
    Example:
        with BalatroSession() as session:
            session.start(Deck.RED, Stake.WHITE)
            while not session.is_over():
                action = decide_action(session.state)
                session.execute_action(action)
    """
    
    def __init__(self, api: Optional[BalatroAPI] = None):
        """
        Initialize a game session.
        
        Args:
            api: BalatroAPI instance (creates new one if not provided)
        """
        self.api = api or BalatroAPI()
        self._state: Optional[GameState] = None
        self._is_connected = False
    
    def connect(self) -> bool:
        """
        Connect to the API server and verify it's alive.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.api.client.is_alive():
                self._is_connected = True
                logger.info("Connected to Balatro API server")
                return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
        
        return False
    
    @property
    def state(self) -> Optional[GameState]:
        """Get cached game state."""
        return self._state
    
    def refresh(self) -> GameState:
        """
        Refresh game state from server.
        
        Returns:
            Updated GameState
        """
        self._state = self.api.gamestate()
        return self._state
    
    def start(
        self,
        deck: Deck | str,
        stake: Stake | str,
        seed: Optional[str] = None,
    ) -> GameState:
        """
        Start a new game.
        
        Args:
            deck: Starting deck
            stake: Stake level
            seed: Optional seed for reproducibility
        
        Returns:
            GameState after game start
        """
        self._state = self.api.start(deck, stake, seed)
        logger.info(f"Game started with seed: {self._state.get('seed')}")
        return self._state
    
    def select_blind(self) -> GameState:
        """Select the current blind."""
        if self.state["state"] != "BLIND_SELECT":
            raise ValueError(f"Cannot select blind in state {self.state['state']}")
        
        self._state = self.api.select()
        return self._state
    
    def play_cards(self, cards: list[int]) -> GameState:
        """
        Play cards from hand.
        
        Args:
            cards: List of 0-based card indices
        
        Returns:
            GameState after playing cards
        """
        if self.state["state"] != "SELECTING_HAND":
            raise ValueError(f"Cannot play cards in state {self.state['state']}")
        
        self._state = self.api.play(cards)
        return self._state
    
    def cash_out(self) -> GameState:
        """Cash out after scoring."""
        if self.state["state"] != "ROUND_EVAL":
            raise ValueError(f"Cannot cash out in state {self.state['state']}")
        
        self._state = self.api.cash_out()
        return self._state
    
    def buy_card(self, card_index: int) -> GameState:
        """Buy a card from shop."""
        if self.state["state"] != "SHOP":
            raise ValueError(f"Cannot buy in state {self.state['state']}")
        
        self._state = self.api.buy(card=card_index)
        return self._state
    
    def buy_pack(self, pack_index: int) -> GameState:
        """Buy a booster pack from shop."""
        if self.state["state"] != "SHOP":
            raise ValueError(f"Cannot buy in state {self.state['state']}")
        
        self._state = self.api.buy(pack=pack_index)
        return self._state
    
    def next_round(self) -> GameState:
        """Skip shop and go to next round."""
        if self.state["state"] != "SHOP":
            raise ValueError(f"Cannot skip shop in state {self.state['state']}")
        
        self._state = self.api.next_round()
        return self._state
    
    def menu(self) -> GameState:
        """Return to main menu."""
        self._state = self.api.menu()
        return self._state
    
    def is_over(self) -> bool:
        """Check if game is over."""
        return self.state and self.state.get("state") == "GAME_OVER"
    
    def won(self) -> bool:
        """Check if game was won."""
        return self.state and self.state.get("won", False)
    
    def save(self, path: Optional[str] = None):
        """Save current game state."""
        return self.api.save(path)
    
    def load(self, path: str):
        """Load a saved game state."""
        self._state = self.api.load(path)
        return self._state
    
    def screenshot(self, path: Optional[str] = None):
        """Take a screenshot of current game."""
        return self.api.screenshot(path)
    
    def close(self) -> None:
        """Close the session and clean up."""
        try:
            self.api.client.close()
            logger.info("Session closed")
        except Exception as e:
            logger.error(f"Error closing session: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        if not self._is_connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

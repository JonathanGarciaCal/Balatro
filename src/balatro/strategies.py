"""
Strategy base class and examples for Balatro bots.

Provides a framework for implementing custom game strategies and decision logic.
Strategies can be used with BalatroSession to automate gameplay.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
import logging

from .session import BalatroSession
from .types import GameState

logger = logging.getLogger(__name__)


class Strategy(ABC):
    """
    Base class for game strategies.
    
    Subclass this to implement custom decision logic for playing Balatro.
    The strategy receives the current game state and must decide the next action.
    
    Example:
        class GreedyStrategy(Strategy):
            def decide_action(self, state: GameState) -> str:
                if state["state"] == "BLIND_SELECT":
                    return "select"
                elif state["state"] == "SELECTING_HAND":
                    return "play"
                # ... etc
    """
    
    @abstractmethod
    def decide_action(self, state: GameState) -> str:
        """
        Decide the next action based on game state.
        
        Args:
            state: Current GameState
        
        Returns:
            Action name as string (e.g., "select", "play", "cash_out", "buy_card")
        """
        pass
    
    def on_game_start(self, state: GameState) -> None:
        """Called when game starts (optional hook)."""
        pass
    
    def on_game_over(self, state: GameState) -> None:
        """Called when game ends (optional hook)."""
        pass
    
    def on_round_start(self, state: GameState) -> None:
        """Called at start of each round (optional hook)."""
        pass
    
    def on_error(self, error: Exception) -> None:
        """Called when an error occurs during gameplay (optional hook)."""
        logger.error(f"Strategy error: {error}")


class GreedyStrategy(Strategy):
    """
    Simple greedy strategy: play cards greedily, skip shopping, advance rounds.
    
    Rules:
    - BLIND_SELECT: Select current blind
    - SELECTING_HAND: Play first 5 cards
    - ROUND_EVAL: Cash out
    - SHOP: Skip and go to next round
    """
    
    def decide_action(self, state: GameState) -> str:
        """Decide action using greedy heuristic."""
        game_state = state.get("state")
        
        if game_state == "BLIND_SELECT":
            return "select"
        elif game_state == "SELECTING_HAND":
            return "play"
        elif game_state == "ROUND_EVAL":
            return "cash_out"
        elif game_state == "SHOP":
            return "next_round"
        elif game_state == "GAME_OVER":
            return "end"
        
        logger.warning(f"Unknown game state: {game_state}")
        return "skip"


class RandomStrategy(Strategy):
    """
    Random strategy: make random valid moves.
    
    Useful for testing and baseline comparisons.
    Requires implementing action dispatch with actual card selection logic.
    """
    
    def decide_action(self, state: GameState) -> str:
        """Decide action randomly from valid options."""
        import random
        
        game_state = state.get("state")
        
        if game_state == "BLIND_SELECT":
            return "select"
        elif game_state == "SELECTING_HAND":
            return "play"  # Card selection delegated to caller
        elif game_state == "ROUND_EVAL":
            return "cash_out"
        elif game_state == "SHOP":
            # Randomly buy or skip
            return random.choice(["buy_card", "next_round"])
        elif game_state == "GAME_OVER":
            return "end"
        
        return "skip"


class PlayCardsStrategy(Strategy):
    """
    Strategy that plays N cards from hand (configurable).
    
    Subclass and override num_cards to change card play behavior.
    """
    
    def __init__(self, num_cards: int = 5):
        """
        Initialize with target number of cards to play.
        
        Args:
            num_cards: Number of cards to play each hand (default: 5)
        """
        self.num_cards = num_cards
    
    def decide_action(self, state: GameState) -> str:
        """Decide action based on game state."""
        game_state = state.get("state")
        
        if game_state == "BLIND_SELECT":
            return "select"
        elif game_state == "SELECTING_HAND":
            return "play"
        elif game_state == "ROUND_EVAL":
            return "cash_out"
        elif game_state == "SHOP":
            return "next_round"
        elif game_state == "GAME_OVER":
            return "end"
        
        return "skip"
    
    def get_cards_to_play(self, state: GameState) -> list[int]:
        """Get list of card indices to play."""
        hand = state.get("hand", {})
        cards = hand.get("cards", [])
        num_to_play = min(self.num_cards, len(cards))
        return list(range(num_to_play))


def run_game_with_strategy(
    session: BalatroSession,
    strategy: Strategy,
    max_rounds: Optional[int] = None,
    verbose: bool = False,
) -> dict:
    """
    Run a complete game using a given strategy.
    
    Args:
        session: BalatroSession instance
        strategy: Strategy instance
        max_rounds: Optional max rounds to play (prevents infinite loops)
        verbose: Print game progress
    
    Returns:
        {"won": bool, "ante": int, "round": int, "score": int}
    """
    from .types import Deck, Stake
    
    try:
        # Start game
        state = session.start(Deck.RED, Stake.WHITE)
        strategy.on_game_start(state)
        
        if verbose:
            print(f"Game started with seed: {state['seed']}")
        
        round_count = 0
        
        # Main loop
        while state.get("state") != "GAME_OVER":
            if max_rounds and round_count >= max_rounds:
                if verbose:
                    print(f"Max rounds ({max_rounds}) reached, ending game")
                break
            
            # Get decision
            action = strategy.decide_action(state)
            
            if verbose:
                print(f"State: {state.get('state')}, Action: {action}")
            
            # Execute action
            if action == "end":
                break
            elif action == "select":
                state = session.select_blind()
                strategy.on_round_start(state)
            elif action == "play":
                # Get cards to play from strategy
                if isinstance(strategy, PlayCardsStrategy):
                    cards = strategy.get_cards_to_play(state)
                else:
                    cards = [0]  # Default: play first card
                
                state = session.play_cards(cards)
            elif action == "cash_out":
                state = session.cash_out()
            elif action == "buy_card":
                # Buy first card if available
                shop = state.get("shop", {})
                cards = shop.get("cards", [])
                if cards:
                    state = session.buy_card(0)
                else:
                    state = session.next_round()
            elif action == "next_round":
                state = session.next_round()
            elif action == "skip":
                state = session.refresh()
            else:
                logger.warning(f"Unknown action: {action}")
                state = session.refresh()
            
            round_count += 1
        
        strategy.on_game_over(state)
        
        result = {
            "won": state.get("won", False),
            "ante": state.get("ante_num", 0),
            "round": state.get("round_num", 0),
            "score": state.get("score", 0),
        }
        
        if verbose:
            status = "WON" if result["won"] else "LOST"
            print(f"Game Over ({status}): Ante {result['ante']}, Score {result['score']}")
        
        return result
    
    except Exception as e:
        strategy.on_error(e)
        logger.error(f"Game error: {e}")
        raise

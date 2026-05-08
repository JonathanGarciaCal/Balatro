"""
High-level API wrapper methods for the Balatro JSON-RPC interface.

Provides convenient method calls for common game actions like start, play, buy, etc.
Uses BalatroClient under the hood for low-level RPC communication.
"""

from typing import Optional, Any
from .client import BalatroClient
from .types import GameState, Deck, Stake, Seal, Enhancement, Edition, PathResult


class BalatroAPI:
    """
    High-level wrapper around Balatro JSON-RPC methods.
    
    Groups related methods by functionality (state, gameplay, shop, cards, etc.)
    and provides type-safe parameter passing and result handling.
    
    Example:
        api = BalatroAPI()
        state = api.start(Deck.RED, Stake.WHITE)
        state = api.select()
        state = api.play([0, 1, 2])
        state = api.cash_out()
    """
    
    def __init__(self, client: Optional[BalatroClient] = None):
        """
        Initialize the API wrapper.
        
        Args:
            client: BalatroClient instance (creates new one if not provided)
        """
        self.client = client or BalatroClient()
    
    # === State & Discovery ===
    
    def health(self) -> dict:
        """
        Health check endpoint.
        
        Returns:
            {"status": "ok"} if server is healthy
        """
        return self.client.call("health")
    
    def discover(self) -> dict:
        """
        Get the OpenRPC schema for this API.
        
        Useful for discovering available methods, parameter schemas, and error types.
        
        Returns:
            OpenRPC 1.3.2 specification document
        """
        return self.client.call("rpc.discover")
    
    def gamestate(self) -> GameState:
        """
        Get the complete current game state.
        
        This is the canonical source of truth for game state.
        Call before making decisions or when game state might have changed.
        
        Returns:
            GameState: Complete game state object
        """
        return self.client.call("gamestate")
    
    # === Core Gameplay ===
    
    def start(
        self,
        deck: Deck | str,
        stake: Stake | str,
        seed: Optional[str] = None,
    ) -> GameState:
        """
        Start a new game run.
        
        Args:
            deck: Starting deck (e.g., Deck.RED or "RED")
            stake: Stake level (e.g., Stake.WHITE or "WHITE")
            seed: Optional seed for deterministic play
        
        Returns:
            GameState: Game state after start (state will be BLIND_SELECT)
        """
        params = {
            "deck": deck.value if isinstance(deck, Deck) else deck,
            "stake": stake.value if isinstance(stake, Stake) else stake,
        }
        if seed:
            params["seed"] = seed
        
        return self.client.call("start", params)
    
    def select(self) -> GameState:
        """
        Select the current blind to begin the round.
        
        Can only be called when game state is BLIND_SELECT.
        
        Returns:
            GameState: Game state after selection (state will be SELECTING_HAND)
        """
        return self.client.call("select")
    
    def play(self, cards: list[int]) -> GameState:
        """
        Play cards from the hand.
        
        Args:
            cards: List of 0-based card indices from hand.cards
        
        Returns:
            GameState: Game state after play
        """
        return self.client.call("play", {"cards": cards})
    
    def cash_out(self) -> GameState:
        """
        Collect rewards and proceed to shop.
        
        Called after scoring a round. Transitions from ROUND_EVAL to SHOP.
        
        Returns:
            GameState: Game state after cashing out
        """
        return self.client.call("cash_out")
    
    def next_round(self) -> GameState:
        """
        Skip the shop and proceed to the next round.
        
        Can be called from SHOP state to advance without buying anything.
        
        Returns:
            GameState: Game state after advancing (will be BLIND_SELECT for next round)
        """
        return self.client.call("next_round")
    
    def menu(self) -> GameState:
        """
        Return to main menu, ending the current game.
        
        Returns:
            GameState: Game state after returning to menu
        """
        return self.client.call("menu")
    
    # === Shop Actions ===
    
    def buy(
        self,
        card: Optional[int] = None,
        voucher: Optional[int] = None,
        pack: Optional[int] = None,
    ) -> GameState:
        """
        Buy a shop item. Provide exactly one of card, voucher, or pack.
        
        Args:
            card: 0-based index of shop card to buy
            voucher: 0-based index of shop voucher to buy
            pack: 0-based index of shop pack to buy
        
        Returns:
            GameState: Game state after purchase
        """
        params = {}
        count = sum([card is not None, voucher is not None, pack is not None])
        if count != 1:
            raise ValueError("Exactly one of card, voucher, or pack must be specified")
        
        if card is not None:
            params["card"] = card
        elif voucher is not None:
            params["voucher"] = voucher
        else:
            params["pack"] = pack
        
        return self.client.call("buy", params)
    
    def reroll(self, shop: bool = False) -> GameState:
        """
        Reroll shop items or deck.
        
        Args:
            shop: If True, reroll shop items; if False, reroll deck
        
        Returns:
            GameState: Game state after reroll
        """
        params = {"shop": shop}
        return self.client.call("reroll", params)
    
    # === Card Operations ===
    
    def add(
        self,
        key: str,
        seal: Optional[Seal | str] = None,
        edition: Optional[Edition | str] = None,
        enhancement: Optional[Enhancement | str] = None,
        eternal: bool = False,
        perishable: Optional[int] = None,
        rental: bool = False,
    ) -> GameState:
        """
        Add a new card to the game (debug/cheat method).
        
        Args:
            key: Card key (e.g., "j_joker", "H_A", "c_fool", "v_voucher")
            seal: Card seal (playing cards only)
            edition: Card edition
            enhancement: Card enhancement (playing cards only)
            eternal: If True, card cannot be sold/destroyed (jokers only)
            perishable: Rounds before card perishes (jokers only)
            rental: If True, card costs $1/round (jokers only)
        
        Returns:
            GameState: Game state after adding card
        """
        params = {"key": key}
        
        if seal:
            params["seal"] = seal.value if isinstance(seal, Seal) else seal
        if edition:
            params["edition"] = edition.value if isinstance(edition, Edition) else edition
        if enhancement:
            params["enhancement"] = enhancement.value if isinstance(enhancement, Enhancement) else enhancement
        if eternal:
            params["eternal"] = eternal
        if perishable:
            params["perishable"] = perishable
        if rental:
            params["rental"] = rental
        
        return self.client.call("add", params)
    
    def discard(self, cards: list[int]) -> GameState:
        """
        Discard cards from hand.
        
        Args:
            cards: List of 0-based hand card indices to discard
        
        Returns:
            GameState: Game state after discarding
        """
        return self.client.call("discard", {"cards": cards})
    
    def sell(self, cards: list[int]) -> GameState:
        """
        Sell jokers or consumables.
        
        Args:
            cards: List of 0-based joker/consumable indices to sell
        
        Returns:
            GameState: Game state after selling
        """
        return self.client.call("sell", {"cards": cards})
    
    def rearrange(self, cards: list[int]) -> GameState:
        """
        Rearrange order of cards in hand.
        
        Args:
            cards: Reordered list of 0-based hand card indices
        
        Returns:
            GameState: Game state after rearranging
        """
        return self.client.call("rearrange", {"cards": cards})
    
    def use(self, card: int) -> GameState:
        """
        Use/activate a consumable card.
        
        Args:
            card: 0-based index of consumable to use
        
        Returns:
            GameState: Game state after using consumable
        """
        return self.client.call("use", {"card": card})
    
    # === File/Debug Operations ===
    
    def save(self, path: Optional[str] = None) -> PathResult:
        """
        Save current game state to disk.
        
        Args:
            path: Optional file path (if not provided, saves to default location)
        
        Returns:
            PathResult: {"path": saved_file_path}
        """
        params = {}
        if path:
            params["path"] = path
        
        return self.client.call("save", params)
    
    def load(self, path: str) -> GameState:
        """
        Load a previously saved game state.
        
        Args:
            path: Path to the saved game file
        
        Returns:
            GameState: Loaded game state
        """
        return self.client.call("load", {"path": path})
    
    def screenshot(self, path: Optional[str] = None) -> PathResult:
        """
        Capture a screenshot of the game.
        
        Args:
            path: Optional output path (if not provided, uses default)
        
        Returns:
            PathResult: {"path": screenshot_file_path}
        """
        params = {}
        if path:
            params["path"] = path
        
        return self.client.call("screenshot", params)
    
    def set(self, field: str, value: Any) -> GameState:
        """
        Set a debug field (advanced/cheat method).
        
        Args:
            field: Field name to set
            value: Value to set
        
        Returns:
            GameState: Game state after modification
        """
        return self.client.call("set", {"field": field, "value": value})
    
    def skip(self) -> GameState:
        """
        Skip to next game phase/state.
        
        Returns:
            GameState: Game state after skipping
        """
        return self.client.call("skip")

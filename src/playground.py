"""
Playground for testing and experimenting with the Balatro API.

Examples of various API calls and game interactions.
"""
#%%
from balatro import BalatroAPI
from balatro.types import Deck, Stake, Seal, Enhancement, Edition
import json


def pretty_print(data, title=""):
    """Pretty print data structures."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    if isinstance(data, dict) and "gamestate" in data:
        state = data["gamestate"]
        print(f"State: {state.get('state')}")
        print(f"Round: {state.get('round')}")
        print(f"Money: ${state.get('money')}")
        print(f"Score: {state.get('score')}")
        if "hand" in state:
            print(f"Hand: {len(state['hand'].get('cards', []))} cards")
        if "jokers" in state:
            print(f"Jokers: {len(state['jokers'].get('cards', []))} jokers")
    else:
        print(json.dumps(data, indent=2))


def example_basic_game():
    """Example: Play a basic game run."""
    api = BalatroAPI()

    # Check server health
    print("\n1. Checking API health...")
    health = api.health()
    print(f"Status: {health.get('status')}")

    # Start a new game
    print("\n2. Starting a new game...")
    state = api.start(Deck.RED, Stake.WHITE, seed="test123")
    pretty_print(state, "Game Started")

    # Select the blind
    print("\n3. Selecting blind...")
    state = api.select()
    pretty_print(state, "Blind Selected")

    # Play cards from hand
    print("\n4. Playing cards...")
    state = api.play([0, 1, 2])
    pretty_print(state, "Cards Played")


def example_shop_interaction():
    """Example: Navigate the shop and make purchases."""
    api = BalatroAPI()

    state = api.start(Deck.BLUE, Stake.RED)
    state = api.select()
    state = api.play([0, 1, 2, 3, 4])

    print("\n5. Cashing out and entering shop...")
    state = api.cash_out()
    pretty_print(state, "Shop Entered")

    # Get current state to see shop items
    current_state = api.gamestate()
    shop = current_state.get("gamestate", {}).get("shop", {})

    if shop.get("cards"):
        print(f"\nAvailable cards: {len(shop['cards'])}")
        # Buy the first available card
        print("Buying first card...")
        state = api.buy(card=0)
        pretty_print(state, "Card Purchased")

    # Proceed to next round
    print("\n6. Moving to next round...")
    state = api.next_round()
    pretty_print(state, "Next Round")


def example_card_operations():
    """Example: Add, manipulate, and sell cards."""
    api = BalatroAPI()

    state = api.start(Deck.GREEN, Stake.GREEN)
    state = api.select()

    print("\n7. Adding a special joker...")
    # Add a joker with special properties
    state = api.add(
        key="j_joker",
        edition=Edition.HOLOGRAPHIC,
        eternal=False
    )
    pretty_print(state, "Joker Added")

    print("\n8. Adding a playing card with seal...")
    state = api.add(
        key="H_A",  # Ace of hearts
        seal=Seal.RED,
        enhancement=Enhancement.BONUS
    )
    pretty_print(state, "Card Added with Seal")

    print("\n9. Playing and discarding cards...")
    state = api.play([0, 1, 2])
    pretty_print(state, "Cards Played")

    # Check current state for what we can discard
    current = api.gamestate()
    hand_size = len(current.get("gamestate", {}).get("hand", {}).get("cards", []))
    if hand_size > 0:
        print(f"\n10. Discarding first card...")
        state = api.discard([0])
        pretty_print(state, "Card Discarded")


def example_rerolling():
    """Example: Reroll shop items."""
    api = BalatroAPI()

    state = api.start(Deck.PURPLE, Stake.WHITE)
    state = api.select()
    state = api.play([0, 1, 2])
    state = api.cash_out()

    print("\n11. Rerolling shop...")
    current = api.gamestate()
    money = current.get("gamestate", {}).get("money", 0)

    if money >= 1:
        state = api.reroll(shop=True)
        pretty_print(state, "Shop Rerolled")

    print("\n12. Rerolling deck...")
    state = api.reroll(shop=False)
    pretty_print(state, "Deck Rerolled")


def example_debug_operations():
    """Example: Debug operations like save/load and set."""
    api = BalatroAPI()

    state = api.start(Deck.BLACK, Stake.BLUE)

    print("\n13. Taking a screenshot...")
    result = api.screenshot()
    print(f"Screenshot saved to: {result.get('path')}")

    print("\n14. Setting a debug field...")
    state = api.set("money", 9999)
    pretty_print(state, "Money Set to 9999")

    print("\n15. Saving game state...")
    result = api.save()
    print(f"Game saved to: {result.get('path')}")


def example_api_discovery():
    """Example: Discover available API methods."""
    api = BalatroAPI()

    print("\n16. Discovering API schema...")
    schema = api.discover()

    # Extract method names
    methods = [m.get("name") for m in schema.get("methods", [])]
    print(f"\nAvailable methods ({len(methods)}):")
    for method in sorted(methods):
        print(f"  - {method}")


def run_all_examples():
    """Run all examples in sequence."""
    try:
        example_basic_game()
        # Uncomment to run other examples:
        # example_shop_interaction()
        # example_card_operations()
        # example_rerolling()
        # example_debug_operations()
        # example_api_discovery()

        print("\n" + "="*60)
        print("  Examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    api = BalatroAPI()
    # Run specific examples
    # run_all_examples()

    # Or try individual examples:
    # example_basic_game()
    # example_shop_interaction()
    # example_card_operations()
    # example_rerolling()
    # example_debug_operations()
    # example_api_discovery()

# %%

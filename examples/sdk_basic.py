#%%
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

"""
Example: Using the Balatro Python SDK to play a simple game.

This script demonstrates the high-level BalatroSession API and how to use
it to automate gameplay. Compare with examples/bot.py which uses raw JSON-RPC calls.
"""

from balatro import BalatroSession, GreedyStrategy, Deck, Stake, run_game_with_strategy


def simple_game_loop():
    """Play a single game using BalatroSession."""
    print("=== Simple Game Loop (Session API) ===\n")
    
    with BalatroSession() as session:
        # Start a game
        state = session.start(Deck.RED, Stake.WHITE)
        print(f"Started game with seed: {state['seed']}")
        print(f"Initial state: {state['state']}\n")
        
        round_num = 1
        max_rounds = 20  # Prevent infinite loops during testing
        
        # Main game loop
        while not session.is_over() and round_num <= max_rounds:
            current_state = session.state
            game_phase = current_state["state"]
            
            print(f"Round {round_num}, Phase: {game_phase}")
            
            try:
                match game_phase:
                    case "BLIND_SELECT":
                        # Select the blind
                        session.select_blind()
                        print("  -> Selected blind")
                    
                    case "SELECTING_HAND":
                        # Play first 5 cards
                        hand_size = len(current_state["hand"]["cards"])
                        num_to_play = min(5, hand_size)
                        cards = list(range(num_to_play))
                        session.play_cards(cards)
                        print(f"  -> Played {num_to_play} cards")
                    
                    case "ROUND_EVAL":
                        # Cash out and collect rewards
                        session.cash_out()
                        print("  -> Cashed out")
                    
                    case "SHOP":
                        # Skip shop for now
                        session.next_round()
                        print("  -> Skipped shop")
                    
                    case _:
                        print(f"  -> Unknown state: {game_phase}")
                        break
                
                round_num += 1
                print()
            
            except Exception as e:
                print(f"  ERROR: {e}\n")
                break
        
        # Game ended
        final_state = session.state
        if final_state.get("won"):
            print(f"✓ VICTORY! Final ante: {final_state['ante_num']}")
        else:
            print(f"✗ GAME OVER. Final ante: {final_state['ante_num']}")
        
        print(f"Final score: {final_state['score']}\n")
        
        return final_state.get("won", False)


def strategy_based_game():
    """Play a game using a pre-built strategy."""
    print("=== Strategy-Based Game (GreedyStrategy) ===\n")
    
    with BalatroSession() as session:
        # Create a greedy strategy
        strategy = GreedyStrategy()
        
        # Run the game
        result = run_game_with_strategy(
            session,
            strategy,
            max_rounds=20,
            verbose=True,
        )
        
        print(f"\nGame Result: {result}\n")
        return result.get("won", False)


def api_level_example():
    """Example using the lower-level BalatroAPI directly."""
    print("=== API-Level Example (BalatroAPI) ===\n")
    
    from balatro import BalatroAPI
    
    api = BalatroAPI()
    
    # Start a game
    print("Starting game...")
    state = api.start("RED", "WHITE")
    print(f"  Seed: {state['seed']}, State: {state['state']}\n")
    
    # Select blind
    print("Selecting blind...")
    state = api.select()
    print(f"  New state: {state['state']}\n")
    
    # Play cards
    print("Playing cards 0, 1, 2...")
    state = api.play([0, 1, 2])
    print(f"  New state: {state['state']}\n")
    
    # Cash out
    print("Cashing out...")
    state = api.cash_out()
    print(f"  New state: {state['state']}\n")
    
    api.client.close()


def compare_apis():
    """Compare raw RPC (old) vs SDK (new) approach."""
    print("=== Comparison: Raw RPC vs SDK ===\n")
    
    # Old way (from examples/bot.py)
    print("OLD WAY (Raw JSON-RPC):")
    print("""
    import requests
    URL = "http://127.0.0.1:12346"
    
    def rpc(method: str, params: dict = {}):
        response = requests.post(URL, json={
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        })
        if "error" in response.json():
            raise Exception(response.json()["error"]["message"])
        return response.json()["result"]
    
    state = rpc("start", {"deck": "RED", "stake": "WHITE"})
    state = rpc("select")
    state = rpc("play", {"cards": [0, 1, 2]})
    state = rpc("cash_out")
    """)
    
    # New way (with SDK)
    print("\nNEW WAY (SDK):")
    print("""
    from balatro import BalatroSession, Deck, Stake
    
    with BalatroSession() as session:
        session.start(Deck.RED, Stake.WHITE)
        session.select_blind()
        session.play_cards([0, 1, 2])
        session.cash_out()
    """)
    
    print("\nBENEFITS:")
    print("✓ Type safety (Enums instead of strings)")
    print("✓ Error handling built-in (auto-retry, specific exceptions)")
    print("✓ State validation (can't play cards in wrong phase)")
    print("✓ Context manager support (automatic cleanup)")
    print("✓ Logging and debugging")
    print("✓ Reusable strategies")
    print()


if __name__ == "__main__":
    print("Balatro SDK Examples\n")
    print("=" * 50)
    print()
    
    # Show comparison
    compare_apis()
    
    print("=" * 50)
    print()
    
    # Run examples
    try:
        # Try session-based gameplay
        simple_game_loop()
    except Exception as e:
        print(f"Session example failed: {e}\n")
    
    try:
        # Try strategy-based gameplay
        strategy_based_game()
    except Exception as e:
        print(f"Strategy example failed: {e}\n")
    
    try:
        # Try API-level example
        api_level_example()
    except Exception as e:
        print(f"API example failed: {e}\n")

# %%

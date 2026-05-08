#!/usr/bin/env python
"""
Quick validation script for the Balatro SDK.
Tests imports and basic instantiation without requiring a running API server.
"""

import sys
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all SDK modules can be imported."""
    print("Testing SDK imports...")
    
    try:
        from balatro.types import (
            Deck, Stake, Suit, Rank, Seal, Enhancement, Edition,
            GameState, Card, Hand, Shop
        )
        print("  ✓ types module imported")
    except Exception as e:
        print(f"  ✗ types import failed: {e}")
        return False
    
    try:
        from balatro.client import BalatroClient, BalatroAPIError
        print("  ✓ client module imported")
    except Exception as e:
        print(f"  ✗ client import failed: {e}")
        return False
    
    try:
        from balatro.api import BalatroAPI
        print("  ✓ api module imported")
    except Exception as e:
        print(f"  ✗ api import failed: {e}")
        return False
    
    try:
        from balatro.session import BalatroSession
        print("  ✓ session module imported")
    except Exception as e:
        print(f"  ✗ session import failed: {e}")
        return False
    
    try:
        from balatro.strategies import (
            Strategy, GreedyStrategy, RandomStrategy, 
            PlayCardsStrategy, run_game_with_strategy
        )
        print("  ✓ strategies module imported")
    except Exception as e:
        print(f"  ✗ strategies import failed: {e}")
        return False
    
    return True


def test_enums():
    """Test that enums work correctly."""
    print("\nTesting SDK enums...")
    
    from balatro.types import Deck, Stake, Suit, Rank
    
    try:
        assert Deck.RED.value == "RED"
        assert Stake.WHITE.value == "WHITE"
        assert Suit.HEARTS.value == "H"
        assert Rank.ACE.value == "A"
        print("  ✓ All enums have correct values")
        return True
    except Exception as e:
        print(f"  ✗ Enum test failed: {e}")
        return False


def test_client_instantiation():
    """Test that client can be instantiated."""
    print("\nTesting BalatroClient instantiation...")
    
    try:
        from balatro.client import BalatroClient
        client = BalatroClient()
        assert client.base_url == "http://127.0.0.1:12346"
        assert client.timeout == 10.0
        print("  ✓ BalatroClient instantiated successfully")
        client.close()
        return True
    except Exception as e:
        print(f"  ✗ Client instantiation failed: {e}")
        return False


def test_api_instantiation():
    """Test that API wrapper can be instantiated."""
    print("\nTesting BalatroAPI instantiation...")
    
    try:
        from balatro.api import BalatroAPI
        api = BalatroAPI()
        assert api.client is not None
        print("  ✓ BalatroAPI instantiated successfully")
        api.client.close()
        return True
    except Exception as e:
        print(f"  ✗ API instantiation failed: {e}")
        return False


def test_strategy_instantiation():
    """Test that strategies can be instantiated."""
    print("\nTesting Strategy classes...")
    
    try:
        from balatro.strategies import GreedyStrategy, PlayCardsStrategy
        
        greedy = GreedyStrategy()
        assert greedy is not None
        print("  ✓ GreedyStrategy instantiated")
        
        play_cards = PlayCardsStrategy(num_cards=5)
        assert play_cards.num_cards == 5
        print("  ✓ PlayCardsStrategy instantiated")
        
        return True
    except Exception as e:
        print(f"  ✗ Strategy instantiation failed: {e}")
        return False


def test_session_instantiation():
    """Test that session can be instantiated."""
    print("\nTesting BalatroSession...")
    
    try:
        from balatro.session import BalatroSession
        session = BalatroSession()
        assert session.state is None
        print("  ✓ BalatroSession instantiated successfully")
        session.close()
        return True
    except Exception as e:
        print(f"  ✗ Session instantiation failed: {e}")
        return False


def test_helpers():
    """Test helper functions."""
    print("\nTesting helper functions...")
    
    try:
        from balatro.types import card_key_from_suit_rank, parse_card_key, Suit, Rank
        
        # Test card key generation
        key = card_key_from_suit_rank(Suit.HEARTS, Rank.ACE)
        assert key == "H_A"
        print("  ✓ card_key_from_suit_rank works")
        
        # Test card key parsing
        card_type, card_name = parse_card_key("j_joker")
        assert card_type == "joker" and card_name == "joker"
        print("  ✓ parse_card_key works")
        
        return True
    except Exception as e:
        print(f"  ✗ Helper function test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Balatro SDK Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_enums,
        test_client_instantiation,
        test_api_instantiation,
        test_strategy_instantiation,
        test_session_instantiation,
        test_helpers,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("✓ All validation tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

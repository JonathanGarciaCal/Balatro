"""
Unit tests for the Balatro SDK client and API wrapper.

Tests request/response handling, error handling, retries, and basic API methods.
Uses mocked HTTP responses to avoid requiring a running API server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from balatro.client import (
    BalatroClient,
    BalatroAPIError,
    BalatroInternalError,
    BalatroBadRequest,
    BalatroInvalidState,
    BalatroNotAllowed,
)
from balatro.api import BalatroAPI
from balatro.types import Deck, Stake, GameState


class TestBalatroClient:
    """Test BalatroClient request/response handling and error management."""
    
    def test_client_initialization(self):
        """Test client initializes with correct defaults."""
        client = BalatroClient()
        assert client.base_url == "http://127.0.0.1:12346"
        assert client.timeout == 10.0
        assert client.max_retries == 3
    
    def test_client_custom_url(self):
        """Test client accepts custom URL."""
        client = BalatroClient(base_url="http://example.com:5000")
        assert client.base_url == "http://example.com:5000"
    
    def test_build_request_payload(self):
        """Test JSON-RPC request payload format."""
        client = BalatroClient()
        payload = client._build_request("start", {"deck": "RED", "stake": "WHITE"})
        
        assert payload["jsonrpc"] == "2.0"
        assert payload["method"] == "start"
        assert payload["params"] == {"deck": "RED", "stake": "WHITE"}
        assert isinstance(payload["id"], int)
        assert payload["id"] > 0
    
    def test_request_id_increment(self):
        """Test request IDs increment sequentially."""
        client = BalatroClient()
        id1 = client._build_request("test")["id"]
        id2 = client._build_request("test")["id"]
        id3 = client._build_request("test")["id"]
        
        assert id2 == id1 + 1
        assert id3 == id2 + 1
    
    @patch("balatro.client.requests.Session.post")
    def test_successful_call(self, mock_post):
        """Test successful RPC call."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"seed": "12345"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient()
        result = client.call("start", {"deck": "RED", "stake": "WHITE"})
        
        assert result == {"seed": "12345"}
        mock_post.assert_called_once()
    
    @patch("balatro.client.requests.Session.post")
    def test_error_bad_request(self, mock_post):
        """Test BAD_REQUEST error is converted to exception."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32001, "message": "Invalid parameters"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient()
        with pytest.raises(BalatroBadRequest):
            client.call("play", {"cards": "invalid"})
    
    @patch("balatro.client.requests.Session.post")
    def test_error_invalid_state(self, mock_post):
        """Test INVALID_STATE error is converted to exception."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32002, "message": "Cannot play cards now"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient()
        with pytest.raises(BalatroInvalidState):
            client.call("play", {"cards": [0, 1]})
    
    @patch("balatro.client.requests.Session.post")
    def test_error_not_allowed(self, mock_post):
        """Test NOT_ALLOWED error is converted to exception."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32003, "message": "Not enough money"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient()
        with pytest.raises(BalatroNotAllowed):
            client.call("buy", {"card": 0})
    
    @patch("balatro.client.requests.Session.post")
    @patch("time.sleep")
    def test_retry_on_internal_error(self, mock_sleep, mock_post):
        """Test client retries on INTERNAL_ERROR."""
        # First call fails, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Internal error"},
            "id": 1,
        }
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"status": "ok"},
            "id": 2,
        }
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        client = BalatroClient(max_retries=3, retry_backoff=0.1)
        result = client.call("gamestate", auto_retry=True)
        
        assert result == {"status": "ok"}
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch("balatro.client.requests.Session.post")
    @patch("time.sleep")
    def test_max_retries_exhausted(self, mock_sleep, mock_post):
        """Test exception raised when max retries exhausted."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Internal error"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient(max_retries=2, retry_backoff=0.1)
        with pytest.raises(BalatroInternalError):
            client.call("gamestate", auto_retry=True)
        
        # Should try 3 times (initial + 2 retries)
        assert mock_post.call_count == 3
    
    @patch("balatro.client.requests.Session.post")
    def test_disable_auto_retry(self, mock_post):
        """Test auto_retry=False prevents retries."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Internal error"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient(max_retries=3)
        with pytest.raises(BalatroInternalError):
            client.call("gamestate", auto_retry=False)
        
        # Should only try once
        assert mock_post.call_count == 1
    
    @patch("balatro.client.requests.Session.post")
    def test_health_check(self, mock_post):
        """Test health check method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"status": "ok"},
            "id": 1,
        }
        mock_post.return_value = mock_response
        
        client = BalatroClient()
        assert client.is_alive() is True
    
    @patch("balatro.client.requests.Session.post")
    def test_health_check_failure(self, mock_post):
        """Test health check returns False on failure."""
        mock_post.side_effect = Exception("Connection refused")
        
        client = BalatroClient()
        assert client.is_alive() is False
    
    def test_context_manager(self):
        """Test client works as context manager."""
        with BalatroClient() as client:
            assert client is not None
            assert isinstance(client, BalatroClient)


class TestBalatroAPI:
    """Test BalatroAPI high-level method wrappers."""
    
    @patch.object(BalatroClient, "call")
    def test_api_initialization(self, mock_call):
        """Test API can be initialized with or without client."""
        api1 = BalatroAPI()
        assert isinstance(api1.client, BalatroClient)
        
        custom_client = BalatroClient(base_url="http://custom:1234")
        api2 = BalatroAPI(custom_client)
        assert api2.client is custom_client
    
    @patch.object(BalatroClient, "call")
    def test_start_game(self, mock_call):
        """Test start method."""
        mock_call.return_value = {"seed": "12345", "state": "BLIND_SELECT"}
        
        api = BalatroAPI()
        result = api.start(Deck.RED, Stake.WHITE)
        
        assert result == {"seed": "12345", "state": "BLIND_SELECT"}
        mock_call.assert_called_once_with("start", {"deck": "RED", "stake": "WHITE"})
    
    @patch.object(BalatroClient, "call")
    def test_start_with_seed(self, mock_call):
        """Test start method with seed."""
        mock_call.return_value = {"seed": "custom_seed", "state": "BLIND_SELECT"}
        
        api = BalatroAPI()
        result = api.start("RED", "WHITE", seed="custom_seed")
        
        mock_call.assert_called_once_with(
            "start",
            {"deck": "RED", "stake": "WHITE", "seed": "custom_seed"},
        )
    
    @patch.object(BalatroClient, "call")
    def test_select_blind(self, mock_call):
        """Test select method."""
        mock_call.return_value = {"state": "SELECTING_HAND"}
        
        api = BalatroAPI()
        result = api.select()
        
        assert result["state"] == "SELECTING_HAND"
        mock_call.assert_called_once_with("select")
    
    @patch.object(BalatroClient, "call")
    def test_play_cards(self, mock_call):
        """Test play method."""
        mock_call.return_value = {"state": "ROUND_EVAL"}
        
        api = BalatroAPI()
        result = api.play([0, 1, 2])
        
        assert result["state"] == "ROUND_EVAL"
        mock_call.assert_called_once_with("play", {"cards": [0, 1, 2]})
    
    @patch.object(BalatroClient, "call")
    def test_buy_card(self, mock_call):
        """Test buy method with card."""
        mock_call.return_value = {"money": 4}
        
        api = BalatroAPI()
        result = api.buy(card=0)
        
        mock_call.assert_called_once_with("buy", {"card": 0})
    
    @patch.object(BalatroClient, "call")
    def test_buy_invalid_params(self, mock_call):
        """Test buy method raises error with invalid params."""
        api = BalatroAPI()
        
        # No params
        with pytest.raises(ValueError):
            api.buy()
        
        # Multiple params
        with pytest.raises(ValueError):
            api.buy(card=0, voucher=1)
    
    @patch.object(BalatroClient, "call")
    def test_add_card(self, mock_call):
        """Test add card method."""
        mock_call.return_value = {"jokers": []}
        
        api = BalatroAPI()
        result = api.add("j_joker", eternal=True)
        
        mock_call.assert_called_once_with(
            "add",
            {"key": "j_joker", "eternal": True},
        )
    
    @patch.object(BalatroClient, "call")
    def test_gamestate(self, mock_call):
        """Test gamestate method."""
        mock_gamestate = {"state": "BLIND_SELECT", "seed": "123"}
        mock_call.return_value = mock_gamestate
        
        api = BalatroAPI()
        result = api.gamestate()
        
        assert result == mock_gamestate
        mock_call.assert_called_once_with("gamestate")
    
    @patch.object(BalatroClient, "call")
    def test_discover(self, mock_call):
        """Test discover method."""
        mock_spec = {"openrpc": "1.3.2", "methods": []}
        mock_call.return_value = mock_spec
        
        api = BalatroAPI()
        result = api.discover()
        
        assert result == mock_spec
        mock_call.assert_called_once_with("rpc.discover")

    @patch.object(BalatroClient, "call")
    def test_playable_cards_returns_visible_indices(self, mock_call):
        """Test playable_cards returns visible hand card indices in SELECTING_HAND."""
        mock_call.return_value = {
            "state": "SELECTING_HAND",
            "hand": {
                "cards": [
                    {"key": "H_A", "state": {"hidden": False, "debuff": False}},
                    {"key": "H_K", "state": {"hidden": True, "debuff": False}},
                    {"key": "H_Q", "state": {"hidden": False, "debuff": True}},
                ]
            },
        }

        api = BalatroAPI()
        result = api.playable_cards()

        assert result == [0, 2]
        mock_call.assert_called_once_with("gamestate")

    @patch.object(BalatroClient, "call")
    def test_playable_cards_excludes_debuffed_when_requested(self, mock_call):
        """Test playable_cards can filter out debuffed cards."""
        mock_call.return_value = {
            "state": "SELECTING_HAND",
            "hand": {
                "cards": [
                    {"key": "H_A", "state": {"hidden": False, "debuff": False}},
                    {"key": "H_Q", "state": {"hidden": False, "debuff": True}},
                ]
            },
        }

        api = BalatroAPI()
        result = api.playable_cards(include_debuffed=False)

        assert result == [0]
        mock_call.assert_called_once_with("gamestate")

    @patch.object(BalatroClient, "call")
    def test_playable_cards_returns_empty_outside_selecting_hand(self, mock_call):
        """Test playable_cards returns empty list when not in SELECTING_HAND."""
        mock_call.return_value = {"state": "SHOP"}

        api = BalatroAPI()
        result = api.playable_cards()

        assert result == []
        mock_call.assert_called_once_with("gamestate")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

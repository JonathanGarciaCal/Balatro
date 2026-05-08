"""
Core BalatroClient for JSON-RPC communication with the Balatro API server.

Handles request/response formatting, error handling, retries, and connection management.
"""

import requests
import time
from typing import Any, Optional
import logging

from .types import GameState, RPCResponse, RPCError, ErrorCode

logger = logging.getLogger(__name__)


class BalatroAPIError(Exception):
    """Base exception for Balatro API errors."""
    pass


class BalatroInternalError(BalatroAPIError):
    """Raised when the API returns an INTERNAL_ERROR (-32000)."""
    pass


class BalatroBadRequest(BalatroAPIError):
    """Raised when the API returns a BAD_REQUEST (-32001)."""
    pass


class BalatroInvalidState(BalatroAPIError):
    """Raised when the API returns an INVALID_STATE (-32002)."""
    pass


class BalatroNotAllowed(BalatroAPIError):
    """Raised when the API returns a NOT_ALLOWED (-32003)."""
    pass


class BalatroClient:
    """
    Python client for the Balatro JSON-RPC API.
    
    Provides low-level request/response handling with automatic retries,
    error handling, and logging. Use this for direct API method calls.
    For higher-level abstractions, see BalatroSession.
    
    Example:
        client = BalatroClient()
        state = client.call("start", {"deck": "RED", "stake": "WHITE"})
        print(f"Game started with seed: {state['seed']}")
    """
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:12346",
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        """
        Initialize the Balatro API client.
        
        Args:
            base_url: URL of the Balatro API server (default: local development)
            timeout: Request timeout in seconds (default: 10)
            max_retries: Max retry attempts on INTERNAL_ERROR (default: 3)
            retry_backoff: Backoff multiplier for retries (default: 1.0)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._request_id = 0
        self._session = requests.Session()
    
    def _next_request_id(self) -> int:
        """Generate the next JSON-RPC request ID."""
        self._request_id += 1
        return self._request_id
    
    def _build_request(self, method: str, params: Optional[dict] = None) -> dict:
        """Build a JSON-RPC 2.0 request payload."""
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._next_request_id(),
        }
    
    def _handle_error(self, error: RPCError) -> None:
        """Convert JSON-RPC error into appropriate Python exception."""
        code = error.get("code", -32603)
        message = error.get("message", "Unknown error")
        data = error.get("data")
        
        error_msg = f"API Error {code}: {message}"
        if data:
            error_msg += f" | {data}"
        
        logger.error(error_msg)
        
        if code == ErrorCode.INTERNAL_ERROR:
            raise BalatroInternalError(error_msg)
        elif code == ErrorCode.BAD_REQUEST:
            raise BalatroBadRequest(error_msg)
        elif code == ErrorCode.INVALID_STATE:
            raise BalatroInvalidState(error_msg)
        elif code == ErrorCode.NOT_ALLOWED:
            raise BalatroNotAllowed(error_msg)
        else:
            raise BalatroAPIError(error_msg)
    
    def call(
        self,
        method: str,
        params: Optional[dict] = None,
        auto_retry: bool = True,
    ) -> Any:
        """
        Call a JSON-RPC method on the Balatro API.
        
        Args:
            method: JSON-RPC method name (e.g., "start", "play", "gamestate")
            params: Method parameters as a dict (default: {})
            auto_retry: Auto-retry on INTERNAL_ERROR with exponential backoff (default: True)
        
        Returns:
            The result field from the JSON-RPC response
        
        Raises:
            BalatroInternalError: If API returns INTERNAL_ERROR (after retries exhausted)
            BalatroBadRequest: If API returns BAD_REQUEST
            BalatroInvalidState: If API returns INVALID_STATE
            BalatroNotAllowed: If API returns NOT_ALLOWED
            BalatroAPIError: For other JSON-RPC errors
            requests.RequestException: For network/connection errors
        """
        attempt = 0
        last_error = None
        
        while attempt <= self.max_retries:
            try:
                payload = self._build_request(method, params)
                
                logger.debug(f"RPC Call: {method} (attempt {attempt + 1}/{self.max_retries + 1})")
                logger.debug(f"Payload: {payload}")
                
                response = self._session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                
                data: RPCResponse = response.json()
                logger.debug(f"Response: {data}")
                
                # Check for JSON-RPC error
                if "error" in data:
                    error = data["error"]
                    
                    # Retry on INTERNAL_ERROR if auto_retry enabled
                    if auto_retry and error.get("code") == ErrorCode.INTERNAL_ERROR:
                        attempt += 1
                        if attempt <= self.max_retries:
                            wait_time = self.retry_backoff ** attempt
                            logger.warning(
                                f"INTERNAL_ERROR, retrying in {wait_time}s "
                                f"({attempt}/{self.max_retries})"
                            )
                            time.sleep(wait_time)
                            continue
                    
                    # Handle error
                    self._handle_error(error)
                
                # Success
                result = data.get("result")
                logger.debug(f"Result: {result}")
                return result
            
            except requests.RequestException as e:
                logger.error(f"Network error: {e}")
                raise
        
        # If we got here, retries exhausted
        if last_error:
            raise last_error
        raise BalatroAPIError("Max retries exhausted")
    
    def is_alive(self) -> bool:
        """Check if the API server is reachable."""
        try:
            result = self.call("health", auto_retry=False)
            return result.get("status") == "ok"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def close(self) -> None:
        """Close the session and clean up resources."""
        self._session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

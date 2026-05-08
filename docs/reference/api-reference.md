# API Reference (concise)

This file summarizes the core JSON-RPC methods agents will use most often. For full, authoritative schemas use `openrpc.json`.

### rpc.discover
- Summary: Returns the OpenRPC schema for this service.
- Params: none
- Result: OpenRPC JSON (machine-readable spec)
- Errors: none

### health
- Summary: Health check endpoint
- Params: none
- Result: `{ "status": "ok" }`
- Errors: none

### gamestate
- Summary: Get complete current game state
- Params: none
- Result: `GameState` object (see `openrpc.json`)
- Errors: none

### start
- Summary: Start a new game run
- Params:
  - `deck` (string, required) — one of Deck values (e.g., `RED`)
  - `stake` (string, required) — one of Stake values (e.g., `WHITE`)
  - `seed` (string, optional)
- Result: `GameState` (state will be `BLIND_SELECT`)
- Errors: `BAD_REQUEST`, `INVALID_STATE`, `INTERNAL_ERROR`

### select
- Summary: Select the current blind to begin the round
- Params: none
- Result: `GameState` (state will be `SELECTING_HAND`)
- Errors: `INVALID_STATE`

### play
- Summary: Play cards from the hand
- Params:
  - `cards` (array of integers, required) — 0-based indices of hand cards
- Result: `GameState`
- Errors: `BAD_REQUEST`

### buy
- Summary: Buy a shop item; provide exactly one: `card`, `voucher`, or `pack` (0-based index)
- Params: `card` | `voucher` | `pack` (integer, one required)
- Result: `GameState`
- Errors: `BAD_REQUEST`, `NOT_ALLOWED`

### cash_out, next_round, save, load, screenshot, add, set, discard, rearrange, reroll, sell, use, skip
- Summary: See `openrpc.json` for parameter schemas and full descriptions. These return `GameState` for most game-modifying calls or `PathResult` for file operations.

Errors (common)
- `INTERNAL_ERROR` (-32000)
- `BAD_REQUEST` (-32001)
- `INVALID_STATE` (-32002)
- `NOT_ALLOWED` (-32003)

Notes
- Card/area indices in API params are 0-based.
- Use `rpc.discover` to validate required params and types programmatically before sending requests.

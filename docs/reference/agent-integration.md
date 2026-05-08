# Agent Integration Guide

Purpose: give an AI agent the minimal, precise instructions and patterns for safely and effectively calling the BalatroBot API.

1) System prompt template (recommended)

You may provide this to an LLM acting as the agent's system message:

"You are an autonomous agent that can call a JSON-RPC API at http://127.0.0.1:12346 to control a Balatro game. Use `rpc.discover` at startup to fetch the API schema. Always validate parameters against the schema before calling. When uncertain about game state, call `gamestate`. Use 0-based indices for lists. Use integer or string `id` values (no floats). After each call, inspect `result` and update your internal plan. Avoid destructive actions unless the policy permits."

2) Minimal agent loop (pseudocode)

- On start: `spec = rpc('rpc.discover')`
- `state = rpc('gamestate')`
- While not state['state']=='GAME_OVER':
  - Decide action based on `state`.
  - Validate params against `spec` for chosen method.
  - Call the method and receive `result`.
  - If `error`, handle by fallback (e.g., re-fetch `gamestate` or choose different action).
  - Update `state = result` (if method returns `GameState`) or `state = rpc('gamestate')`.

3) Constructing JSON-RPC calls

- Format: `{"jsonrpc":"2.0","method":"NAME","params":{...},"id":<int|string>}`
- Use small `id` values and increment them for tracing.
- For array params, ensure they are numeric 0-based indices.
- For mutually exclusive parameters (e.g., `buy` expects exactly one of `card|voucher|pack`), pass only the chosen field.

4) Error handling strategy

- If `BAD_REQUEST`: check parameter types and schema, then retry once with corrected parameters.
- If `INVALID_STATE` or `NOT_ALLOWED`: re-query `gamestate` to resolve allowed actions.
- If `INTERNAL_ERROR`: back off and retry after a short delay; escalate if persistent.

5) Safety and policies

- Unless explicitly allowed, avoid `add` (inserts new cards) and `set` (mutates debug fields) in production.
- Use `save` before any batch of destructive operations if you may want to revert later.

6) Quick validation helper (Python)

```python
# minimal validate-and-call helper
import requests
URL = 'http://127.0.0.1:12346'

def rpc(method, params=None, req_id=1):
  payload = {"jsonrpc":"2.0","method":method,"params":params or {},"id":req_id}
  r = requests.post(URL, json=payload, timeout=10)
  r.raise_for_status()
  data = r.json()
  if 'error' in data:
    raise RuntimeError(data['error'])
  return data.get('result')
```

7) Quick decision heuristics

- If `state` is `BLIND_SELECT`: call `select`.
- If `state` is `SELECTING_HAND`: try `play` with a greedy selection (play as many cards as allowed) or use heuristics derived from hand structure.
- If `state` is `ROUND_EVAL`: call `cash_out`.
- If `state` is `SHOP`: prefer `buy`/`pack`/`next_round` according to available money and strategy.

8) Where to find schemas and implementation

- Machine-readable spec (bundled here): `openrpc.json`.
- Server & dispatcher mapping: see `docs/specifications/balatrobot_docs/src_snapshot/dispatcher.lua` and `server.lua` for how requests are validated and dispatched.

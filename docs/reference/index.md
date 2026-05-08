# AI Agent Reference — BalatroBot API

This folder contains a concise, machine- and AI-agent-friendly reference for interacting with the BalatroBot JSON-RPC API.

Included files

- `api-reference.md` — Core methods, parameters, results and errors (concise).
- `agent-integration.md` — Recommended agent workflow, system prompt templates, and best practices.
- `examples.md` — Copy of curl and Python examples useful for automation and testing.
- `openrpc.json` — Copy of the authoritative OpenRPC specification (machine readable).

Quick facts

- Base URL: `http://127.0.0.1:12346`
- Protocol: JSON-RPC 2.0 over HTTP POST to `/`
- Discovery: call `rpc.discover` to fetch the authoritative machine-readable API spec.
- Request format: `{"jsonrpc":"2.0","method":"...","params":{...},"id":1}`
- IDs: use integer or string IDs (floats are rejected).
- Indexing: card and shop indices in method parameters are 0-based.

Recommended agent workflow

1. Call `rpc.discover` once at startup to fetch `openrpc.json` and validate method names and schemas.
2. Use `gamestate` as the canonical source of truth before planning an action.
3. Decide the desired API call, validate parameters against the OpenRPC schema, then send a single well-formed JSON-RPC request.
4. Inspect `result` or `error` and update internal agent state; repeat.

For full machine-readable details, see the bundled `openrpc.json` in this folder.

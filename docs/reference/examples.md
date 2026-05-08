# Examples — curl & Python

## Curl examples

Health:

```bash
curl -X POST http://127.0.0.1:12346 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"health","id":1}'
```

Get game state:

```bash
curl -X POST http://127.0.0.1:12346 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"gamestate","id":1}'
```

Start a run:

```bash
curl -X POST http://127.0.0.1:12346 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"start","params":{"deck":"RED","stake":"WHITE"},"id":1}'
```

Play a round (select -> play):

```bash
curl -X POST http://127.0.0.1:12346 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"select","id":1}'
curl -X POST http://127.0.0.1:12346 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"play","params":{"cards":[0,1,2]},"id":2}'
```

## Python example (minimal bot)

```python
import requests

URL = "http://127.0.0.1:12346"

def rpc(method: str, params: dict = None, req_id: int = 1):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": req_id}
    r = requests.post(URL, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data.get("result")


def quick_play():
    rpc("menu")
    state = rpc("start", {"deck": "RED", "stake": "WHITE"})
    while state.get("state") != "GAME_OVER":
        s = state.get("state")
        if s == "BLIND_SELECT":
            state = rpc("select")
        elif s == "SELECTING_HAND":
            num = min(5, len(state.get("hand", {}).get("cards", [])))
            state = rpc("play", {"cards": list(range(num))})
        elif s == "ROUND_EVAL":
            state = rpc("cash_out")
        elif s == "SHOP":
            state = rpc("next_round")
        else:
            state = rpc("gamestate")
    return state.get("won", False)

if __name__ == '__main__':
    print(quick_play())
```

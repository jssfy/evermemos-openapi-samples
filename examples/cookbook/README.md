# Cookbook Examples (v1)

SDK v1 versions of [Your First Memory in 5 Minutes](https://docs.evermind.ai/cookbook/quickstart).

## Prerequisites

```bash
pip install everos -U
export EVEROS_API_KEY="your_api_key"
```

## Examples

| File | Corresponds to |
|------|---------------|
| `quickstart_sdk_sync.py` | Steps 1-3 (Store → Flush → Search), sync SDK |
| `quickstart_sdk_async.py` | Steps 1-3, async SDK |
| `quickstart_sdk_complete.py` | "Complete Working Script" section (user_bob) |
| `quickstart_api.py` | Raw HTTP requests (no SDK) |

## Run

```bash
python quickstart_sdk_sync.py
python quickstart_sdk_async.py
python quickstart_sdk_complete.py
```

## v0 Cookbook

See [`../v0/cookbook/`](../v0/cookbook/) for the v0 SDK equivalents.

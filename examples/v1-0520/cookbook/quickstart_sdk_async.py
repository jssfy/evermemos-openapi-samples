# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration from old v1:
#   - AsyncEverOS().v1.memories → AsyncEverOS().v1.memory
#   - memories.group.add() → memory.add(owner_id=..., owner_type=..., session_id=...)
import asyncio
import time
from everos import AsyncEverOS

client = AsyncEverOS()
memory = client.v1.memory

now_ms = int(time.time() * 1000)


async def main() -> None:
    # ── Step 1: Store a Conversation ─────────────────────────────────────────
    await memory.add(
        owner_id="user_alice",
        owner_type="user",
        session_id="demo_async_001",
        messages=[
            {
                "role": "user",
                "name": "Alice",
                "timestamp": now_ms,
                "content": "I prefer working in the morning, usually from 6am to 10am.",
            }
        ],
    )

    await memory.add(
        owner_id="user_alice",
        owner_type="user",
        session_id="demo_async_001",
        messages=[
            {
                "role": "user",
                "name": "Alice",
                "timestamp": now_ms + 5000,
                "content": "Let's switch topics - what's the weather like today?",
            }
        ],
    )

    # ── Step 2: Wait for Indexing ─────────────────────────────────────────────
    print("Waiting for memory extraction...")
    await asyncio.sleep(5)

    # ── Step 3: Search ────────────────────────────────────────────────────────
    response = await memory.search(
        owner_id="user_alice",
        owner_type="user",
        query="when does alice prefer to work",
        method="hybrid",
        include_profile=True,
        top_k=5,
    )

    data = response.data
    episodes = data.episodes if data else []
    print(f"Found {len(episodes)} relevant memories:\n")
    for ep in episodes:
        print(f"Content: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
        print(f"Score: {getattr(ep, 'score', 'N/A')}")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())

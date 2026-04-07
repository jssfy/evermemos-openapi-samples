# everos should've been installed (pip install everos -U)
# Async SDK version of https://docs.evermind.ai/cookbook/quickstart (Steps 1-3)
# Migration notes from v0:
#   - Group conversations → client.v1.memories.group.add()
#   - response.result.memories → response.data.episodes
import asyncio
import time
from everos import AsyncEverOS

client = AsyncEverOS()
group_mem = client.v1.memories.group

now_ms = int(time.time() * 1000)


async def main() -> None:
    # ── Step 1: Store a Conversation ──────────────────────────────────────────

    response = await group_mem.add(
        group_id="demo_conversation_001",
        group_meta={"name": "Demo Conversation"},
        messages=[
            {
                "role": "user",
                "sender_id": "user_alice",
                "sender_name": "Alice",
                "timestamp": now_ms,
                "content": "I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive.",
            }
        ],
    )

    print(f"Status: {response.data.status if response.data else 'unknown'}")

    # ── Step 2: Wait for Indexing ─────────────────────────────────────────────

    await group_mem.add(
        group_id="demo_conversation_001",
        group_meta={"name": "Demo Conversation"},
        messages=[
            {
                "role": "user",
                "sender_id": "user_alice",
                "sender_name": "Alice",
                "timestamp": now_ms + 5000,
                "content": "Let's switch topics - what's the weather like today?",
            }
        ],
    )

    print("Waiting for memory extraction...")
    await asyncio.sleep(5)

    # ── Step 3: Search Your Memory ────────────────────────────────────────────

    response = await client.v1.memories.search(
        filters={"user_id": "user_alice"},
        query="when does alice prefer to work",
        method="hybrid",
        top_k=5,
        memory_types=["episodic_memory", "profile"],
    )

    data = response.data
    episodes = data.episodes if data else []

    print(f"Found {len(episodes)} relevant memories:\n")
    for ep in episodes:
        print(f"Type: {getattr(ep, 'memory_type', 'N/A')}")
        print(f"Content: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
        print(f"Score: {getattr(ep, 'score', 'N/A')}")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())

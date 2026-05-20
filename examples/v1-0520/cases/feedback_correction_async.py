#!/usr/bin/env python3
# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# NEW in 0.0.1: Full feedback workflow — add memory → get memory_id → submit feedback
import asyncio
import time
from everos import AsyncEverOS
from pprint import pprint

client = AsyncEverOS()
memory = client.v1.memory


async def main() -> None:
    now_ms = int(time.time() * 1000)

    # 1. Add a memory with potentially inaccurate content
    print("1. Storing memory...")
    add_resp = await memory.add(
        owner_id="user_feedback_demo",
        owner_type="user",
        session_id="session_feedback_001",
        messages=[
            {
                "role": "user",
                "timestamp": now_ms,
                "content": "I drink coffee every morning before work.",
            }
        ],
    )
    print(f"Add status: {add_resp.data.status if add_resp.data else None}")

    print("\nWaiting for memory extraction...")
    await asyncio.sleep(8)

    # 2. Get the stored memory to find its ID
    print("\n2. Retrieving stored memories...")
    get_resp = await memory.get(
        owner_id="user_feedback_demo",
        owner_type="user",
        memory_type="episodic_memory",
        page_size=5,
    )
    pprint(get_resp)

    episodes = get_resp.data.episodes if get_resp.data else []
    if not episodes:
        print("No episodes found yet. Try again after a few more seconds.")
        return

    # 3. Submit feedback to correct the first memory
    target = episodes[0]
    memory_id = target.id
    print(f"\n3. Submitting feedback for memory_id={memory_id}")
    print(f"   Original: {target.episode or target.summary}")

    fb_resp = await memory.feedback(
        memory_id=memory_id,
        memory_type="episodic_memory",
        content="Correction: the user actually drinks tea in the morning, not coffee.",
        owner_id="user_feedback_demo",
        owner_type="user",
    )
    pprint(fb_resp)
    print(f"\nFeedback applied: record_id={fb_resp.data.record_id if fb_resp.data else None}, "
          f"version={fb_resp.data.version if fb_resp.data else None}")

    # 4. Search to verify correction is reflected
    print("\n4. Searching to verify correction...")
    await asyncio.sleep(3)
    search_resp = await memory.search(
        owner_id="user_feedback_demo",
        owner_type="user",
        query="morning drink preference",
        method="hybrid",
        top_k=3,
    )
    pprint(search_resp)


if __name__ == "__main__":
    asyncio.run(main())

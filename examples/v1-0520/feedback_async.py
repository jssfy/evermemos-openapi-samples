# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# NEW in 0.0.1: memory.feedback() — correct or annotate an existing memory
#   memory_type: "profile" | "episodic_memory"
#   content: the corrected or additional information
#   memory_id: ID of the memory to update
import asyncio
import os
from everos import AsyncEverOS
from pprint import pprint

memory = AsyncEverOS().v1.memory

# Set via env var or replace directly:
MEMORY_ID = os.environ.get("EVEROS_MEMORY_ID", "your-memory-id-here")


async def main() -> None:
    # Example 1: Correct an episodic memory
    # NOTE: owner_id must match the actual owner of the memory (set EVEROS_OWNER_ID accordingly)
    owner_id = os.environ.get("EVEROS_OWNER_ID", "user_feedback_test")
    print("=== feedback on episodic_memory ===")
    response = await memory.feedback(
        memory_id=MEMORY_ID,
        memory_type="episodic_memory",
        content="Correction: the user drinks black tea every morning, not green tea.",
        owner_id=owner_id,
        owner_type="user",
    )
    pprint(response)
    print(f"record_id: {response.data.record_id if response.data else None}")
    print(f"version: {response.data.version if response.data else None}")


if __name__ == "__main__":
    asyncio.run(main())

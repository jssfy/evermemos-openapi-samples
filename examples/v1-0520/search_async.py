# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - memories.search(filters={"user_id": ...}, query=...)
#     → memory.search(owner_id=..., owner_type=..., query=...)
#   - method options: "keyword" | "vector" | "hybrid" | "agentic"
#   - include_profile=True to include profile results in search
import asyncio
from everos import AsyncEverOS
from pprint import pprint

memory = AsyncEverOS().v1.memory


async def main() -> None:
    # Search 1: hybrid search with profile included
    print("=== hybrid search with profile ===")
    response = await memory.search(
        owner_id="user_001",
        owner_type="user",
        query="outdoor activities",
        method="hybrid",
        include_profile=True,
        top_k=5,
    )
    pprint(response)

    # Search 2: vector search only (episodic memories)
    print("\n=== vector search ===")
    response = await memory.search(
        owner_id="user_001",
        owner_type="user",
        query="sports preferences",
        method="vector",
        top_k=3,
    )
    pprint(response)

    # Search 3: keyword search
    print("\n=== keyword search ===")
    response = await memory.search(
        owner_id="user_001",
        owner_type="user",
        query="basketball",
        method="keyword",
        top_k=5,
    )
    pprint(response)

    # Search 4: agentic search (NEW in 0.0.1 — AI-driven search strategy)
    print("\n=== agentic search ===")
    response = await memory.search(
        owner_id="user_001",
        owner_type="user",
        query="what does this user like to do for fun?",
        method="agentic",
        top_k=5,
    )
    pprint(response)

    # Search 5: agent-type memory search
    print("\n=== agent memory search ===")
    response = await memory.search(
        owner_id="agent_001",
        owner_type="agent",
        query="data analysis tasks",
        method="hybrid",
        top_k=3,
    )
    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())

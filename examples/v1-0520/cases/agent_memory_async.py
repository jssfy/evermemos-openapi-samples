#!/usr/bin/env python3
# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# NEW in 0.0.1: Agent-type memory (owner_type="agent")
#   Demonstrates storing tool-call conversations and retrieving agent_case / agent_skill memories.
import asyncio
import time
from everos import AsyncEverOS
from pprint import pprint

client = AsyncEverOS()
memory = client.v1.memory


async def main() -> None:
    now_ms = int(time.time() * 1000)

    # 1. Store an agent conversation (with tool calls)
    print("1. Storing agent conversation with tool calls...")
    response = await memory.add(
        owner_id="agent_code_assistant",
        owner_type="agent",
        session_id="session_agent_001",
        agent_id="agent_code_assistant",
        messages=[
            {
                "role": "user",
                "timestamp": now_ms,
                "content": "Please analyze the data in sales.csv and generate a summary report.",
            },
            {
                "role": "assistant",
                "timestamp": now_ms + 1000,
                "tool_calls": [
                    {
                        "id": "call_001",
                        "type": "function",
                        "function": {
                            "name": "read_file",
                            "arguments": '{"path": "sales.csv"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "timestamp": now_ms + 2000,
                "tool_call_id": "call_001",
                "content": "date,product,revenue\n2025-01,Widget A,50000\n2025-02,Widget A,62000",
            },
            {
                "role": "assistant",
                "timestamp": now_ms + 3000,
                "content": "Analysis complete. Total revenue Q1: $112,000. Widget A shows 24% growth.",
            },
        ],
    )
    print(f"Add status: {response.data.status if response.data else None}")

    print("\nWaiting for memory extraction...")
    await asyncio.sleep(8)

    # 2. Retrieve agent_case memories
    print("\n2. Get agent_case memories...")
    response = await memory.get(
        owner_id="agent_code_assistant",
        owner_type="agent",
        memory_type="agent_case",
        page_size=5,
    )
    pprint(response)
    if response.data and response.data.agent_cases:
        for case in response.data.agent_cases:
            print(f"\ntask_intent: {case.task_intent}")
            print(f"approach: {case.approach}")
            print(f"key_insight: {case.key_insight}")
            print(f"quality_score: {case.quality_score}")

    # 3. Retrieve agent_skill memories
    print("\n3. Get agent_skill memories...")
    response = await memory.get(
        owner_id="agent_code_assistant",
        owner_type="agent",
        memory_type="agent_skill",
        page_size=5,
    )
    pprint(response)

    # 4. Search agent memories
    print("\n4. Search agent memories for 'data analysis'...")
    response = await memory.search(
        owner_id="agent_code_assistant",
        owner_type="agent",
        query="data analysis and reporting",
        method="hybrid",
        top_k=3,
    )
    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())

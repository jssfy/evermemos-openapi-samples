# Install the everos python sdk:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Agent version: owner_type="agent"
#   - agent_id identifies the agent (optional but recommended)
#   - Messages can include tool_calls / tool role for capturing reasoning traces
#   - Extracted memories will be stored as episodic_memory and may generate agent_case / agent_skill

from everos import EverOS

memory = EverOS().v1.memory  # reads EVEROS_API_KEY + EVER_OS_BASE_URL from env

response = memory.add(
    owner_id="agent_demo_001",
    owner_type="agent",
    agent_id="agent_demo_001",
    session_id="session_agent_getting_started",
    messages=[
        {
            "role": "user",
            "timestamp": 1736935200000,  # 2025-01-15T10:00:00Z
            "content": "Analyze sales.csv and generate a monthly revenue summary.",
        },
        {
            "role": "assistant",
            "timestamp": 1736935210000,
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
            "timestamp": 1736935220000,
            "tool_call_id": "call_001",
            "content": "date,product,revenue\n2025-01,Widget A,50000\n2025-02,Widget A,62000",
        },
        {
            "role": "assistant",
            "timestamp": 1736935230000,
            "content": "Analysis complete. Widget A: Jan $50k, Feb $62k. Total Q1 so far: $112k (+24% MoM).",
        },
    ],
)
print(f"Status: {response.data.status}, Message count: {response.data.message_count}")

# Install the everos python sdk:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Agent version: query agent-specific memory types
#   - episodic_memory: raw conversation episodes (same as user)
#   - agent_case:  successful task patterns distilled from episodes
#   - agent_skill: reusable capabilities extracted across cases

from everos import EverOS

memory = EverOS().v1.memory  # reads EVEROS_API_KEY + EVER_OS_BASE_URL from env

# Fetch episodic memories (conversation traces)
print("=== episodic_memory ===")
response = memory.get(
    owner_id="agent_demo_001",
    owner_type="agent",
    memory_type="episodic_memory",
    page_size=5,
    sort_by="timestamp",
    sort_order="desc",
)
episodes = response.data.episodes if response.data else []
print(f"Fetched {len(episodes) if episodes else 0} episodes")

# Fetch agent cases (task patterns)
print("\n=== agent_case ===")
response = memory.get(
    owner_id="agent_demo_001",
    owner_type="agent",
    memory_type="agent_case",
    page_size=5,
)
cases = response.data.agent_cases if response.data else []
print(f"Fetched {len(cases) if cases else 0} agent cases")
if cases:
    for c in cases:
        print(f"  task_intent: {c.task_intent}")
        print(f"  approach: {c.approach}")

# Fetch agent skills
print("\n=== agent_skill ===")
response = memory.get(
    owner_id="agent_demo_001",
    owner_type="agent",
    memory_type="agent_skill",
    page_size=5,
)
skills = response.data.agent_skills if response.data else []
print(f"Fetched {len(skills) if skills else 0} agent skills")
if skills:
    for s in skills:
        print(f"  name: {s.name}  confidence: {s.confidence}")

# Install the everos python sdk:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Agent version: semantic search over agent memories
#   - Returns episodic_memory, agent_case, agent_skill matching the query
#   - "agentic" method lets the server choose the best retrieval strategy

from everos import EverOS

memory = EverOS().v1.memory  # reads EVEROS_API_KEY + EVER_OS_BASE_URL from env

# Hybrid search across all agent memory types
response = memory.search(
    owner_id="agent_demo_001",
    owner_type="agent",
    query="data analysis and CSV processing",
    method="hybrid",
    top_k=5,
)
episodes = response.data.episodes if response.data else []
cases = response.data.agent_cases if response.data else []
skills = response.data.agent_skills if response.data else []

print(f"Found {len(episodes) if episodes else 0} episodes, "
      f"{len(cases) if cases else 0} cases, "
      f"{len(skills) if skills else 0} skills")

if episodes:
    for ep in episodes:
        print(f"\n[episode] score={ep.score}")
        print(f"  {ep.summary or ep.episode}")
if cases:
    for c in cases:
        print(f"\n[case] task_intent={c.task_intent}")
if skills:
    for s in skills:
        print(f"\n[skill] {s.name}: {s.description}")

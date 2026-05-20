# Install the everos python sdk:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration from old v1:
#   - memories.search(filters={"user_id": ...}, query=...)
#     → memory.search(owner_id=..., owner_type=..., query=...)
#   - include_profile=True replaces memory_types=["episodic_memory", "profile"]

from everos import EverOS

memory = EverOS().v1.memory  # reads EVEROS_API_KEY + EVER_OS_BASE_URL from env

response = memory.search(
    owner_id="user_demo_001",
    owner_type="user",
    query="coffee preference",
    method="hybrid",
    include_profile=True,
)

episodes = response.data.episodes if response.data else []
print(f"Found {len(episodes) if episodes else 0} memories")

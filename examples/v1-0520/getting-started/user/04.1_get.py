# Install the everos python sdk:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration from old v1:
#   - memories.get(filters={"user_id": ...}, memory_type=...)
#     → memory.get(owner_id=..., owner_type=..., memory_type=...)

from everos import EverOS

memory = EverOS().v1.memory  # reads EVEROS_API_KEY + EVER_OS_BASE_URL from env

response = memory.get(
    owner_id="user_demo_001",
    owner_type="user",
    memory_type="episodic_memory",
)

episodes = response.data.episodes if response.data else []
print(f"Fetched {len(episodes) if episodes else 0} memories")

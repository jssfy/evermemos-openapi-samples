# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - client.v1.memories  → client.v1.memory  (singular)
#   - memories.add(user_id=...)   → memory.add(owner_id=..., owner_type=..., session_id=...)
#   - memories.get(filters={"user_id": ...}) → memory.get(owner_id=..., owner_type=...)
import time
from everos import EverOS

client = EverOS()
memory = client.v1.memory

owner = "user_015"
session = "session_add_get_demo"

# 1. Add a memory
add_response = memory.add(
    owner_id=owner,
    owner_type="user",
    session_id=session,
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I went to the dentist today. I was scared of the dentist.",
        }
    ],
)

print("=== add response ===")
print(add_response)

print("Waiting for memory extraction...")
time.sleep(5)

# 2. Get memories for this user
get_response = memory.get(
    owner_id=owner,
    owner_type="user",
    memory_type="episodic_memory",
)

print("\n=== get response ===")
print(get_response)

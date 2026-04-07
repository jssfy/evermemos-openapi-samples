# everos should've been installed (pip install everos -U)
# NOTE: v0's status.request polling is REMOVED in v1.
#       Use client.v1.tasks.retrieve(task_id=...) for async task tracking.
import time
from everos import EverOS

client = EverOS()
memories = client.v1.memories

sender = "user_015"

# 1. Add a memory
add_response = memories.add(
    user_id=sender,
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

# 2. For async task tracking use: client.v1.tasks.retrieve(task_id=add_response.data.task_id)
#    Here we simply wait before querying.
print("Waiting for memory extraction...")
time.sleep(5)

# 3. Get memories for this user (add & get combined flow)
get_response = memories.get(
    filters={"user_id": sender},
    memory_type="episodic_memory",
)

print("\n=== get response ===")
print(get_response)

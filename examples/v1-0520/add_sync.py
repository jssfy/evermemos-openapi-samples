# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - client.v1.memories  → client.v1.memory  (singular)
#   - user_id             → owner_id + owner_type="user"
#   - session_id is now REQUIRED in add()
#   - response.data no longer has task_id; use status/message_count
import time
from everos import EverOS

client = EverOS()
memory = client.v1.memory

response = memory.add(
    owner_id="user_010",
    owner_type="user",
    session_id="session_001",
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I went to the dentist today. I was scared of the dentist.",
        }
    ],
)
print(response)

response = memory.add(
    owner_id="user_010",
    owner_type="user",
    session_id="session_001",
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I admire the beauty of the sea.",
        }
    ],
)
print(response)

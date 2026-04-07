# everos should've been installed (pip install everos -U)
# NOTE: v0's flush=True param is removed in v1.
#       Memory extraction is triggered automatically; call memories.flush(user_id=...)
#       explicitly only when you need to force a conversation boundary.
import time
from everos import EverOS

client = EverOS()
memories = client.v1.memories

response = memories.add(
    user_id="user_010",
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I went to the dentist today. I was scared of the dentist.",
        }
    ],
)
print(response)

response = memories.add(
    user_id="user_010",
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I admire the beauty of the sea.",
        }
    ],
)
print(response)

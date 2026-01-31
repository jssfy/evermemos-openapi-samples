# EverMemOS should've been installed (pip install evermemos -U)
from evermemos import EverMemOS

memories = EverMemOS().v1.memories

response = memories.add(
    content="I went to the dentist today. I was scared of the dentist.",
    create_time="2025-01-15T10:00:00+00:00",
    message_id="msg_001",
    sender="user_001",
)
print(response)
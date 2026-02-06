# EverMemOS should've been installed (pip install evermemos -U)
from evermemos import EverMemOS

memories = EverMemOS().v0.memories

response = memories.add(
    content="I went to the dentist today. I was scared of the dentist.",
    create_time="2025-01-15T10:00:00+00:00",
    message_id="msg_001",
    sender="user_010",
    flush=True, # Force memory extraction immediately, but not recommended for production use
)

print(response)

response = memories.add(
    content="I admire the beauty of the sea.",
    create_time="2025-01-15T10:00:00+00:00",
    message_id="msg_001",
    sender="user_010",
    flush=True, # Force memory extraction immediately, but not recommended for production use
)

print(response)
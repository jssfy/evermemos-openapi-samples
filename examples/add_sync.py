from evermemos import EverMemOS

client = EverMemOS()

memory = client.v1.memories.create(
    content="Let's discuss the technical solution for the new feature today",
    create_time="2025-01-15T10:00:00+00:00",
    message_id="msg_001",
    sender="user_001",
)
print(memory.message)
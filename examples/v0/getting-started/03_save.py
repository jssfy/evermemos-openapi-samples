# Install the evermemos python sdk
# bash command: pip install evermemos

from evermemos import EverMemOS

memory = EverMemOS(api_key="evermemos_api_key").v0.memories

messages = [
    {
        "message_id": "msg_001",
        "create_time": "2025-01-15T10:00:00Z",
        "sender": "user_demo_001",
        "sender_name": "Demo User",
        "group_id": "group_001",
        "content": "I like black Americano, no sugar, the stronger the better!"
    },
    {
        "message_id": "msg_002",
        "create_time": "2025-01-16T10:01:00Z",
        "sender": "user_demo_001",
        "sender_name": "Demo User",
        "group_id": "group_001",
        "content": "Today I want to discuss the project progress.",
        "flush": "true" # set flush to true, if this message is the final end of this conversation
    }
]

for msg in messages:
    response = memory.add(**msg)
    print(f"Status: {response.status}, Message: {response.message}, Request ID: {response.request_id}")
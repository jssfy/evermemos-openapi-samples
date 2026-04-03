# pip install everos
# Getting Started — Save memories with multimodal content (v1 SDK)
#
# The SDK auto-detects local paths and HTTP URLs in `uri` fields,
# uploads them, and calls add() with the resulting object keys.

import time
from everos import EverOS

client = EverOS(api_key="everos_api_key")
memories = client.v1.memories

now_ms = int(time.time() * 1000)

response = memories.add(
    user_id="user_demo_001",
    session_id="session_gs_003",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": [
                {"type": "text", "text": "Here is a photo from today's meeting."},
                {
                    "type": "image",
                    "uri": "./whiteboard.jpg",           # local path — auto-uploaded
                    "name": "whiteboard.jpg",
                    "ext": "jpg",
                    "text": "meeting whiteboard",
                },
            ],
        },
        {
            "role": "user",
            "timestamp": now_ms + 60_000,               # 1 minute later
            "content": [
                {"type": "text", "text": "Reference image from the web."},
                {
                    "type": "image",
                    "uri": "https://storage.example.com/uploads/restaurant.jpg",  # HTTP URL — auto-downloaded + uploaded
                },
            ],
        },
    ],
)
print(f"status={response.data.status}  task_id={response.data.task_id}")

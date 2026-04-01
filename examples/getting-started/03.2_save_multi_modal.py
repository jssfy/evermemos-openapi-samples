# pip install evermemos
# Getting Started — Save multimodal memories (v1 SDK)
# Demonstrates saving a message with mixed content: text + image + pdf

import time
from evermemos import EverMemOS

client = EverMemOS(api_key="evermemos_api_key")
memories = client.v1.memories

now_ms = int(time.time() * 1000)

response = memories.add(
    user_id="user_demo_001",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": [
                {
                    "type": "text",
                    "text": "Here are the files from my business trip",
                },
                {
                    "type": "image",
                    "uri": "https://storage.example.com/uploads/restaurant.jpg",
                    "ext": "jpg",
                    "name": "restaurant.jpg",
                    "text": "Restaurant photo from the trip",
                },
                {
                    "type": "pdf",
                    "uri": "https://storage.example.com/uploads/expense_report.pdf",
                    "ext": "pdf",
                    "name": "expense_report.pdf",
                },
            ],
        }
    ],
)
print(f"status={response.data.status}  task_id={response.data.task_id}")

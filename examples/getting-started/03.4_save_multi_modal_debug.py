# pip install everos
# Getting Started — Save memories with multimodal content (v1 SDK, debug logging)
#
# Same as 03.3, but with debug logging enabled to trace each upload step:
#   - which URIs are detected as local / HTTP / skipped
#   - sign request / response
#   - S3 upload attempts and result
#   - uri replacement and temp file cleanup

import logging
import time
from everos import EverOS

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(name)s: %(message)s",
)
logging.getLogger("everos").setLevel(logging.DEBUG)

client = EverOS() # 复用环境变量 EVEROS_API_KEY 来初始化 EverOS 客户端
memories = client.v1.memories

now_ms = int(time.time() * 1000)

response = memories.add(
    user_id="user_demo_001",
    session_id="session_gs_004",
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
                    "uri": "https://s41.ax1x.com/2026/04/01/peG0uAH.png",  # HTTP URL — auto-downloaded + uploaded
                },
            ],
        },
    ],
)
print(f"status={response.data.status}  task_id={response.data.task_id}")

"""Example: multimodal add — one-step interface.

The SDK automatically detects local file paths and HTTP/HTTPS URLs in content
item `uri` fields, signs and uploads them, then calls add() with the resulting
object keys. No manual sign/upload steps are required.

Prerequisites:
    pip install everos
    export EVEROS_API_KEY="your-api-key"
    export EVER_OS_BASE_URL="https://api.evermind.ai"   # optional
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import time
from pathlib import Path

from everos import AsyncEverOS, EverOS

API_KEY = os.environ.get("EVEROS_API_KEY", "")
BASE_URL = os.environ.get("EVER_OS_BASE_URL") or None
USER_ID = "demo_user_001"
SESSION_ID = "demo_session_001"


# ── Helper: create a small local test image ───────────────────────────────────


def _make_temp_image() -> Path:
    """Write a minimal 1×1 white JPEG to a temp file and return its path."""
    jpeg_bytes = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
        b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf5\x0a\xff\xd9"
    )
    fd, path = tempfile.mkstemp(suffix=".jpg", prefix="everos_demo_")
    os.write(fd, jpeg_bytes)
    os.close(fd)
    return Path(path)


# ── Sync example ──────────────────────────────────────────────────────────────


def sync_example() -> None:
    client = EverOS(api_key=API_KEY, base_url=BASE_URL)
    img_path = _make_temp_image()

    try:
        print(f"[sync] Using local image: {img_path}")
        print(f"[sync] Using remote image: https://s41.ax1x.com/2026/04/01/peG0uAH.png")

        # Both local path and HTTP URL are auto-signed and uploaded by the SDK
        response = client.v1.memories.add(
            user_id=USER_ID,
            session_id=SESSION_ID,
            messages=[
                {
                    "role": "user",
                    "timestamp": 1711900000000,
                    "content": [
                        {"type": "text", "text": "Snapshot from today's meeting"},
                        {
                            "type": "image",
                            "uri": str(img_path),   # ← local path, auto-uploaded
                            "name": img_path.name,
                            "ext": "jpg",
                            "text": "meeting whiteboard",
                        },
                    ],
                },
                {
                    "role": "user",
                    "timestamp": int(time.time() * 1000),
                    "content": [
                        {"type": "text", "text": "Image from the web"},
                        {
                            "type": "image",
                            "uri": "https://s41.ax1x.com/2026/04/01/peG0uAH.png",  # ← HTTP URL, auto-downloaded+uploaded
                        },
                    ],
                },
            ],
        )
        print(f"[sync] add() response.data={response.data}")

    finally:
        img_path.unlink(missing_ok=True)


# ── Async example ─────────────────────────────────────────────────────────────


async def async_example() -> None:
    async with AsyncEverOS(api_key=API_KEY, base_url=BASE_URL) as client:
        img_path = _make_temp_image()

        try:
            print(f"[async] Using local image: {img_path}")

            response = await client.v1.memories.add(
                user_id=USER_ID,
                session_id=SESSION_ID,
                messages=[
                    {
                        "role": "user",
                        "timestamp": 1711900001000,
                        "content": [
                            {"type": "text", "text": "Async version of the same upload"},
                            {
                                "type": "image",
                                "uri": str(img_path),   # ← same API, async path
                                "name": img_path.name,
                                "ext": "jpg",
                            },
                        ],
                    }
                ],
            )
            print(f"[async] add() response.data={response.data}")

        finally:
            img_path.unlink(missing_ok=True)


# ── Entry point ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    if not API_KEY:
        print("Set EVEROS_API_KEY to run this example.")
    else:
        sync_example()
        asyncio.run(async_example())

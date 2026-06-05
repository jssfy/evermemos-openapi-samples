#!/usr/bin/env python3
"""
09_delete_async.py — 异步 delete，多种过滤粒度

delete() 参数均可选，至少传一个过滤条件：
  user_id / session_id / sender_id / memory_id / group_id
"""
import asyncio, os, time
from everos_cloud import AsyncEverOS, NotFoundError

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")

client = AsyncEverOS(api_key=API_KEY, base_url=BASE_URL)


async def write_then_delete(user_id: str, session_id: str, label: str) -> None:
    now_ms = int(time.time() * 1000)
    await client.v1.memories.add(
        user_id=user_id,
        session_id=session_id,
        messages=[{"role": "user", "timestamp": now_ms, "content": [{"type": "text", "text": f"temp: {label}"}]}],
    )
    await asyncio.sleep(0.5)


async def main() -> None:
    uid = f"everos-cloud-del-{int(time.time())}"

    # 写入两个 session
    await asyncio.gather(
        write_then_delete(uid, "s1", "session 1"),
        write_then_delete(uid, "s2", "session 2"),
    )

    # Example 1: 删除指定 session
    print("=== delete by session_id ===")
    await client.v1.memories.delete(user_id=uid, session_id="s1")
    print("done")

    # Example 2: 删除用户所有记忆
    print("=== delete all by user_id ===")
    await client.v1.memories.delete(user_id=uid)
    print("done")

    # Example 3: 删除不存在的 memory_id（处理异常）
    print("=== delete non-existent memory_id ===")
    try:
        await client.v1.memories.delete(memory_id="000000000000000000000000")
        print("done (or silently ignored)")
    except NotFoundError as e:
        print(f"NotFoundError: {e}")
    except Exception as e:
        print(f"other error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

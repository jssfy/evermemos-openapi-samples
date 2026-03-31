# pip install evermemos
# 异步模式写入 + 轮询任务状态 —— 对应旧版 add_async.py / get_request_status_async.py
import asyncio
import time
from evermemos import AsyncEverMemOS, NotFoundError

client = AsyncEverMemOS()
memories = client.v1.memories
tasks = client.v1.tasks


async def wait_for_task(task_id: str, poll_interval: float = 2.0, max_attempts: int = 30) -> str:
    """轮询 task 直到完成，返回最终 status。

    404 表示 task 已处理完毕并从系统中清除（TTL 很短），视为成功。
    """
    for attempt in range(max_attempts):
        try:
            resp = await tasks.retrieve(task_id)
        except NotFoundError:
            # task 已完成并被清除
            print(f"  [attempt {attempt + 1}] task_id={task_id!r} status='done (expired)'")
            return "done"
        status = resp.data.status if resp.data else "unknown"
        print(f"  [attempt {attempt + 1}] task_id={task_id!r} status={status!r}")
        if status in ("success", "failed", "completed", "done"):
            return status
        await asyncio.sleep(poll_interval)
    return "timeout"


async def main() -> None:
    now_ms = int(time.time() * 1000)

    # async_mode=True → HTTP 202，返回 task_id
    response = await memories.add(
        user_id="user_010",
        async_mode=True,
        messages=[
            {
                "role": "user",
                "timestamp": now_ms,
                "content": "I love hiking on weekends, especially in the mountains.",
            },
            {
                "role": "assistant",
                "timestamp": now_ms + 1000,
                "content": "That sounds wonderful! Do you have a favorite trail?",
            },
            {
                "role": "user",
                "timestamp": now_ms + 2000,
                "content": "Yes, the mountain trails near the lake.",
            },
        ],
    )
    print("add response:", response)

    # 若后端返回 task_id，轮询等待完成
    task_id = response.data.task_id if response.data else None
    if task_id:
        final_status = await wait_for_task(task_id)
        print(f"Task finished with status: {final_status!r}")


if __name__ == "__main__":
    asyncio.run(main())

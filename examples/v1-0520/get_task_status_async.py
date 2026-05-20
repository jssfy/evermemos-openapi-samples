# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - API unchanged: client.v1.tasks.retrieve(task_id=...)
#   - In 0.0.1 add() response, AddMemoriesData no longer has task_id field.
#     Use response.request_id (top-level) as the task_id when polling status.
#     Verified: tasks.retrieve(task_id=response.request_id) returns status="success".
import os
import asyncio
from everos import AsyncEverOS

client = AsyncEverOS()


async def main() -> None:
    task_id = os.environ.get("EVEROS_TASK_ID", "your-task-id-here")

    response = await client.v1.tasks.retrieve(task_id=task_id)
    print(response)
    print(f"status: {response.status}")
    print(f"task_id: {response.task_id}")
    if response.error:
        print(f"error: {response.error}")


if __name__ == "__main__":
    asyncio.run(main())

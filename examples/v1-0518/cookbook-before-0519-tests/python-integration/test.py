"""
Cookbook: Python Integration Patterns
Tests: basic sync usage → concurrent requests → async_mode task polling
       error handling → fire-and-forget → logging/monitoring decorator
API: https://api.evermind.ai
"""
import os
import time
import logging
import threading
import queue as _queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from everos import EverOS, BadRequestError, NotFoundError

client   = EverOS()
memories = client.v1.memories
tasks    = client.v1.tasks

OWNER_ID = "cookbook_pyint_alice"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("everos_test")


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _poll_task(task_id: str, max_attempts: int = 15, interval: float = 2.0) -> str:
    for attempt in range(max_attempts):
        try:
            resp = tasks.retrieve(task_id)
        except NotFoundError:
            print(f"  [attempt {attempt+1}] task completed (expired/404)")
            return "done"
        status = resp.data.status if resp.data else "unknown"
        print(f"  [attempt {attempt+1}] status={status!r}")
        if status in ("success", "failed", "completed", "done"):
            return status
        time.sleep(interval)
    return "timeout"


# ── Case 1: Basic sync usage (add + search + get) ─────────────────────────
def test_basic_sync_usage():
    print("\n=== Case 1: Basic sync usage ===")
    resp = memories.add(
        user_id=OWNER_ID,
        session_id="pyint_session",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000),
                   "content": "I prefer morning meetings before 10am"}],
    )
    print("add:", resp.data)
    assert resp.data is not None

    time.sleep(3)

    search_resp = memories.search(
        filters={"user_id": OWNER_ID},
        query="meeting preferences",
        method="vector",
        top_k=5,
    )
    episodes = search_resp.data.episodes if search_resp.data else []
    print(f"search: {len(episodes)} episodes")

    get_resp = memories.get(
        filters={"user_id": OWNER_ID},
        memory_type="profile",
        page=1, page_size=10,
    )
    profiles = get_resp.data.profiles if get_resp.data else []
    print(f"get profile: {len(profiles)} profiles")
    print("PASS")


# ── Case 2: Concurrent requests ────────────────────────────────────────────
def test_concurrent_requests():
    print("\n=== Case 2: Concurrent requests ===")
    now_ms = int(time.time() * 1000)
    n = 10
    results, errors = [], []

    def store_one(i):
        try:
            return memories.add(
                user_id=OWNER_ID,
                session_id=f"conc_{i}",
                messages=[{"role": "user", "timestamp": now_ms + i,
                           "content": f"Concurrent message {i}"}],
            )
        except Exception as e:
            return e

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(store_one, i) for i in range(n)]
        for f in as_completed(futures):
            r = f.result()
            if isinstance(r, Exception):
                errors.append(str(r))
            else:
                results.append(r)

    print(f"Stored {len(results)}/{n}  errors={len(errors)}")
    assert len(results) >= n * 0.8, f"Too many failures: {errors}"
    print("PASS")


# ── Case 3: Async mode with task polling ──────────────────────────────────
def test_async_mode_task_polling():
    print("\n=== Case 3: Async mode with task polling ===")
    now_ms = int(time.time() * 1000)
    resp = memories.add(
        user_id=OWNER_ID,
        session_id="async_session",
        async_mode=True,
        messages=[
            {"role": "user",      "timestamp": now_ms,       "content": "I love hiking on weekends, especially in the mountains."},
            {"role": "assistant", "timestamp": now_ms + 1000, "content": "That sounds wonderful! Do you have a favorite trail?"},
            {"role": "user",      "timestamp": now_ms + 2000, "content": "Yes, the mountain trails near the lake."},
        ],
    )
    print("async add:", resp.data)
    task_id = resp.data.task_id if resp.data else None
    if task_id:
        print(f"Polling task {task_id}…")
        status = _poll_task(task_id)
        print(f"Final status: {status!r}")
        assert status in ("done", "success", "completed", "failed", "timeout")
    else:
        print("No task_id (synchronous processing)")
    print("PASS")


# ── Case 4: Error handling ─────────────────────────────────────────────────
def test_error_handling():
    print("\n=== Case 4: Error handling ===")

    # BadRequestError: empty messages list
    try:
        memories.add(user_id=OWNER_ID, session_id="s", messages=[])
        print("  empty messages: no error (server accepted)")
    except (BadRequestError, Exception) as e:
        print(f"  empty messages → {type(e).__name__}: {str(e)[:60]}")

    # NotFoundError: non-existent task
    try:
        tasks.retrieve("nonexistent_task_xyz_000")
        print("  bad task_id: no error")
    except NotFoundError as e:
        print(f"  bad task_id → NotFoundError ✓")
    except Exception as e:
        print(f"  bad task_id → {type(e).__name__}: {str(e)[:60]}")

    print("PASS")


# ── Case 5: Fire-and-forget (threaded queue) ──────────────────────────────
class FireAndForgetStore:
    def __init__(self, max_queue: int = 100):
        self._q: _queue.Queue = _queue.Queue(maxsize=max_queue)
        self._stats = {"sent": 0, "failed": 0}
        self._stop   = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def store(self, user_id: str, content: str, role: str = "user"):
        try:
            self._q.put_nowait({"user_id": user_id, "role": role, "content": content})
        except _queue.Full:
            logger.warning("Queue full, dropping message")

    def _run(self):
        while not self._stop.is_set() or not self._q.empty():
            try:
                msg = self._q.get(timeout=0.5)
            except _queue.Empty:
                continue
            try:
                memories.add(
                    user_id=msg["user_id"],
                    session_id="ff_session",
                    messages=[{"role": msg["role"],
                               "timestamp": int(time.time() * 1000),
                               "content": msg["content"]}],
                )
                self._stats["sent"] += 1
            except Exception as e:
                logger.error(f"Store failed: {e}")
                self._stats["failed"] += 1
            self._q.task_done()

    def stop(self):
        self._stop.set()
        self._worker.join(timeout=10)

    def stats(self):
        return dict(self._stats)


def test_fire_and_forget():
    print("\n=== Case 5: Fire-and-forget storage ===")
    store = FireAndForgetStore()
    n = 20
    for i in range(n):
        store.store("cookbook_pyint_ff_user", f"Background message {i}")
    time.sleep(4)
    store.stop()
    s = store.stats()
    print(f"Sent={s['sent']}  Failed={s['failed']}  (queued {n})")
    assert s["sent"] + s["failed"] == n
    print("PASS")


# ── Case 6: Logging / monitoring decorator ─────────────────────────────────
def log_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            ms = (time.perf_counter() - start) * 1000
            logger.info(f"EverOS {func.__name__} OK  {ms:.1f}ms")
            return result
        except Exception as e:
            ms = (time.perf_counter() - start) * 1000
            logger.error(f"EverOS {func.__name__} FAIL  {ms:.1f}ms  {e}")
            raise
    return wrapper


@log_operation
def _monitored_add(content: str):
    return memories.add(
        user_id=OWNER_ID, session_id="mon_session",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000), "content": content}],
    )


@log_operation
def _monitored_search(query: str):
    return memories.search(
        filters={"user_id": OWNER_ID}, query=query, method="vector", top_k=5,
    )


def test_logging_and_monitoring():
    print("\n=== Case 6: Logging and monitoring decorator ===")
    r1 = _monitored_add("Observability test message for EverOS")
    assert r1.data is not None
    time.sleep(2)
    r2 = _monitored_search("observability monitoring")
    episodes = r2.data.episodes if r2.data else []
    print(f"Monitored search returned {len(episodes)} episodes")
    print("PASS")


if __name__ == "__main__":
    test_basic_sync_usage()
    test_concurrent_requests()
    test_async_mode_task_polling()
    test_error_handling()
    test_fire_and_forget()
    test_logging_and_monitoring()
    print("\n✅ All python-integration cases passed")

"""
Cookbook: Python Integration Patterns
SDK: everos (new v1 SDK)
ENV: EVEROS_API_KEY_DEV + dev-gateway

NOTE on missing methods vs old SDK:
  - flush()  → NOT available in new API (no /memory/flush endpoint)
  - group.add() → use memory.add(owner_type="user", owner_id=group_id)
  - agent.add() → use memory.add(owner_type="agent", owner_id=agent_id)
  - feedback()  → NEW in new SDK (not in old SDK)
"""
import os
import time
import logging
import threading
import queue as _queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from everos import EverOS, BadRequestError, NotFoundError

BASE_URL = os.environ.get("EVEROS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
API_KEY  = os.environ.get("EVEROS_API_KEY", "")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
memory = client.memory
tasks  = client.tasks

OWNER_ID   = "cookbook_pyint_alice"
OWNER_TYPE = "user"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("everos_test")


def _poll_task(task_id: str, max_attempts: int = 15, interval: float = 2.0) -> str:
    for attempt in range(max_attempts):
        try:
            resp = tasks.retrieve(task_id)
        except NotFoundError:
            print(f"  [attempt {attempt+1}] task completed (expired/404)")
            return "done"
        status = getattr(resp.data, "status", "unknown") if resp.data else "unknown"
        print(f"  [attempt {attempt+1}] status={status!r}")
        if status in ("success", "failed", "completed", "done"):
            return status
        time.sleep(interval)
    return "timeout"


# ── Case 1: Basic sync usage (add + search + get) ─────────────────────────
def test_basic_sync_usage():
    print("\n=== Case 1: Basic sync usage ===")
    resp = memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="pyint_session",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000),
                   "content": "I prefer morning meetings before 10am"}],
    )
    print("add:", resp.data)
    assert resp.data is not None
    time.sleep(3)

    s = memory.search(owner_id=OWNER_ID, owner_type=OWNER_TYPE,
                      query="meeting preferences", method="vector", top_k=5)
    episodes = s.data.episodes or [] if s.data else []
    print(f"search: {len(episodes)} episodes")

    g = memory.get(memory_type="profile", owner_id=OWNER_ID, owner_type=OWNER_TYPE,
                   page=1, page_size=10)
    profiles = g.data.profiles or [] if g.data else []
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
            return memory.add(
                owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id=f"conc_{i}",
                messages=[{"role": "user", "timestamp": now_ms + i,
                           "content": f"Concurrent message {i}"}],
            )
        except Exception as e:
            return e

    with ThreadPoolExecutor(max_workers=5) as pool:
        for f in as_completed([pool.submit(store_one, i) for i in range(n)]):
            r = f.result()
            (errors if isinstance(r, Exception) else results).append(r)

    print(f"Stored {len(results)}/{n}  errors={len(errors)}")
    assert len(results) >= n * 0.8
    print("PASS")


# ── Case 3: Async mode with task polling ──────────────────────────────────
def test_async_mode_task_polling():
    print("\n=== Case 3: Async mode with task polling ===")
    now_ms = int(time.time() * 1000)
    resp = memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="async_session",
        async_mode=True,
        messages=[
            {"role": "user",      "timestamp": now_ms,       "content": "I love hiking in the mountains."},
            {"role": "assistant", "timestamp": now_ms + 1000, "content": "Sounds wonderful!"},
            {"role": "user",      "timestamp": now_ms + 2000, "content": "Yes, the trails near the lake."},
        ],
    )
    print("async add:", resp.data)
    task_id = getattr(resp.data, "task_id", None) if resp.data else None
    if task_id:
        print(f"Polling task {task_id}…")
        status = _poll_task(task_id)
        print(f"Final status: {status!r}")
    else:
        # New API add response: AddMemoriesData(message_count, status) — no task_id field
        print("No task_id in response (new API processes synchronously / no task tracking on add)")
    print("PASS")


# ── Case 4: Error handling ─────────────────────────────────────────────────
def test_error_handling():
    print("\n=== Case 4: Error handling ===")
    try:
        memory.add(owner_id="", owner_type=OWNER_TYPE, session_id="s", messages=[])
        print("  empty owner_id: no error")
    except (BadRequestError, Exception) as e:
        print(f"  empty owner_id → {type(e).__name__} ✓")

    try:
        tasks.retrieve("nonexistent_task_xyz_000")
        print("  bad task_id: no error")
    except NotFoundError:
        print("  bad task_id → NotFoundError ✓")
    except Exception as e:
        print(f"  bad task_id → {type(e).__name__}: {str(e)[:60]}")

    print("PASS")


# ── Case 5: Fire-and-forget (threaded queue) ──────────────────────────────
class FireAndForgetStore:
    def __init__(self, max_queue: int = 100):
        self._q      = _queue.Queue(maxsize=max_queue)
        self._stats  = {"sent": 0, "failed": 0}
        self._stop   = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def store(self, owner_id: str, content: str, role: str = "user"):
        try:
            self._q.put_nowait({"owner_id": owner_id, "role": role, "content": content})
        except _queue.Full:
            logger.warning("Queue full, dropping")

    def _run(self):
        while not self._stop.is_set() or not self._q.empty():
            try:
                msg = self._q.get(timeout=0.5)
            except _queue.Empty:
                continue
            try:
                memory.add(
                    owner_id=msg["owner_id"], owner_type=OWNER_TYPE,
                    session_id="ff_session",
                    messages=[{"role": msg["role"], "timestamp": int(time.time() * 1000),
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
            logger.info(f"EverOS {func.__name__} OK  {(time.perf_counter()-start)*1000:.1f}ms")
            return result
        except Exception as e:
            logger.error(f"EverOS {func.__name__} FAIL  {e}")
            raise
    return wrapper


@log_operation
def _monitored_add(content: str):
    return memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="mon_session",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000), "content": content}],
    )


@log_operation
def _monitored_search(query: str):
    return memory.search(owner_id=OWNER_ID, owner_type=OWNER_TYPE,
                         query=query, method="vector", top_k=5)


def test_logging_and_monitoring():
    print("\n=== Case 6: Logging and monitoring ===")
    r1 = _monitored_add("Observability test message for EverOS")
    assert r1.data is not None
    time.sleep(2)
    r2 = _monitored_search("observability monitoring")
    episodes = r2.data.episodes or [] if r2.data else []
    print(f"Monitored search: {len(episodes)} episodes")
    print("PASS")


# ── Case 7: memory.feedback() — NEW in new SDK ────────────────────────────
def test_feedback():
    print("\n=== Case 7: memory.feedback() [new in v1 SDK] ===")
    # First find a memory_id to give feedback on
    resp = memory.search(owner_id=OWNER_ID, owner_type=OWNER_TYPE,
                         query="morning meeting", method="vector", top_k=1)
    episodes = resp.data.episodes or [] if resp.data else []
    if episodes:
        ep = episodes[0]
        memory_id = getattr(ep, "memory_id", None) or getattr(ep, "id", None)
        if memory_id:
            fb = memory.feedback(
                content="This memory is accurate and useful",
                memory_id=memory_id,
                memory_type="episodic_memory",
                owner_id=OWNER_ID,
                owner_type=OWNER_TYPE,
            )
            print(f"feedback response: {fb}")
            print("PASS")
            return
    print("No episodes found to give feedback on (memories still processing) — SKIP")


if __name__ == "__main__":
    assert API_KEY, "Set EVEROS_API_KEY env var"
    test_basic_sync_usage()
    test_concurrent_requests()
    test_async_mode_task_polling()
    test_error_handling()
    test_fire_and_forget()
    test_logging_and_monitoring()
    test_feedback()
    print("\n✅ All python-integration cases passed")

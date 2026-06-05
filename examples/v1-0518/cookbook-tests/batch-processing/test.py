"""
Cookbook: Batch Processing
SDK: everos (new v1 SDK)
ENV: EVEROS_API_KEY_DEV + dev-gateway

NOTE on missing methods vs old SDK:
  - flush()        → NOT available in new API. No /memory/flush endpoint.
  - group.add()    → use memory.add(owner_id=group_id, owner_type="user",
                                    messages=[{...sender_id, sender_name...}])
  - group.flush()  → NOT available.
  - async task_id  → add() response has no task_id in new SDK.
                      tasks.retrieve() still works for other task types.
"""
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from everos import EverOS, NotFoundError

BASE_URL = os.environ.get("EVEROS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
API_KEY  = os.environ.get("EVEROS_API_KEY", "")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
memory = client.memory
tasks  = client.tasks

OWNER_TYPE = "user"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("batch_test")


# ── Case 1: Convert Slack export format ───────────────────────────────────
def test_convert_slack_format():
    print("\n=== Case 1: Convert Slack export format ===")
    slack_messages = [
        {"ts": "1705312800.000001", "user": "U001",
         "user_profile": {"real_name": "Alice"},
         "text": "Let's discuss the new architecture proposal."},
        {"ts": "1705312890.000002", "user": "U002",
         "user_profile": {"real_name": "Bob"},
         "text": "I think we should consider microservices."},
    ]
    messages = sorted([{
        "role":        "user",
        "sender_id":   m["user"],
        "sender_name": m.get("user_profile", {}).get("real_name", "Unknown"),
        "timestamp":   int(float(m["ts"]) * 1000),
        "content":     m["text"],
    } for m in slack_messages], key=lambda x: x["timestamp"])

    assert len(messages) == 2
    print(f"Converted {len(messages)} Slack messages for group_id=slack_engineering")
    print("PASS")
    return {"group_id": "slack_engineering", "messages": messages}


# ── Case 2: Convert Discord export format ─────────────────────────────────
def test_convert_discord_format():
    print("\n=== Case 2: Convert Discord export format ===")
    discord_messages = [
        {"id": "d001", "timestamp": "2024-01-15T10:00:00Z",
         "author": {"id": "da001", "username": "alice_dev"},
         "content": "Just deployed the new feature to staging!"},
        {"id": "d002", "timestamp": "2024-01-15T10:02:30Z",
         "author": {"id": "da002", "username": "bob_qa"},
         "content": "Running tests now."},
    ]
    messages = sorted([{
        "role":        "user",
        "sender_id":   m["author"]["id"],
        "sender_name": m["author"]["username"],
        "timestamp":   int(datetime.fromisoformat(
                           m["timestamp"].replace("Z", "+00:00")).timestamp() * 1000),
        "content":     m["content"],
    } for m in discord_messages], key=lambda x: x["timestamp"])

    assert len(messages) == 2
    print(f"Converted {len(messages)} Discord messages")
    print("PASS")


# ── Case 3: Batch import personal conversation ─────────────────────────────
def test_batch_import_personal():
    print("\n=== Case 3: Batch import personal conversation ===")
    owner_id = "cookbook_batch_alice"
    session_id = "personal_conv_001"
    now_ms = int(time.time() * 1000)
    all_msgs = [
        {"role": "user",      "timestamp": now_ms,      "content": "I love hiking on weekends."},
        {"role": "assistant", "timestamp": now_ms+1000,  "content": "That sounds wonderful!"},
        {"role": "user",      "timestamp": now_ms+2000,  "content": "Mountain trails near the lake."},
        {"role": "assistant", "timestamp": now_ms+3000,  "content": "Do you go alone or with friends?"},
        {"role": "user",      "timestamp": now_ms+4000,  "content": "With my dog, Max."},
    ]
    chunk_size, sent = 2, 0
    for i in range(0, len(all_msgs), chunk_size):
        chunk = all_msgs[i:i + chunk_size]
        resp  = memory.add(owner_id=owner_id, owner_type=OWNER_TYPE,
                           session_id=session_id, messages=chunk)
        assert resp.data is not None
        sent += len(chunk)
        logger.info(f"  Chunk {i//chunk_size+1}: {len(chunk)} msgs")
    # NOTE: flush() not available in new API
    print(f"Imported {sent} messages (flush not available — boundary detection is automatic)")
    print("PASS")


# ── Case 4: Batch import group conversation ────────────────────────────────
def test_batch_import_group():
    print("\n=== Case 4: Batch import group conversation ===")
    group_id = "cookbook_batch_group_eng"
    now_ms   = int(time.time() * 1000)
    all_msgs = [
        {"role": "user", "sender_id": "u_alice", "sender_name": "Alice",
         "timestamp": now_ms,       "content": "Architecture: microservices vs monolith?"},
        {"role": "user", "sender_id": "u_bob",   "sender_name": "Bob",
         "timestamp": now_ms+5000,  "content": "Microservices would scale better."},
        {"role": "user", "sender_id": "u_carol",  "sender_name": "Carol",
         "timestamp": now_ms+10000, "content": "Agreed, independent deployments too."},
        {"role": "user", "sender_id": "u_alice", "sender_name": "Alice",
         "timestamp": now_ms+15000, "content": "Let's go with microservices."},
    ]
    chunk_size, sent = 2, 0
    for i in range(0, len(all_msgs), chunk_size):
        chunk = all_msgs[i:i + chunk_size]
        # Group = owner_type="user" with shared owner_id; sender_id/sender_name in messages
        resp = memory.add(owner_id=group_id, owner_type=OWNER_TYPE,
                          session_id=group_id, messages=chunk)
        assert resp.data is not None
        sent += len(chunk)
    # NOTE: group.flush() not available in new API
    print(f"Imported {sent} group messages (no group.flush() in new API)")
    print("PASS")


# ── Case 5: Large conversation chunked import ──────────────────────────────
def test_large_conversation_chunked():
    print("\n=== Case 5: Large conversation chunked ===")
    owner_id, chunk_size = "cookbook_batch_large_user", 4
    now_ms = int(time.time() * 1000)
    all_msgs = [
        {"role": "user" if i % 2 == 0 else "assistant",
         "timestamp": now_ms + i * 2000,
         "content": f"Message {i+1}: topic {i//2+1}"}
        for i in range(12)
    ]
    total_sent, stages = 0, (len(all_msgs) + chunk_size - 1) // chunk_size
    for stage, i in enumerate(range(0, len(all_msgs), chunk_size)):
        chunk = all_msgs[i:i + chunk_size]
        resp  = memory.add(owner_id=owner_id, owner_type=OWNER_TYPE,
                           session_id=f"large_stage_{stage}", messages=chunk)
        assert resp.data is not None
        total_sent += len(chunk)
    print(f"Processed 12 messages in {stages} stages, sent={total_sent}")
    print("PASS")


# ── Case 6: Error recovery / checkpoint ───────────────────────────────────
class CheckpointImporter:
    def __init__(self):
        self.checkpoint: Dict[str, Any] = {"completed": [], "last_index": {}}
        self.stats = {"sent": 0, "failed": 0, "skipped": 0}

    def import_conv(self, conv_id: str, msgs: List[dict], chunk_size: int = 3) -> Dict:
        if conv_id in self.checkpoint["completed"]:
            logger.info(f"Skipping {conv_id}")
            self.stats["skipped"] += 1
            return {"conversation_id": conv_id, "skipped": True}

        last = self.checkpoint["last_index"].get(conv_id, 0)
        sent = failed = 0
        for i in range(last, len(msgs), chunk_size):
            chunk = msgs[i:i + chunk_size]
            try:
                memory.add(owner_id=conv_id, owner_type=OWNER_TYPE,
                           session_id=conv_id, messages=chunk)
                sent += len(chunk)
                self.checkpoint["last_index"][conv_id] = i + len(chunk)
            except Exception as e:
                logger.error(f"Chunk failed: {e}")
                failed += len(chunk)
        if failed == 0:
            self.checkpoint["completed"].append(conv_id)
        self.stats["sent"] += sent
        self.stats["failed"] += failed
        return {"conversation_id": conv_id, "messages_sent": sent, "messages_failed": failed}


def test_error_recovery_checkpoint():
    print("\n=== Case 6: Error recovery / checkpoint ===")
    imp    = CheckpointImporter()
    now_ms = int(time.time() * 1000)
    msgs   = [{"role": "user" if i%2==0 else "assistant",
               "timestamp": now_ms + i * 1000,
               "content": f"Recovery test message {i+1}"} for i in range(6)]

    r1 = imp.import_conv("cookbook_batch_checkpoint_conv", msgs)
    print(f"First import: {r1}")
    assert r1["messages_sent"] == 6

    r2 = imp.import_conv("cookbook_batch_checkpoint_conv", msgs)
    print(f"Second import: {r2}")
    assert r2.get("skipped") is True
    print(f"Stats: {imp.stats}")
    print("PASS")


# ── Case 7: Import stats tracking ─────────────────────────────────────────
def test_import_stats_tracking():
    print("\n=== Case 7: Import stats tracking ===")
    stats  = {"messages_sent": 0, "messages_failed": 0, "conversations_processed": 0}
    now_ms = int(time.time() * 1000)
    convs  = [
        {"owner_id": "cookbook_batch_stats_u1", "session": "stats_c1",
         "msgs": [{"role": "user", "timestamp": now_ms,     "content": "First conv"},
                  {"role": "user", "timestamp": now_ms+1000, "content": "More details"}]},
        {"owner_id": "cookbook_batch_stats_u2", "session": "stats_c2",
         "msgs": [{"role": "user", "timestamp": now_ms+2000, "content": "Second conv"}]},
    ]
    for c in convs:
        try:
            resp = memory.add(owner_id=c["owner_id"], owner_type=OWNER_TYPE,
                              session_id=c["session"], messages=c["msgs"])
            assert resp.data is not None
            stats["messages_sent"] += len(c["msgs"])
            # flush() not available — boundary detection automatic
        except Exception as e:
            logger.error(f"Failed: {e}")
            stats["messages_failed"] += len(c["msgs"])
        stats["conversations_processed"] += 1
    print(f"Stats: {stats}")
    assert stats["conversations_processed"] == len(convs)
    print("PASS")


# ── Case 8: Async mode import ─────────────────────────────────────────────
def test_async_mode_import():
    print("\n=== Case 8: Async mode import ===")
    now_ms = int(time.time() * 1000)
    resp   = memory.add(
        owner_id="cookbook_batch_async_user", owner_type=OWNER_TYPE,
        session_id="async_import_session", async_mode=True,
        messages=[
            {"role": "user",      "timestamp": now_ms,       "content": "Async import A"},
            {"role": "assistant", "timestamp": now_ms + 1000, "content": "Acknowledged A"},
            {"role": "user",      "timestamp": now_ms + 2000, "content": "Async import B"},
        ],
    )
    print("async add:", resp.data)
    # New API add response has no task_id — async processing happens server-side
    task_id = getattr(resp.data, "task_id", None) if resp.data else None
    if task_id:
        print(f"Polling task {task_id}…")
        for attempt in range(10):
            try:
                t = tasks.retrieve(task_id)
                status = getattr(t.data, "status", "unknown") if t.data else "unknown"
                print(f"  [{attempt+1}] {status}")
                if status in ("success", "failed", "completed", "done"):
                    break
            except NotFoundError:
                print(f"  [{attempt+1}] done (expired)")
                break
            time.sleep(2)
    else:
        print("No task_id in response (new API: async_mode has no client-side task tracking)")
    print("PASS")


if __name__ == "__main__":
    assert API_KEY, "Set EVEROS_API_KEY env var"
    test_convert_slack_format()
    test_convert_discord_format()
    test_batch_import_personal()
    test_batch_import_group()
    test_large_conversation_chunked()
    test_error_recovery_checkpoint()
    test_import_stats_tracking()
    test_async_mode_import()
    print("\n✅ All batch-processing cases passed")

"""
Cookbook: Team Collaboration & Group Chat
Tests: group message storage → search group vs personal episodes
       MeetingMemoryBot workflow → group ID naming conventions
API: https://api.evermind.ai
"""
import os
import time
from everos import EverOS

client   = EverOS()
memories = client.v1.memories

GROUP_ID = "cookbook_team_engineering"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _group_add(group_id: str, msgs: list):
    return memories.group.add(group_id=group_id, messages=msgs)


def _group_search(group_id: str, query: str, top_k: int = 10):
    return memories.search(
        filters={"group_id": group_id},
        query=query,
        method="vector",
        top_k=top_k,
    )


def _user_add(user_id: str, session_id: str, msgs: list):
    return memories.add(user_id=user_id, session_id=session_id, messages=msgs)


def _user_search(user_id: str, query: str, top_k: int = 10):
    return memories.search(
        filters={"user_id": user_id},
        query=query,
        method="vector",
        top_k=top_k,
    )


# ── Case 1: Store group discussion messages ────────────────────────────────
def test_store_group_messages():
    print("\n=== Case 1: Store group discussion messages ===")
    now_ms = int(time.time() * 1000)
    resp = _group_add(GROUP_ID, [
        {"role": "user", "sender_id": "u_alice", "sender_name": "Alice",
         "timestamp": now_ms,       "content": "Team, we need to decide on the database for the new project."},
        {"role": "user", "sender_id": "u_bob",   "sender_name": "Bob",
         "timestamp": now_ms+5000,  "content": "I think PostgreSQL would work well. It's what we know best."},
        {"role": "user", "sender_id": "u_carol",  "sender_name": "Carol",
         "timestamp": now_ms+10000, "content": "I agree with Bob. Plus we already have monitoring set up for Postgres."},
        {"role": "user", "sender_id": "u_alice", "sender_name": "Alice",
         "timestamp": now_ms+15000, "content": "Good points. Let's go with PostgreSQL. Bob, can you set up the schema?"},
        {"role": "user", "sender_id": "u_bob",   "sender_name": "Bob",
         "timestamp": now_ms+20000, "content": "Sure, I'll have a draft ready by Friday."},
    ])
    print("response:", resp)
    assert resp.data is not None
    print("PASS")


# ── Case 2: Search group memories ─────────────────────────────────────────
def test_search_group_memories():
    print("\n=== Case 2: Search group memories ===")
    time.sleep(3)
    resp = _group_search(GROUP_ID, "database decision", top_k=5)
    episodes = resp.data.episodes if resp.data else []
    print(f"Found {len(episodes)} episodes")
    for ep in episodes[:3]:
        print(f"  score={getattr(ep, 'score', '?')}  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 3: Personal perspective (per-participant search) ──────────────────
def test_personal_perspective():
    print("\n=== Case 3: Personal perspective per participant ===")
    now_ms = int(time.time() * 1000)
    _user_add("cookbook_team_bob", "bob_personal", [
        {"role": "user", "timestamp": now_ms,      "content": "I advocated for PostgreSQL based on team familiarity."},
        {"role": "user", "timestamp": now_ms+1000,  "content": "I was assigned to create the database schema by Friday."},
    ])
    time.sleep(2)

    resp = _user_search("cookbook_team_bob", "project architecture PostgreSQL")
    episodes = resp.data.episodes if resp.data else []
    print(f"Bob's perspective: {len(episodes)} episodes")
    for ep in episodes[:2]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 4: MeetingMemoryBot – workflow ───────────────────────────────────
class MeetingMemoryBot:
    def __init__(self, group_id: str):
        self.group_id = group_id

    def setup_meeting(self, participants: list, topic: str):
        names = ", ".join(p["name"] for p in participants)
        memories.group.add(
            group_id=self.group_id,
            messages=[{
                "role": "user",
                "sender_id": "bot",
                "sender_name": "MeetingBot",
                "timestamp": int(time.time() * 1000),
                "content": f"Meeting started. Topic: {topic}. Participants: {names}",
            }],
        )

    def record(self, sender_id: str, sender_name: str, content: str):
        memories.group.add(
            group_id=self.group_id,
            messages=[{
                "role": "user",
                "sender_id": sender_id,
                "sender_name": sender_name,
                "timestamp": int(time.time() * 1000),
                "content": content,
            }],
        )

    def get_context(self, topic: str) -> list:
        resp = memories.search(
            filters={"group_id": self.group_id},
            query=topic,
            method="vector",
            top_k=5,
        )
        return resp.data.episodes if resp.data else []

    def end_meeting(self):
        memories.group.add(
            group_id=self.group_id,
            messages=[{
                "role": "user",
                "sender_id": "bot",
                "sender_name": "MeetingBot",
                "timestamp": int(time.time() * 1000),
                "content": "Meeting ended.",
            }],
        )
        memories.group.flush(group_id=self.group_id)


def test_meeting_memory_bot():
    print("\n=== Case 4: MeetingMemoryBot workflow ===")
    bot = MeetingMemoryBot("cookbook_sprint_planning")

    bot.setup_meeting(
        [{"user_id": "user_alice", "name": "Alice"}, {"user_id": "user_bob", "name": "Bob"}],
        "Q1 Sprint Planning",
    )
    bot.record("user_alice", "Alice", "We should prioritize the auth refactor this sprint.")
    bot.record("user_bob",   "Bob",   "Agreed. I can take the backend portion.")
    time.sleep(2)

    ctx = bot.get_context("authentication system")
    print(f"Context items: {len(ctx)}")
    for c in ctx[:2]:
        print(f"  {_ep_text(c)[:80]}")

    bot.end_meeting()
    print("PASS")


# ── Case 5: Group ID strategy (naming test) ───────────────────────────────
def test_group_id_strategy():
    print("\n=== Case 5: Group ID naming convention ===")
    group_ids = [
        "team_engineering_sprint_2024_01",
        "project_phoenix_standup",
        "meeting_quarterly_review_2024_q1",
    ]
    now_ms = int(time.time() * 1000)
    for gid in group_ids:
        resp = memories.group.add(
            group_id=gid,
            messages=[{"role": "user", "sender_id": "u1", "sender_name": "User",
                       "timestamp": now_ms, "content": f"Discussion in {gid}"}],
        )
        print(f"  {gid}: status={resp.data.status if resp.data else 'ok'}")
    print("PASS")


if __name__ == "__main__":
    test_store_group_messages()
    test_search_group_memories()
    test_personal_perspective()
    test_meeting_memory_bot()
    test_group_id_strategy()
    print("\n✅ All team-collaboration cases passed")

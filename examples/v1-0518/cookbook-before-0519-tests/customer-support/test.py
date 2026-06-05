"""
Cookbook: Customer Support Bot
Tests: create_ticket → store messages → gather context → generate response
       close_ticket (flush) → escalate to agent → cross-ticket intelligence
API: https://api.evermind.ai
"""
import os
import time
from everos import EverOS

client   = EverOS()
memories = client.v1.memories

CUSTOMER_ID = "cookbook_cs_john"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _store(user_id: str, session_id: str, role: str, content: str):
    memories.add(
        user_id=user_id,
        session_id=session_id,
        messages=[{"role": role, "timestamp": int(time.time() * 1000), "content": content}],
    )


def _search(user_id: str, query: str, top_k: int = 5):
    return memories.search(
        filters={"user_id": user_id},
        query=query,
        method="vector",
        top_k=top_k,
    )


# ── Case 1: Create ticket ──────────────────────────────────────────────────
def test_create_ticket():
    print("\n=== Case 1: Create ticket ===")
    resp = memories.add(
        user_id=CUSTOMER_ID,
        session_id="ticket_T2024001",
        messages=[{
            "role": "assistant",
            "timestamp": int(time.time() * 1000),
            "content": "Ticket opened: Unable to reset password",
        }],
    )
    print("response:", resp)
    assert resp.data is not None
    print("PASS")


# ── Case 2: Store customer messages ───────────────────────────────────────
def test_store_customer_messages():
    print("\n=== Case 2: Store customer messages ===")
    now_ms = int(time.time() * 1000)
    exchanges = [
        ("user",      "I've been trying to reset my password but the email never arrives."),
        ("assistant", "I'm sorry to hear that. Have you checked your spam folder?"),
        ("user",      "I checked spam folder too. My email is john@example.com"),
        ("assistant", "I can see your account. Let me manually trigger a password reset."),
    ]
    for i, (role, content) in enumerate(exchanges):
        memories.add(
            user_id=CUSTOMER_ID,
            session_id="ticket_T2024001",
            messages=[{"role": role, "timestamp": now_ms + i * 3000, "content": content}],
        )
    print(f"Stored {len(exchanges)} messages")
    print("PASS")


# ── Case 3: Gather context (profile + history) ────────────────────────────
def test_gather_context():
    print("\n=== Case 3: Gather context ===")
    time.sleep(3)
    query = "password reset email"
    resp = _search(CUSTOMER_ID, query, top_k=5)
    episodes = resp.data.episodes if resp.data else []
    profiles  = resp.data.profiles  if resp.data else []
    print(f"Episodes: {len(episodes)}  Profiles: {len(profiles)}")
    for ep in (episodes + profiles)[:3]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 4: Generate context-aware response (simulate) ───────────────────
def test_generate_context_aware_response():
    print("\n=== Case 4: Generate context-aware response ===")
    resp = _search(CUSTOMER_ID, "customer preferences history")
    episodes = resp.data.episodes if resp.data else []
    simulated = f"[LLM response using {len(episodes)} memory items]"
    print(f"Response: {simulated}")
    _store(CUSTOMER_ID, "ticket_T2024001", "assistant",
           "I've manually triggered a new password reset. Please check your inbox in 5 minutes.")
    print("PASS")


# ── Case 5: Close ticket (flush) ──────────────────────────────────────────
def test_close_ticket_flush():
    print("\n=== Case 5: Close ticket (flush) ===")
    resp = memories.flush(user_id=CUSTOMER_ID, session_id="ticket_T2024001")
    print("flush response:", resp)
    print("PASS")


# ── Case 6: Escalate to agent ─────────────────────────────────────────────
def test_escalate_to_agent():
    print("\n=== Case 6: Escalate to agent ===")
    time.sleep(2)
    resp = _search(CUSTOMER_ID, "issue summary resolution attempts", top_k=10)
    episodes = resp.data.episodes if resp.data else []
    handoff = {
        "ticket_id": "T2024001",
        "summary": [_ep_text(ep)[:80] for ep in episodes[:3]],
        "handoff_note": "Escalated to Sarah. See memory context for full history.",
    }
    print(f"Handoff: ticket={handoff['ticket_id']}  episodes={len(episodes)}")
    for s in handoff["summary"]:
        print(f"  - {s}")
    print("PASS")


# ── Case 7: Cross-ticket intelligence ─────────────────────────────────────
def test_cross_ticket_intelligence():
    print("\n=== Case 7: Cross-ticket intelligence ===")
    now_ms = int(time.time() * 1000)
    memories.add(
        user_id=CUSTOMER_ID,
        session_id="ticket_T2023050",
        messages=[
            {"role": "user",      "timestamp": now_ms,
             "content": "My email isn't receiving reset links again."},
            {"role": "assistant", "timestamp": now_ms + 1000,
             "content": "This customer has had email delivery issues before."},
        ],
    )
    time.sleep(2)
    resp = _search(CUSTOMER_ID, "issue problem error unable", top_k=20)
    episodes = resp.data.episodes if resp.data else []
    print(f"Found {len(episodes)} relevant past interactions")
    for ep in episodes[:3]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 8: CustomerSupportBot full workflow ──────────────────────────────
class CustomerSupportBot:
    def __init__(self, customer_id: str):
        self.customer_id = customer_id

    def create_ticket(self, ticket_id: str, subject: str) -> str:
        session_id = f"ticket_{ticket_id}"
        memories.add(
            user_id=self.customer_id, session_id=session_id,
            messages=[{"role": "assistant", "timestamp": int(time.time() * 1000),
                       "content": f"Ticket opened: {subject}"}],
        )
        return session_id

    def customer_message(self, ticket_id: str, message: str) -> str:
        session_id = f"ticket_{ticket_id}"
        memories.add(
            user_id=self.customer_id, session_id=session_id,
            messages=[{"role": "user", "timestamp": int(time.time() * 1000), "content": message}],
        )
        resp = memories.search(filters={"user_id": self.customer_id},
                               query=message, method="vector", top_k=5)
        n = len(resp.data.episodes) if resp.data else 0
        response = f"[Response using {n} memory items]"
        memories.add(
            user_id=self.customer_id, session_id=session_id,
            messages=[{"role": "assistant", "timestamp": int(time.time() * 1000), "content": response}],
        )
        return response

    def close_ticket(self, ticket_id: str):
        memories.flush(user_id=self.customer_id, session_id=f"ticket_{ticket_id}")


def test_support_bot_workflow():
    print("\n=== Case 8: CustomerSupportBot workflow ===")
    bot = CustomerSupportBot("cookbook_cs_workflow_user")
    session = bot.create_ticket("T2024099", "Login issues after recent update")
    print(f"Ticket session: {session}")
    r1 = bot.customer_message("T2024099", "I can't log in since the update this morning.")
    print(f"Bot: {r1}")
    r2 = bot.customer_message("T2024099", "I've tried clearing cookies and cache already.")
    print(f"Bot: {r2}")
    bot.close_ticket("T2024099")
    print("Ticket closed")
    print("PASS")


if __name__ == "__main__":
    test_create_ticket()
    test_store_customer_messages()
    test_gather_context()
    test_generate_context_aware_response()
    test_close_ticket_flush()
    test_escalate_to_agent()
    test_cross_ticket_intelligence()
    test_support_bot_workflow()
    print("\n✅ All customer-support cases passed")

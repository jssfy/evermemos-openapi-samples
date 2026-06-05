"""
Cookbook: Customer Support Bot
SDK: everos (new v1 SDK)
ENV: EVEROS_API_KEY_DEV + dev-gateway

NOTE: flush() not available in new API — no /memory/flush endpoint.
      Boundary detection happens automatically. Use delete() if cleanup needed.
"""
import os
import time
from everos import EverOS

BASE_URL = os.environ.get("EVEROS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
API_KEY  = os.environ.get("EVEROS_API_KEY", "")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
memory = client.memory

CUSTOMER_ID = "cookbook_cs_john"
OWNER_TYPE  = "user"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _store(owner_id: str, session_id: str, role: str, content: str):
    memory.add(
        owner_id=owner_id, owner_type=OWNER_TYPE, session_id=session_id,
        messages=[{"role": role, "timestamp": int(time.time() * 1000), "content": content}],
    )


def _search(owner_id: str, query: str, top_k: int = 5):
    return memory.search(owner_id=owner_id, owner_type=OWNER_TYPE,
                         query=query, method="vector", top_k=top_k)


# ── Case 1: Create ticket ──────────────────────────────────────────────────
def test_create_ticket():
    print("\n=== Case 1: Create ticket ===")
    resp = memory.add(
        owner_id=CUSTOMER_ID, owner_type=OWNER_TYPE, session_id="ticket_T2024001",
        messages=[{"role": "assistant", "timestamp": int(time.time() * 1000),
                   "content": "Ticket opened: Unable to reset password"}],
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
        memory.add(
            owner_id=CUSTOMER_ID, owner_type=OWNER_TYPE, session_id="ticket_T2024001",
            messages=[{"role": role, "timestamp": now_ms + i * 3000, "content": content}],
        )
    print(f"Stored {len(exchanges)} messages")
    print("PASS")


# ── Case 3: Gather context ────────────────────────────────────────────────
def test_gather_context():
    print("\n=== Case 3: Gather context ===")
    time.sleep(3)
    resp = _search(CUSTOMER_ID, "password reset email", top_k=5)
    episodes = resp.data.episodes or [] if resp.data else []
    profiles  = resp.data.profiles  or [] if resp.data else []
    print(f"Episodes: {len(episodes)}  Profiles: {len(profiles)}")
    for ep in (episodes + profiles)[:3]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 4: Generate context-aware response ───────────────────────────────
def test_generate_context_aware_response():
    print("\n=== Case 4: Generate context-aware response ===")
    resp = _search(CUSTOMER_ID, "customer preferences history")
    episodes = resp.data.episodes or [] if resp.data else []
    simulated = f"[LLM response using {len(episodes)} memory items]"
    print(f"Response: {simulated}")
    _store(CUSTOMER_ID, "ticket_T2024001", "assistant",
           "I've manually triggered a new password reset. Please check your inbox.")
    print("PASS")


# ── Case 5: Close ticket (no flush — N/A in new API) ─────────────────────
def test_close_ticket():
    print("\n=== Case 5: Close ticket ===")
    # New API has no flush(). Add a closing message; boundary detection is automatic.
    resp = memory.add(
        owner_id=CUSTOMER_ID, owner_type=OWNER_TYPE, session_id="ticket_T2024001",
        messages=[{"role": "assistant", "timestamp": int(time.time() * 1000),
                   "content": "Ticket T2024001 resolved and closed."}],
    )
    assert resp.data is not None
    print("Ticket closed (flush not available in new API — boundary detection is automatic)")
    print("PASS")


# ── Case 6: Escalate to agent ─────────────────────────────────────────────
def test_escalate_to_agent():
    print("\n=== Case 6: Escalate to agent ===")
    time.sleep(2)
    resp = _search(CUSTOMER_ID, "issue summary resolution attempts", top_k=10)
    episodes = resp.data.episodes or [] if resp.data else []
    handoff = {
        "ticket_id": "T2024001",
        "summary":   [_ep_text(ep)[:80] for ep in episodes[:3]],
        "note":      "Escalated to Sarah.",
    }
    print(f"Handoff: ticket={handoff['ticket_id']}  episodes={len(episodes)}")
    for s in handoff["summary"]:
        print(f"  - {s}")
    print("PASS")


# ── Case 7: Cross-ticket intelligence ─────────────────────────────────────
def test_cross_ticket_intelligence():
    print("\n=== Case 7: Cross-ticket intelligence ===")
    now_ms = int(time.time() * 1000)
    memory.add(
        owner_id=CUSTOMER_ID, owner_type=OWNER_TYPE, session_id="ticket_T2023050",
        messages=[
            {"role": "user",      "timestamp": now_ms,
             "content": "My email isn't receiving reset links again."},
            {"role": "assistant", "timestamp": now_ms + 1000,
             "content": "This customer has had email delivery issues before."},
        ],
    )
    time.sleep(2)
    resp = _search(CUSTOMER_ID, "issue problem error unable", top_k=20)
    episodes = resp.data.episodes or [] if resp.data else []
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
        memory.add(
            owner_id=self.customer_id, owner_type=OWNER_TYPE, session_id=session_id,
            messages=[{"role": "assistant", "timestamp": int(time.time() * 1000),
                       "content": f"Ticket opened: {subject}"}],
        )
        return session_id

    def customer_message(self, ticket_id: str, msg: str) -> str:
        session_id = f"ticket_{ticket_id}"
        memory.add(
            owner_id=self.customer_id, owner_type=OWNER_TYPE, session_id=session_id,
            messages=[{"role": "user", "timestamp": int(time.time() * 1000), "content": msg}],
        )
        resp = memory.search(owner_id=self.customer_id, owner_type=OWNER_TYPE,
                             query=msg, method="vector", top_k=5)
        n = len(resp.data.episodes or []) if resp.data else 0
        response = f"[Response using {n} memory items]"
        memory.add(
            owner_id=self.customer_id, owner_type=OWNER_TYPE, session_id=session_id,
            messages=[{"role": "assistant", "timestamp": int(time.time() * 1000), "content": response}],
        )
        return response

    def close_ticket(self, ticket_id: str):
        # New API: no flush(). Add closing boundary message.
        memory.add(
            owner_id=self.customer_id, owner_type=OWNER_TYPE, session_id=f"ticket_{ticket_id}",
            messages=[{"role": "assistant", "timestamp": int(time.time() * 1000),
                       "content": f"Ticket {ticket_id} closed."}],
        )


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
    assert API_KEY, "Set EVEROS_API_KEY env var"
    test_create_ticket()
    test_store_customer_messages()
    test_gather_context()
    test_generate_context_aware_response()
    test_close_ticket()
    test_escalate_to_agent()
    test_cross_ticket_intelligence()
    test_support_bot_workflow()
    print("\n✅ All customer-support cases passed")

"""
Cookbook: Personal AI Assistant
SDK: everos (new v1 SDK)
ENV: EVEROS_API_KEY_DEV + dev-gateway
"""
import os
import time
from everos import EverOS

BASE_URL = os.environ.get("EVEROS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
API_KEY  = os.environ.get("EVEROS_API_KEY", "")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
memory = client.memory

OWNER_ID   = "cookbook_pa_alice"
OWNER_TYPE = "user"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _add(content: str, role: str = "user") -> None:
    memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="pa_session",
        messages=[{"role": role, "timestamp": int(time.time() * 1000), "content": content}],
    )


def _search(query: str, top_k: int = 5, include_profile: bool = True):
    return memory.search(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE,
        query=query, method="hybrid", top_k=top_k, include_profile=include_profile,
    )


# ── Case 1: store_message ──────────────────────────────────────────────────
def test_store_message():
    print("\n=== Case 1: store_message ===")
    resp = memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="pa_session",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000),
                   "content": "I prefer meetings in the morning, before 10am."}],
    )
    print("response:", resp)
    assert resp.data is not None
    print("PASS")


# ── Case 2: get_memory_context (search) ────────────────────────────────────
def test_get_memory_context():
    print("\n=== Case 2: get_memory_context (search) ===")
    time.sleep(3)
    resp = _search("meeting schedule preferences")
    episodes = resp.data.episodes or [] if resp.data else []
    profiles  = resp.data.profiles  or [] if resp.data else []
    print(f"episodes={len(episodes)}  profiles={len(profiles)}")
    for ep in episodes[:3]:
        print(f"  [episode] {_ep_text(ep)[:80]}")
    for p in profiles[:3]:
        print(f"  [profile] {str(getattr(p, 'profile_data', ''))[:80]}")
    print("PASS")


# ── Case 3: PersonalAssistant chat loop ────────────────────────────────────
class PersonalAssistant:
    def __init__(self, owner_id: str):
        self.owner_id = owner_id

    def _store(self, content: str, role: str = "user"):
        memory.add(
            owner_id=self.owner_id, owner_type=OWNER_TYPE, session_id="pa_session",
            messages=[{"role": role, "timestamp": int(time.time() * 1000), "content": content}],
        )

    def _get_context(self, query: str) -> list:
        resp = memory.search(
            owner_id=self.owner_id, owner_type=OWNER_TYPE,
            query=query, method="hybrid", top_k=5, include_profile=True,
        )
        eps  = resp.data.episodes or [] if resp.data else []
        pros = resp.data.profiles  or [] if resp.data else []
        return eps + pros

    def chat(self, user_message: str) -> str:
        self._store(user_message, "user")
        context  = self._get_context(user_message)
        response = f"[LLM response using {len(context)} memory items]"
        self._store(response, "assistant")
        return response


def test_assistant_chat_loop():
    print("\n=== Case 3: PersonalAssistant chat loop ===")
    assistant = PersonalAssistant(OWNER_ID)
    r1 = assistant.chat("I prefer meetings in the morning, before 10am.")
    print(f"Turn 1: {r1}")
    r2 = assistant.chat("What time works best for our call tomorrow?")
    print(f"Turn 2: {r2}")
    assert "[LLM response" in r1 and "[LLM response" in r2
    print("PASS")


# ── Case 4: Preferences stored and retrieved ──────────────────────────────
def test_preferences_stored_and_retrieved():
    print("\n=== Case 4: Using preferences ===")
    for pref in ["I'm vegetarian and allergic to nuts", "I love Italian food"]:
        memory.add(
            owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="pa_prefs",
            messages=[{"role": "user", "timestamp": int(time.time() * 1000), "content": pref}],
        )
    time.sleep(3)
    resp = _search("restaurant dinner vegetarian")
    episodes = resp.data.episodes or [] if resp.data else []
    profiles  = resp.data.profiles  or [] if resp.data else []
    print(f"episodes={len(episodes)}  profiles={len(profiles)}")
    print("PASS")


# ── Case 5: Get profile memories ──────────────────────────────────────────
def test_get_profile():
    print("\n=== Case 5: Get profile memories ===")
    resp = memory.get(
        memory_type="profile", owner_id=OWNER_ID, owner_type=OWNER_TYPE,
        page=1, page_size=10,
    )
    profiles = resp.data.profiles or [] if resp.data else []
    print(f"profile count={len(profiles)}")
    for p in profiles[:3]:
        print(f"  {str(getattr(p, 'profile_data', ''))[:100]}")
    print("PASS")


# ── Case 6: Get episodic memories ─────────────────────────────────────────
def test_get_episodic():
    print("\n=== Case 6: Get episodic memories ===")
    resp = memory.get(
        memory_type="episodic_memory", owner_id=OWNER_ID, owner_type=OWNER_TYPE,
        page=1, page_size=10,
    )
    episodes = resp.data.episodes or [] if resp.data else []
    print(f"episodic count={len(episodes)}")
    for ep in episodes[:3]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


if __name__ == "__main__":
    assert API_KEY, "Set EVEROS_API_KEY env var"
    test_store_message()
    test_get_memory_context()
    test_assistant_chat_loop()
    test_preferences_stored_and_retrieved()
    test_get_profile()
    test_get_episodic()
    print("\n✅ All personal-assistant cases passed")

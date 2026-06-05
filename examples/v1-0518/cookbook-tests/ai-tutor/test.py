"""
Cookbook: AI Tutor
SDK: everos (new v1 SDK)
ENV: EVEROS_API_KEY_DEV + dev-gateway
"""
import os
import time
from datetime import datetime, timedelta
from everos import EverOS

BASE_URL = os.environ.get("EVEROS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
API_KEY  = os.environ.get("EVEROS_API_KEY", "")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
memory = client.memory

STUDENT_ID = "cookbook_tutor_emma"
OWNER_TYPE = "user"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _add(owner_id: str, student_msg: str, tutor_msg: str, session_id: str = "tutor_session"):
    now = int(time.time() * 1000)
    memory.add(
        owner_id=owner_id, owner_type=OWNER_TYPE, session_id=session_id,
        messages=[
            {"role": "user",      "timestamp": now,        "content": student_msg},
            {"role": "assistant", "timestamp": now + 1000, "content": tutor_msg},
        ],
    )


def _search(owner_id: str, query: str, top_k: int = 10):
    return memory.search(owner_id=owner_id, owner_type=OWNER_TYPE,
                         query=query, method="vector", top_k=top_k)


# ── Case 1: Set learning goals ─────────────────────────────────────────────
def test_set_learning_goals():
    print("\n=== Case 1: Set learning goals ===")
    resp = memory.add(
        owner_id=STUDENT_ID, owner_type=OWNER_TYPE, session_id="tutor_session",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000),
                   "content": "My learning goals for Calculus: pass the AP exam, understand derivatives and integrals"}],
    )
    assert resp.data is not None
    print("PASS")


# ── Case 2: Store tutoring interaction ────────────────────────────────────
def test_store_tutoring_interaction():
    print("\n=== Case 2: Store tutoring interaction ===")
    _add(STUDENT_ID, "Can you explain derivatives?",
         "A derivative measures how a function changes. For f(x)=x², f'(x)=2x.")
    print("PASS")


# ── Case 3: Record quiz result ─────────────────────────────────────────────
def test_record_quiz_result():
    print("\n=== Case 3: Record quiz result ===")
    topic, score, max_score = "Basic Derivatives", 7, 10
    missed = ["chain rule", "product rule"]
    pct = score / max_score * 100
    msg = (f"Quiz completed on {topic}. Score: {score}/{max_score} ({pct:.0f}%). "
           f"Concepts to review: {', '.join(missed)}. This topic needs more practice.")
    _add(STUDENT_ID, f"I just finished the {topic} quiz.", msg)
    print(f"  {msg[:80]}")
    print("PASS")


# ── Case 4: Record explanation ─────────────────────────────────────────────
def test_record_explanation():
    print("\n=== Case 4: Record explanation ===")
    topic, difficulty, understood = "chain rule", "intermediate", False
    status = "understood" if understood else "needs more explanation"
    msg = f"Explained {topic} at {difficulty} level. Student {status}. Will revisit."
    _add(STUDENT_ID, f"Can you explain {topic} at a {difficulty} level?", msg)
    print(f"  {msg[:80]}")
    print("PASS")


# ── Case 5: Identify knowledge gaps ───────────────────────────────────────
def test_identify_knowledge_gaps():
    print("\n=== Case 5: Identify knowledge gaps ===")
    time.sleep(3)
    resp = _search(STUDENT_ID, "needs review struggled difficult missed not understood", top_k=20)
    episodes = resp.data.episodes or [] if resp.data else []
    gaps = [ep for ep in episodes
            if any(w in _ep_text(ep).lower()
                   for w in ["review", "struggled", "difficult", "missed", "needs"])]
    print(f"Total episodes: {len(episodes)}  Gaps: {len(gaps)}")
    for g in gaps[:3]:
        print(f"  {_ep_text(g)[:80]}")
    print("PASS")


# ── Case 6: Get strong topics ──────────────────────────────────────────────
def test_get_strong_topics():
    print("\n=== Case 6: Get strong topics ===")
    _add(STUDENT_ID, "I just completed the Limits quiz.",
         "Assessment on Limits: 9/10 (90%). Excellent understanding demonstrated.")
    time.sleep(2)
    resp = _search(STUDENT_ID, "excellent mastered understood 90% 100%", top_k=20)
    episodes = resp.data.episodes or [] if resp.data else []
    strengths = [ep for ep in episodes
                 if any(w in _ep_text(ep).lower()
                        for w in ["excellent", "mastered", "understood", "90%", "100%"])]
    print(f"Strong topics: {len(strengths)}")
    print("PASS")


# ── Case 7: Schedule review ────────────────────────────────────────────────
def test_schedule_review():
    print("\n=== Case 7: Schedule review ===")
    topic = "chain rule"
    review_date = (datetime.now() + timedelta(days=3)).strftime("%B %d")
    _add(STUDENT_ID, f"When should I review {topic}?",
         f"You should review {topic} on {review_date}. Needs reinforcement.")
    print(f"  Scheduled '{topic}' for {review_date}")
    print("PASS")


# ── Case 8: Get due reviews ────────────────────────────────────────────────
def test_get_due_reviews():
    print("\n=== Case 8: Get due reviews ===")
    time.sleep(2)
    resp = _search(STUDENT_ID, "review remember study practice scheduled", top_k=10)
    episodes = resp.data.episodes or [] if resp.data else []
    print(f"Scheduled reviews: {len(episodes)}")
    for ep in episodes[:3]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 9: Adaptive question context fetch ───────────────────────────────
def test_generate_adaptive_question():
    print("\n=== Case 9: Adaptive question context fetch ===")
    topic = "derivatives"
    p = _search(STUDENT_ID, f"learning style pace {topic}", top_k=5)
    q = _search(STUDENT_ID, f"{topic} quiz score understanding", top_k=5)
    print(f"Profile items: {len(p.data.episodes or [])}  Progress items: {len(q.data.episodes or [])}")
    print(f"Prompt: Generate a {topic} question appropriate for this student's level")
    print("PASS")


# ── Case 10: Complete tutor workflow ──────────────────────────────────────
class AITutor:
    def __init__(self, subject: str, owner_id: str):
        self.subject  = subject
        self.owner_id = owner_id

    def _store(self, student_msg: str, tutor_msg: str):
        _add(self.owner_id, student_msg, tutor_msg)

    def _ctx(self, query: str) -> list:
        resp = _search(self.owner_id, query, top_k=5)
        return resp.data.episodes or [] if resp.data else []

    def study_session(self, msg: str) -> str:
        context   = self._ctx(msg)
        reminders = self._ctx("review remember practice scheduled")
        response  = f"[Tutor: {len(context)} progress memories, {len(reminders)} reminders]"
        self._store(msg, response)
        return response

    def record_assessment(self, topic: str, score: int, total: int, notes: str = ""):
        pct = (score / total) * 100
        self._store(f"I just completed the {topic} assessment.",
                    f"Assessment on {topic}: {score}/{total} ({pct:.0f}%). {notes}")
        if pct < 80:
            review_date = (datetime.now() + timedelta(days=3)).strftime("%B %d")
            self._store(f"When should I review {topic}?",
                        f"Review {topic} by {review_date} — scored {pct:.0f}%.")


def test_complete_tutor_workflow():
    print("\n=== Case 10: Complete tutor workflow ===")
    student = "cookbook_tutor_workflow_emma"
    memory.add(
        owner_id=student, owner_type=OWNER_TYPE, session_id="goals",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000),
                   "content": "My goals: pass AP Calculus, master derivatives and integrals"}],
    )
    tutor = AITutor("Calculus", student)
    r1 = tutor.study_session("I'm having trouble with derivatives. Can you explain?")
    print(f"Session 1: {r1}")
    tutor.record_assessment("Basic Derivatives", 7, 10, "Struggled with chain rule")
    r2 = tutor.study_session("Can we practice more derivative problems?")
    print(f"Session 2: {r2}")
    print("PASS")


# ── Case 11: Spaced repetition ─────────────────────────────────────────────
def test_spaced_repetition():
    print("\n=== Case 11: Spaced repetition ===")
    student = "cookbook_tutor_sr_emma"
    topic   = "Integration by Parts"
    for days in [3, 7, 14]:
        d = (datetime.now() + timedelta(days=days)).strftime("%B %d, %Y")
        _add(student, f"Schedule review for {topic}.",
             f"Scheduled: {topic} on {d}. Mastery: 2/5.", session_id="sr_session")
        print(f"  +{days} days → {d}")
    print("PASS")


if __name__ == "__main__":
    assert API_KEY, "Set EVEROS_API_KEY env var"
    test_set_learning_goals()
    test_store_tutoring_interaction()
    test_record_quiz_result()
    test_record_explanation()
    test_identify_knowledge_gaps()
    test_get_strong_topics()
    test_schedule_review()
    test_get_due_reviews()
    test_generate_adaptive_question()
    test_complete_tutor_workflow()
    test_spaced_repetition()
    print("\n✅ All ai-tutor cases passed")

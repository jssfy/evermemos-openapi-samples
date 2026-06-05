"""
Cookbook: AI Tutor
Tests: set_learning_goals → store_interaction → record_quiz_result
       record_explanation → identify_knowledge_gaps → get_strong_topics
       schedule_review → get_due_reviews → complete_tutor_workflow → spaced_repetition
API: https://api.evermind.ai
"""
import os
import time
from datetime import datetime, timedelta
from everos import EverOS

client   = EverOS()
memories = client.v1.memories

STUDENT_ID = "cookbook_tutor_emma"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


def _add(user_id: str, student_msg: str, tutor_msg: str, session_id: str = "tutor_session"):
    now = int(time.time() * 1000)
    memories.add(
        user_id=user_id,
        session_id=session_id,
        messages=[
            {"role": "user",      "timestamp": now,        "content": student_msg},
            {"role": "assistant", "timestamp": now + 1000, "content": tutor_msg},
        ],
    )


def _search(user_id: str, query: str, top_k: int = 10):
    return memories.search(
        filters={"user_id": user_id},
        query=query,
        method="vector",
        top_k=top_k,
    )


# ── Case 1: Set learning goals ─────────────────────────────────────────────
def test_set_learning_goals():
    print("\n=== Case 1: Set learning goals ===")
    resp = memories.add(
        user_id=STUDENT_ID,
        session_id="tutor_session",
        messages=[{
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "My learning goals for Calculus: pass the AP exam, understand derivatives and integrals",
        }],
    )
    assert resp.data is not None
    print("PASS")


# ── Case 2: Store tutoring interaction ────────────────────────────────────
def test_store_tutoring_interaction():
    print("\n=== Case 2: Store tutoring interaction ===")
    _add(STUDENT_ID,
         "Can you explain derivatives?",
         "A derivative measures how a function changes. For f(x)=x², f'(x)=2x.")
    print("PASS")


# ── Case 3: Record quiz result ─────────────────────────────────────────────
def test_record_quiz_result():
    print("\n=== Case 3: Record quiz result ===")
    topic, score, max_score = "Basic Derivatives", 7, 10
    missed = ["chain rule", "product rule"]
    pct = score / max_score * 100
    result_msg = (
        f"Quiz completed on {topic}. Score: {score}/{max_score} ({pct:.0f}%). "
        f"Concepts to review: {', '.join(missed)}. This topic needs more practice."
    )
    _add(STUDENT_ID, f"I just finished the {topic} quiz.", result_msg)
    print(f"  {result_msg[:80]}")
    print("PASS")


# ── Case 4: Record explanation ─────────────────────────────────────────────
def test_record_explanation():
    print("\n=== Case 4: Record explanation ===")
    topic, difficulty = "chain rule", "intermediate"
    understood = False
    status = "understood" if understood else "needs more explanation"
    msg = f"Explained {topic} at {difficulty} level. Student {status}. Will revisit with different approach."
    _add(STUDENT_ID, f"Can you explain {topic} at a {difficulty} level?", msg)
    print(f"  {msg[:80]}")
    print("PASS")


# ── Case 5: Identify knowledge gaps ───────────────────────────────────────
def test_identify_knowledge_gaps():
    print("\n=== Case 5: Identify knowledge gaps ===")
    time.sleep(3)
    resp = _search(STUDENT_ID,
                   "needs review struggled difficult missed concepts not understood",
                   top_k=20)
    episodes = resp.data.episodes if resp.data else []
    gaps = [ep for ep in episodes
            if any(w in _ep_text(ep).lower()
                   for w in ["review", "struggled", "difficult", "missed", "needs"])]
    print(f"Total episodes: {len(episodes)}  Gaps found: {len(gaps)}")
    for g in gaps[:3]:
        print(f"  {_ep_text(g)[:80]}")
    print("PASS")


# ── Case 6: Get strong topics ──────────────────────────────────────────────
def test_get_strong_topics():
    print("\n=== Case 6: Get strong topics ===")
    _add(STUDENT_ID,
         "I just completed the Limits quiz.",
         "Assessment on Limits: 9/10 (90%). Excellent understanding demonstrated.")
    time.sleep(2)

    resp = _search(STUDENT_ID,
                   "excellent mastered understood good progress correct 90% 100%",
                   top_k=20)
    episodes = resp.data.episodes if resp.data else []
    strengths = [ep for ep in episodes
                 if any(w in _ep_text(ep).lower()
                        for w in ["excellent", "mastered", "understood", "90%", "100%"])]
    print(f"Strong topics found: {len(strengths)}")
    for s in strengths[:3]:
        print(f"  {_ep_text(s)[:80]}")
    print("PASS")


# ── Case 7: Schedule review ────────────────────────────────────────────────
def test_schedule_review():
    print("\n=== Case 7: Schedule review ===")
    topic = "chain rule"
    review_date = (datetime.now() + timedelta(days=3)).strftime("%B %d")
    _add(STUDENT_ID,
         f"When should I review {topic}?",
         f"You should review {topic} on {review_date}. This topic needs reinforcement based on recent quiz results.")
    print(f"  Scheduled review of '{topic}' for {review_date}")
    print("PASS")


# ── Case 8: Get due reviews ────────────────────────────────────────────────
def test_get_due_reviews():
    print("\n=== Case 8: Get due reviews ===")
    time.sleep(2)
    resp = _search(STUDENT_ID, "review remember study practice scheduled review", top_k=10)
    episodes = resp.data.episodes if resp.data else []
    print(f"Scheduled reviews found: {len(episodes)}")
    for ep in episodes[:3]:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 9: Generate adaptive question (context fetch) ────────────────────
def test_generate_adaptive_question():
    print("\n=== Case 9: Generate adaptive question (context fetch) ===")
    topic = "derivatives"
    profile_resp  = _search(STUDENT_ID, f"learning style pace {topic}", top_k=5)
    progress_resp = _search(STUDENT_ID, f"{topic} quiz score understanding", top_k=5)

    profile_eps  = profile_resp.data.episodes  if profile_resp.data  else []
    progress_eps = progress_resp.data.episodes if progress_resp.data else []
    print(f"Profile items: {len(profile_eps)}  Progress items: {len(progress_eps)}")
    print(f"Prompt: Generate a {topic} question appropriate for this student's level")
    print("PASS")


# ── Case 10: Complete tutor workflow ──────────────────────────────────────
class AITutor:
    def __init__(self, subject: str, student_id: str):
        self.subject = subject
        self.student_id = student_id

    def _store(self, student_msg: str, tutor_msg: str):
        _add(self.student_id, student_msg, tutor_msg)

    def _context(self, query: str) -> list:
        resp = _search(self.student_id, query, top_k=5)
        return resp.data.episodes if resp.data else []

    def study_session(self, message: str) -> str:
        context   = self._context(message)
        reminders = self._context("review remember practice scheduled")
        response  = f"[Tutor response based on {len(context)} progress memories, {len(reminders)} reminders]"
        self._store(message, response)
        return response

    def record_assessment(self, topic: str, score: int, total: int, notes: str = ""):
        pct = (score / total) * 100
        tutor_msg = f"Assessment on {topic}: {score}/{total} ({pct:.0f}%). {notes}"
        self._store(f"I just completed the {topic} assessment.", tutor_msg)
        if pct < 80:
            review_date = (datetime.now() + timedelta(days=3)).strftime("%B %d")
            self._store(
                f"When should I review {topic}?",
                f"You should review {topic} by {review_date} - you scored {pct:.0f}%.",
            )


def test_complete_tutor_workflow():
    print("\n=== Case 10: Complete tutor workflow ===")
    student = "cookbook_tutor_workflow_emma"
    memories.add(
        user_id=student, session_id="tutor_goals",
        messages=[{"role": "user", "timestamp": int(time.time() * 1000),
                   "content": "My learning goals for Calculus: pass the AP exam, understand derivatives and integrals"}],
    )
    tutor = AITutor("Calculus", student)
    r1 = tutor.study_session("I'm having trouble understanding derivatives. Can you explain?")
    print(f"Session 1: {r1}")
    tutor.record_assessment("Basic Derivatives", 7, 10, "Struggled with chain rule applications")
    r2 = tutor.study_session("Can we practice more derivative problems?")
    print(f"Session 2: {r2}")
    print("PASS")


# ── Case 11: Spaced repetition ─────────────────────────────────────────────
def test_spaced_repetition():
    print("\n=== Case 11: Spaced repetition ===")
    student = "cookbook_tutor_sr_emma"
    topic = "Integration by Parts"
    mastery = 2
    intervals = {1: [1, 3, 7], 2: [3, 7, 14], 3: [7, 14, 30], 4: [14, 30, 60], 5: [30, 90]}
    for days in intervals[mastery]:
        review_date = (datetime.now() + timedelta(days=days)).strftime("%B %d, %Y")
        _add(student,
             f"Schedule my next review for {topic}.",
             f"Scheduled review: {topic} on {review_date}. Current mastery level: {mastery}/5.",
             session_id="sr_session")
        print(f"  +{days} days → {review_date}")
    print("PASS")


if __name__ == "__main__":
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

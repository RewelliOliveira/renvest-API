import random
from datetime import date

import pytest
from fastapi import HTTPException

from src.content.curriculum import Module
from src.services import trail_service
from src.services.trail_service import build_trail, compute_streak

TODAY = date(2026, 10, 17)
SOURCE = {"document": "Res. CVM 44", "section": "p. 3"}


def question(qid, correct="a"):
    return {
        "id": qid,
        "question": f"Pergunta {qid}?",
        "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
        "correct_option": correct,
        "explanation": "Porque sim.",
        "source": SOURCE,
    }


def make_module(order, lessons=2, bank=4, count=2):
    module_id = f"modulo_{order}"
    return Module.model_validate({
        "id": module_id,
        "order": order,
        "title": f"Módulo {order}",
        "subtitle": "s",
        "description": "d",
        "color": "#000",
        "lessons": [
            {
                "id": f"{module_id}_licao_{n}",
                "order": n,
                "title": f"Lição {n}",
                "subtitle": "s",
                "description": "d",
                "slides": [{"title": "t", "text": "x", "source": SOURCE}],
                "chat_suggestions": ["O que é?"],
                "quiz": [question(f"{module_id}_licao_{n}_q1")],
            }
            for n in range(1, lessons + 1)
        ],
        "exam": {
            "question_count": count,
            "pass_score": 0.5,
            "questions": [question(f"{module_id}_teste_q{n}") for n in range(1, bank + 1)],
        },
    })


MODULES = (make_module(1), make_module(2))
NO_STREAK = compute_streak([], TODAY)


def statuses(trail):
    return [(m.status, [lesson.status for lesson in m.lessons], m.exam.status) for m in trail.modules]


def test_new_user_starts_on_first_lesson_with_everything_else_locked():
    trail = build_trail(MODULES, set(), [], NO_STREAK)
    assert statuses(trail) == [
        ("current", ["current", "locked"], "locked"),
        ("locked", ["locked", "locked"], "locked"),
    ]
    assert trail.current_module_id == "modulo_1"
    assert not trail.completed


def test_exam_unlocks_only_after_all_lessons_of_the_module():
    trail = build_trail(MODULES, {"modulo_1_licao_1", "modulo_1_licao_2"}, [], NO_STREAK)
    assert statuses(trail)[0] == ("current", ["completed", "completed"], "current")
    assert statuses(trail)[1][0] == "locked"


def test_failed_exam_keeps_next_module_locked():
    attempts = [{"module_id": "modulo_1", "score": 0.0, "passed": False}]
    trail = build_trail(MODULES, {"modulo_1_licao_1", "modulo_1_licao_2"}, attempts, NO_STREAK)
    assert statuses(trail)[1][0] == "locked"
    assert trail.modules[0].exam.attempts == 1
    assert trail.modules[0].exam.best_score == 0.0


def test_passing_last_exam_completes_the_trail():
    attempts = [
        {"module_id": "modulo_1", "score": 1.0, "passed": True},
        {"module_id": "modulo_2", "score": 0.5, "passed": True},
    ]
    done = {lesson.id for module in MODULES for lesson in module.lessons}
    trail = build_trail(MODULES, done, attempts, NO_STREAK)
    assert all(module.status == "completed" for module in trail.modules)
    assert trail.completed and trail.current_module_id is None
    assert trail.progress.completed_modules == 2 and trail.progress.completed_lessons == 4


def test_lessons_of_a_locked_module_stay_locked_even_if_recorded():
    trail = build_trail(MODULES, {"modulo_2_licao_1"}, [], NO_STREAK)
    assert statuses(trail)[1] == ("locked", ["locked", "locked"], "locked")


@pytest.mark.parametrize("days, expected", [
    ([], (0, False)),
    ([TODAY], (1, True)),
    ([date(2026, 10, 16), date(2026, 10, 15)], (2, False)),
    ([TODAY, date(2026, 10, 16), date(2026, 10, 14)], (2, True)),
    ([date(2026, 10, 15)], (0, False)),
])
def test_compute_streak(days, expected):
    streak = compute_streak(days, TODAY)
    assert (streak.current_days, streak.active_today) == expected


class FakeProgressRepository:
    def __init__(self, completed=(), attempts=()):
        self.completed = set(completed)
        self.attempts = {}
        self.activity = set()
        for attempt in attempts:
            self.attempts[attempt["id"]] = dict(attempt)

    def list_completed_lessons(self, user_id):
        return set(self.completed)

    def mark_lesson_completed(self, user_id, lesson_id, module_id):
        self.completed.add(lesson_id)

    def record_activity(self, user_id, day):
        self.activity.add(day)

    def list_activity_dates(self, user_id):
        return set(self.activity)

    def list_submitted_attempts(self, user_id):
        return [a for a in self.attempts.values() if a.get("submitted_at")]

    def create_attempt(self, user_id, module_id, question_ids):
        attempt_id = f"attempt-{len(self.attempts) + 1}"
        self.attempts[attempt_id] = {"id": attempt_id, "module_id": module_id, "question_ids": question_ids}
        return attempt_id

    def get_attempt(self, user_id, attempt_id):
        return self.attempts.get(attempt_id)

    def submit_attempt(self, attempt_id, answers, score, passed):
        self.attempts[attempt_id].update(answers=answers, score=score, passed=passed, submitted_at="agora")


@pytest.fixture
def repo(monkeypatch):
    fake = FakeProgressRepository()
    monkeypatch.setattr(trail_service, "ProgressRepository", fake)
    monkeypatch.setattr(trail_service, "get_modules", lambda: MODULES)
    monkeypatch.setattr(trail_service, "get_module", lambda mid: next((m for m in MODULES if m.id == mid), None))
    monkeypatch.setattr(trail_service, "find_lesson", lambda lid: next(
        ((m, lesson) for m in MODULES for lesson in m.lessons if lesson.id == lid), None))
    monkeypatch.setattr(trail_service, "today_in_brazil", lambda: TODAY)
    return fake


def test_locked_lesson_cannot_be_opened_or_completed(repo):
    with pytest.raises(HTTPException) as error:
        trail_service.TrailService.get_lesson("u1", "modulo_1_licao_2")
    assert error.value.status_code == 403
    with pytest.raises(HTTPException):
        trail_service.TrailService.complete_lesson("u1", "modulo_1_licao_2")


def test_completing_a_lesson_unlocks_the_next_and_counts_for_the_streak(repo):
    trail = trail_service.TrailService.complete_lesson("u1", "modulo_1_licao_1")
    assert statuses(trail)[0][1] == ["completed", "current"]
    assert trail.streak.current_days == 1 and trail.streak.active_today


def test_exam_flow_grades_on_the_server_and_unlocks_next_module(repo):
    repo.completed.update({"modulo_1_licao_1", "modulo_1_licao_2"})
    start = trail_service.TrailService.start_exam("u1", "modulo_1", rng=random.Random(0))
    assert len(start.questions) == 2
    assert "correct_option" not in start.questions[0].model_dump()

    answers = {q.id: "a" for q in start.questions}
    result = trail_service.TrailService.submit_exam("u1", start.attempt_id, answers)
    assert result.passed and result.score == 1.0 and result.correct_count == 2
    assert statuses(result.trail)[1][0] == "current"

    with pytest.raises(HTTPException) as error:
        trail_service.TrailService.submit_exam("u1", start.attempt_id, answers)
    assert error.value.status_code == 409


def test_exam_requires_answers_to_exactly_the_drawn_questions(repo):
    repo.completed.update({"modulo_1_licao_1", "modulo_1_licao_2"})
    start = trail_service.TrailService.start_exam("u1", "modulo_1", rng=random.Random(0))
    with pytest.raises(HTTPException) as error:
        trail_service.TrailService.submit_exam("u1", start.attempt_id, {"modulo_1_teste_q99": "a"})
    assert error.value.status_code == 422


def test_exam_is_locked_before_finishing_the_lessons(repo):
    with pytest.raises(HTTPException) as error:
        trail_service.TrailService.start_exam("u1", "modulo_1")
    assert error.value.status_code == 403


def test_trail_routes_require_authentication(client):
    assert client.get("/api/trail").status_code in (401, 403)
    assert client.post("/api/lessons/modulo_1_licao_1/complete").status_code in (401, 403)

import random
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set
from fastapi import HTTPException, status
from src.content.curriculum import Module, find_lesson, get_module, get_modules, questions_by_id
from src.repositories.progress_repository import ProgressRepository
from src.schemas.trail import (
    ExamNode,
    ExamQuestion,
    ExamQuestionResult,
    ExamResultResponse,
    ExamStartResponse,
    LessonNode,
    LessonResponse,
    Streak,
    TrailModule,
    TrailProgressSummary,
    TrailResponse,
)

# Brasil sem horário de verão desde 2019: UTC-3 fixo evita depender da base de fusos (tzdata)
BRAZIL_TZ = timezone(timedelta(hours=-3))


def today_in_brazil() -> date:
    return datetime.now(BRAZIL_TZ).date()


def compute_streak(activity_dates: Iterable[date], today: date) -> Streak:
    """Dias consecutivos com estudo. Sem atividade hoje, a sequência até ontem continua valendo até o fim do dia."""
    days = set(activity_dates)
    active_today = today in days
    cursor = today if active_today else today - timedelta(days=1)
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return Streak(current_days=count, active_today=active_today)


def build_trail(
    modules: Sequence[Module],
    completed_lessons: Set[str],
    attempts: List[Dict[str, Any]],
    streak: Streak,
) -> TrailResponse:
    """Status de cada módulo, lição e teste: lições em ordem, teste após as lições, módulo seguinte após aprovação."""
    passed_modules = {attempt["module_id"] for attempt in attempts if attempt.get("passed")}
    trail_modules: List[TrailModule] = []
    current_module_id: Optional[str] = None
    previous_passed = True

    for module in modules:
        unlocked = previous_passed
        module_passed = module.id in passed_modules
        lesson_nodes: List[LessonNode] = []
        previous_lesson_done = True
        for lesson in module.lessons:
            done = lesson.id in completed_lessons
            if not unlocked:
                lesson_status = "locked"
            elif done or module_passed:
                lesson_status = "completed"
            elif previous_lesson_done:
                lesson_status = "current"
            else:
                lesson_status = "locked"
            lesson_nodes.append(LessonNode(
                id=lesson.id,
                order=lesson.order,
                title=lesson.title,
                subtitle=lesson.subtitle,
                description=lesson.description,
                status=lesson_status,
            ))
            previous_lesson_done = lesson_status == "completed"

        module_attempts = [attempt for attempt in attempts if attempt["module_id"] == module.id]
        scores = [float(attempt["score"]) for attempt in module_attempts if attempt.get("score") is not None]
        if module_passed:
            exam_status = "completed"
        elif unlocked and all(node.status == "completed" for node in lesson_nodes):
            exam_status = "current"
        else:
            exam_status = "locked"

        if module_passed:
            module_status = "completed"
        elif unlocked:
            module_status = "current"
            current_module_id = current_module_id or module.id
        else:
            module_status = "locked"

        trail_modules.append(TrailModule(
            id=module.id,
            order=module.order,
            title=module.title,
            subtitle=module.subtitle,
            description=module.description,
            color=module.color,
            status=module_status,
            lessons=lesson_nodes,
            exam=ExamNode(
                status=exam_status,
                question_count=module.exam.question_count,
                pass_score=module.exam.pass_score,
                attempts=len(module_attempts),
                best_score=max(scores) if scores else None,
            ),
        ))
        previous_passed = module_passed

    completed = bool(modules) and all(module.status == "completed" for module in trail_modules)
    return TrailResponse(
        modules=trail_modules,
        streak=streak,
        progress=TrailProgressSummary(
            completed_lessons=sum(node.status == "completed" for module in trail_modules for node in module.lessons),
            total_lessons=sum(len(module.lessons) for module in trail_modules),
            completed_modules=sum(module.status == "completed" for module in trail_modules),
            total_modules=len(trail_modules),
        ),
        current_module_id=current_module_id,
        completed=completed,
    )


def grade_exam(module: Module, question_ids: List[str], answers: Dict[str, str]) -> List[ExamQuestionResult]:
    bank = questions_by_id(module)
    results = []
    for question_id in question_ids:
        question = bank[question_id]
        selected = answers.get(question_id)
        results.append(ExamQuestionResult(
            question_id=question.id,
            question=question.question,
            options=question.options,
            selected_option=selected,
            correct_option=question.correct_option,
            is_correct=selected == question.correct_option,
            explanation=question.explanation,
            source=question.source,
        ))
    return results


class TrailService:
    @staticmethod
    def get_trail(user_id: str) -> TrailResponse:
        return build_trail(
            get_modules(),
            ProgressRepository.list_completed_lessons(user_id),
            ProgressRepository.list_submitted_attempts(user_id),
            compute_streak(ProgressRepository.list_activity_dates(user_id), today_in_brazil()),
        )

    @staticmethod
    def _lesson_status(trail: TrailResponse, lesson_id: str) -> str:
        for module in trail.modules:
            for lesson in module.lessons:
                if lesson.id == lesson_id:
                    return lesson.status
        return "locked"

    @staticmethod
    def _module_or_404(module_id: str) -> Module:
        module = get_module(module_id)
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Módulo não encontrado.")
        return module

    @classmethod
    def get_lesson(cls, user_id: str, lesson_id: str) -> LessonResponse:
        found = find_lesson(lesson_id)
        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lição não encontrada.")
        if cls._lesson_status(cls.get_trail(user_id), lesson_id) == "locked":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conclua as etapas anteriores para acessar esta lição.")
        module, lesson = found
        return LessonResponse(
            id=lesson.id,
            module_id=module.id,
            title=lesson.title,
            subtitle=lesson.subtitle,
            slides=lesson.slides,
            chat_suggestions=lesson.chat_suggestions,
            quiz=lesson.quiz,
        )

    @classmethod
    def complete_lesson(cls, user_id: str, lesson_id: str) -> TrailResponse:
        found = find_lesson(lesson_id)
        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lição não encontrada.")
        if cls._lesson_status(cls.get_trail(user_id), lesson_id) == "locked":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conclua as etapas anteriores para acessar esta lição.")
        module, lesson = found
        ProgressRepository.mark_lesson_completed(user_id, lesson.id, module.id)
        ProgressRepository.record_activity(user_id, today_in_brazil())
        return cls.get_trail(user_id)

    @classmethod
    def start_exam(cls, user_id: str, module_id: str, rng: Optional[random.Random] = None) -> ExamStartResponse:
        module = cls._module_or_404(module_id)
        trail_module = next(item for item in cls.get_trail(user_id).modules if item.id == module_id)
        if trail_module.exam.status == "locked":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conclua as lições do módulo para liberar o teste final.")

        questions = (rng or random).sample(module.exam.questions, module.exam.question_count)
        attempt_id = ProgressRepository.create_attempt(user_id, module_id, [question.id for question in questions])
        return ExamStartResponse(
            attempt_id=attempt_id,
            module_id=module_id,
            pass_score=module.exam.pass_score,
            questions=[ExamQuestion(id=q.id, question=q.question, options=q.options) for q in questions],
        )

    @classmethod
    def submit_exam(cls, user_id: str, attempt_id: str, answers: Dict[str, str]) -> ExamResultResponse:
        attempt = ProgressRepository.get_attempt(user_id, attempt_id)
        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tentativa não encontrada.")
        if attempt.get("submitted_at"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta tentativa já foi enviada.")

        module = cls._module_or_404(attempt["module_id"])
        question_ids: List[str] = attempt["question_ids"]
        if set(answers) != set(question_ids):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Responda todas as questões do teste.")

        results = grade_exam(module, question_ids, answers)
        correct_count = sum(result.is_correct for result in results)
        score = correct_count / len(results)
        passed = score >= module.exam.pass_score

        ProgressRepository.submit_attempt(attempt_id, answers, score, passed)
        ProgressRepository.record_activity(user_id, today_in_brazil())
        return ExamResultResponse(
            module_id=module.id,
            score=score,
            correct_count=correct_count,
            total=len(results),
            passed=passed,
            pass_score=module.exam.pass_score,
            results=results,
            trail=cls.get_trail(user_id),
        )

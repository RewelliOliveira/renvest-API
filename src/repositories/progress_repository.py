from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Set
from src.core.database import get_supabase_client


class ProgressRepository:
    LESSONS_TABLE = "user_lesson_progress"
    ATTEMPTS_TABLE = "user_exam_attempts"
    ACTIVITY_TABLE = "user_activity_days"

    @classmethod
    def list_completed_lessons(cls, user_id: str) -> Set[str]:
        response = (
            get_supabase_client().table(cls.LESSONS_TABLE).select("lesson_id").eq("user_id", user_id).execute()
        )
        return {row["lesson_id"] for row in response.data}

    @classmethod
    def mark_lesson_completed(cls, user_id: str, lesson_id: str, module_id: str) -> None:
        # Refazer uma lição mantém a data da primeira conclusão
        get_supabase_client().table(cls.LESSONS_TABLE).upsert(
            {"user_id": user_id, "lesson_id": lesson_id, "module_id": module_id},
            on_conflict="user_id,lesson_id",
            ignore_duplicates=True,
        ).execute()

    @classmethod
    def record_activity(cls, user_id: str, day: date) -> None:
        get_supabase_client().table(cls.ACTIVITY_TABLE).upsert(
            {"user_id": user_id, "activity_date": day.isoformat()},
            on_conflict="user_id,activity_date",
            ignore_duplicates=True,
        ).execute()

    @classmethod
    def list_activity_dates(cls, user_id: str) -> Set[date]:
        response = (
            get_supabase_client().table(cls.ACTIVITY_TABLE).select("activity_date").eq("user_id", user_id).execute()
        )
        return {date.fromisoformat(row["activity_date"]) for row in response.data}

    @classmethod
    def list_submitted_attempts(cls, user_id: str) -> List[Dict[str, Any]]:
        response = (
            get_supabase_client()
            .table(cls.ATTEMPTS_TABLE)
            .select("module_id, score, passed")
            .eq("user_id", user_id)
            .not_.is_("submitted_at", "null")
            .execute()
        )
        return response.data

    @classmethod
    def create_attempt(cls, user_id: str, module_id: str, question_ids: List[str]) -> str:
        response = get_supabase_client().table(cls.ATTEMPTS_TABLE).insert(
            {"user_id": user_id, "module_id": module_id, "question_ids": question_ids}
        ).execute()
        if not response.data:
            raise RuntimeError("Falha ao registrar a tentativa do teste.")
        return response.data[0]["id"]

    @classmethod
    def get_attempt(cls, user_id: str, attempt_id: str) -> Optional[Dict[str, Any]]:
        response = (
            get_supabase_client()
            .table(cls.ATTEMPTS_TABLE)
            .select("*")
            .eq("id", attempt_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    @classmethod
    def submit_attempt(cls, attempt_id: str, answers: Dict[str, str], score: float, passed: bool) -> None:
        get_supabase_client().table(cls.ATTEMPTS_TABLE).update({
            "answers": answers,
            "score": round(score, 3),
            "passed": passed,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", attempt_id).execute()

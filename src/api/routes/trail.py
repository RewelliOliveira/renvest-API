from uuid import UUID
from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user
from src.schemas.auth import UserResponse
from src.schemas.trail import (
    ExamResultResponse,
    ExamStartResponse,
    ExamSubmitRequest,
    LessonResponse,
    TrailResponse,
)
from src.services.trail_service import TrailService

router = APIRouter(tags=["trail"])

@router.get("/trail", response_model=TrailResponse)
def get_trail(current_user: UserResponse = Depends(get_current_user)):
    return TrailService.get_trail(current_user.id)

@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(lesson_id: str, current_user: UserResponse = Depends(get_current_user)):
    return TrailService.get_lesson(current_user.id, lesson_id)

@router.post("/lessons/{lesson_id}/complete", response_model=TrailResponse)
def complete_lesson(lesson_id: str, current_user: UserResponse = Depends(get_current_user)):
    return TrailService.complete_lesson(current_user.id, lesson_id)

@router.post("/modules/{module_id}/exam", response_model=ExamStartResponse)
def start_exam(module_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Sorteia as questões do teste final e registra a tentativa (o gabarito não é enviado)."""
    return TrailService.start_exam(current_user.id, module_id)

@router.post("/exam-attempts/{attempt_id}/submit", response_model=ExamResultResponse)
def submit_exam(attempt_id: UUID, payload: ExamSubmitRequest, current_user: UserResponse = Depends(get_current_user)):
    return TrailService.submit_exam(current_user.id, str(attempt_id), payload.answers)

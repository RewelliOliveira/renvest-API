from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from src.content.curriculum import Question, QuestionOption, Slide, SourceRef

NodeStatus = Literal["completed", "current", "locked"]


class LessonNode(BaseModel):
    id: str
    order: int
    title: str
    subtitle: str
    description: str
    status: NodeStatus


class ExamNode(BaseModel):
    status: NodeStatus
    question_count: int
    pass_score: float
    attempts: int
    best_score: Optional[float] = None


class TrailModule(BaseModel):
    id: str
    order: int
    title: str
    subtitle: str
    description: str
    color: str
    status: NodeStatus
    lessons: List[LessonNode]
    exam: ExamNode


class Streak(BaseModel):
    current_days: int
    active_today: bool


class TrailProgressSummary(BaseModel):
    completed_lessons: int
    total_lessons: int
    completed_modules: int
    total_modules: int


class TrailResponse(BaseModel):
    modules: List[TrailModule]
    streak: Streak
    progress: TrailProgressSummary
    current_module_id: Optional[str] = None
    completed: bool


class LessonResponse(BaseModel):
    id: str
    module_id: str
    title: str
    subtitle: str
    slides: List[Slide]
    chat_suggestions: List[str]
    quiz: List[Question]


class ExamQuestion(BaseModel):
    id: str
    question: str
    options: List[QuestionOption]


class ExamStartResponse(BaseModel):
    attempt_id: str
    module_id: str
    pass_score: float
    questions: List[ExamQuestion]


class ExamSubmitRequest(BaseModel):
    answers: Dict[str, str] = Field(description="Alternativa escolhida para cada questão (id da questão -> id da alternativa)")


class ExamQuestionResult(BaseModel):
    question_id: str
    question: str
    options: List[QuestionOption]
    selected_option: Optional[str] = None
    correct_option: str
    is_correct: bool
    explanation: str
    source: SourceRef


class ExamResultResponse(BaseModel):
    module_id: str
    score: float
    correct_count: int
    total: int
    passed: bool
    pass_score: float
    results: List[ExamQuestionResult]
    trail: TrailResponse

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, model_validator

MODULES_DIR = Path(__file__).resolve().parent / "modules"


class SourceRef(BaseModel):
    document: str
    section: str
    institution: Optional[str] = None
    url: Optional[str] = None


class QuestionOption(BaseModel):
    id: str
    text: str


class Question(BaseModel):
    id: str
    question: str
    options: List[QuestionOption] = Field(min_length=2)
    correct_option: str
    explanation: str
    source: SourceRef

    @model_validator(mode="after")
    def correct_option_exists(self) -> "Question":
        if self.correct_option not in {option.id for option in self.options}:
            raise ValueError(f"Questão {self.id}: alternativa correta '{self.correct_option}' não existe")
        return self


class Slide(BaseModel):
    title: str
    text: str
    source: Optional[SourceRef] = None


class Lesson(BaseModel):
    id: str
    order: int
    title: str
    subtitle: str
    description: str
    slides: List[Slide] = Field(min_length=1)
    chat_suggestions: List[str] = Field(default_factory=list)
    quiz: List[Question] = Field(min_length=1)


class Exam(BaseModel):
    question_count: int = Field(gt=0)
    pass_score: float = Field(gt=0, le=1)
    questions: List[Question]

    @model_validator(mode="after")
    def enough_questions(self) -> "Exam":
        if len(self.questions) < self.question_count:
            raise ValueError("O banco do teste tem menos questões do que o teste sorteia")
        return self


class Module(BaseModel):
    id: str
    order: int
    title: str
    subtitle: str
    description: str
    color: str
    lessons: List[Lesson] = Field(min_length=1)
    exam: Exam


@lru_cache(maxsize=1)
def get_modules() -> Tuple[Module, ...]:
    """Módulos da trilha em ordem, lidos dos JSON revisados em src/content/modules/."""
    modules = [
        Module.model_validate(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(MODULES_DIR.glob("*.json"))
    ]
    modules.sort(key=lambda module: module.order)
    for module in modules:
        module.lessons.sort(key=lambda lesson: lesson.order)
    return tuple(modules)


def get_module(module_id: str) -> Optional[Module]:
    return next((module for module in get_modules() if module.id == module_id), None)


def find_lesson(lesson_id: str) -> Optional[Tuple[Module, Lesson]]:
    for module in get_modules():
        for lesson in module.lessons:
            if lesson.id == lesson_id:
                return module, lesson
    return None


def questions_by_id(module: Module) -> Dict[str, Question]:
    return {question.id: question for question in module.exam.questions}

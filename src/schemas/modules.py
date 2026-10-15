from typing import List
from pydantic import BaseModel

class StepItem(BaseModel):
    id: int
    text: str
    mascot: str

class ModuleResponse(BaseModel):
    id: str
    title: str
    description: str
    steps: List[StepItem]

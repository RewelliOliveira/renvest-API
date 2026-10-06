from typing import Optional, List, Dict
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    module: Optional[str] = "modulo_1"
    history: Optional[List[Dict[str, str]]] = None

class SourceResponse(BaseModel):
    document: str
    section: str
    institution: Optional[str] = None
    url: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    source: Optional[SourceResponse] = None

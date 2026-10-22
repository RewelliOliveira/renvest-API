from typing import Optional, List
from pydantic import BaseModel, Field

class ChatMessagePayload(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Mensagem do usuário para o Rev")
    module: Optional[str] = Field("modulo_1", description="Identificador do módulo atual de aprendizado")
    history: Optional[List[ChatMessagePayload]] = Field(None, description="Histórico prévio de mensagens da conversa")

class SourceResponse(BaseModel):
    document: str
    section: str
    institution: Optional[str] = None
    url: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    source: Optional[SourceResponse] = None
    sources: List[SourceResponse] = Field(default_factory=list, description="Fontes de todos os trechos recuperados, sem repetição")
    suggestions: List[str] = Field(default_factory=list, description="Sugestões contextuais de perguntas para continuidade")

class SuggestionsResponse(BaseModel):
    module: str
    suggestions: List[str]

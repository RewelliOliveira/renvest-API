from langchain_core.documents import Document

from src.agents import assistant
from src.tools.bcb_tools import mentions_selic

def test_sanitize_suggestions_cleans_and_limits():
    raw = ['1. "O que é CDB?"', "- O que é CDB?", "x" * 80, "Tesouro tem FGC?", "Extra"]
    cleaned = assistant.sanitize_suggestions(raw)
    assert cleaned[0] == "O que é CDB?"
    assert len(cleaned) == 3
    assert len(cleaned[1]) == 60

def test_sanitize_suggestions_falls_back_to_defaults():
    assert assistant.sanitize_suggestions([None, "  "]) == assistant.DEFAULT_SUGGESTIONS

def test_last_user_message_reads_dicts_and_models():
    class Turn:
        def __init__(self, role, content):
            self.role, self.content = role, content

    history = [{"role": "user", "content": "primeira"}, Turn("assistant", "resp"), Turn("user", "segunda")]
    assert assistant._last_user_message(history) == "segunda"

def test_chat_rag_handles_braces_and_returns_source(monkeypatch):
    doc = Document(page_content="FGC cobre R$ 250 mil.", metadata={"document": "Regulamento FGC", "url": "https://fgc.org.br"})
    monkeypatch.setattr(assistant, "query_relevant_documents", lambda *a, **k: [doc])
    monkeypatch.setattr(assistant, "get_selic_rate", lambda: None)

    class FakeOutput:
        reply = "Resposta"
        suggestions = ["Pergunta?"]

    class FakeRaw:
        usage_metadata = {"input_tokens": 120, "output_tokens": 30}

    class FakeLLM:
        def with_structured_output(self, _schema, include_raw=False):
            return lambda prompt_value: {"raw": FakeRaw(), "parsed": FakeOutput(), "parsing_error": None}

    captured = {}
    original = assistant.ChatPromptTemplate.from_messages

    def spy(messages):
        prompt = original(messages)
        captured["messages"] = prompt.invoke({"question": "q"}).to_messages()
        return prompt

    monkeypatch.setattr(assistant, "get_llm", lambda: FakeLLM())
    monkeypatch.setattr(assistant.ChatPromptTemplate, "from_messages", staticmethod(spy))

    result = assistant.chat_rag("Quanto o FGC cobre? {x}", history=[{"role": "user", "content": "use {chaves}"}])

    assert result["reply"] == "Resposta"
    assert result["source"]["document"] == "Regulamento FGC"
    assert result["sources"] == [result["source"]]
    assert any("{chaves}" in m.content for m in captured["messages"])

def _doc(document, section, url=None, content="trecho"):
    metadata = {"document": document, "section": section, "institution": "CVM"}
    if url:
        metadata["url"] = url
    return Document(page_content=content, metadata=metadata)

def test_build_sources_dedupes_and_keeps_each_url():
    docs = [
        _doc("Caderno CVM 6", "p. 12"),
        _doc("Resolução CVM 44", "p. 3", url="https://cvm.gov.br/res44.pdf"),
        _doc("Caderno CVM 6", "p. 12"),
    ]
    sources = assistant.build_sources(docs)
    assert [s["document"] for s in sources] == ["Caderno CVM 6", "Resolução CVM 44"]
    assert sources[0]["url"] == assistant.DEFAULT_SOURCE_URL
    assert sources[1]["url"] == "https://cvm.gov.br/res44.pdf"

def test_format_context_labels_each_excerpt():
    context = assistant.format_context([_doc("Caderno CVM 6", "p. 12", content="FII é um condomínio.")])
    assert context == "[Fonte: Caderno CVM 6 – CVM, p. 12]\nFII é um condomínio."

def test_chat_rag_without_docs_returns_no_sources(monkeypatch):
    monkeypatch.setattr(assistant, "query_relevant_documents", lambda *a, **k: [])
    monkeypatch.setattr(assistant, "generate", lambda *a, **k: {
        "reply": "Geral", "suggestions": [], "tokens_in": None, "tokens_out": None
    })
    result = assistant.chat_rag("Oi")
    assert result["source"] is None
    assert result["sources"] == []

def test_mentions_selic():
    assert mentions_selic("Quanto está a SELIC?")
    assert not mentions_selic("O que é FGC?")

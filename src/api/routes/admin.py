from typing import Callable, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import require_admin

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])

def load_ingestion() -> Optional[Callable[[], None]]:
    """A ingestão depende de PyMuPDF e dos PDFs, ausentes no deploy serverless; por isso é importada sob demanda."""
    try:
        from src.database.ingest import run_ingestion
    except ImportError:
        return None
    return run_ingestion

@router.post("/ingest")
def trigger_ingest():
    run_ingestion = load_ingestion()
    if run_ingestion is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ingestão indisponível neste ambiente. Execute `python main.py --ingest` localmente.",
        )
    run_ingestion()
    return {"status": "Ingestão executada com sucesso!"}

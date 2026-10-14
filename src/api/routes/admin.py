from fastapi import APIRouter, Depends
from src.api.dependencies import require_admin
from src.database.ingest import run_ingestion

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])

@router.post("/ingest")
def trigger_ingest():
    run_ingestion()
    return {"status": "Ingestão executada com sucesso!"}

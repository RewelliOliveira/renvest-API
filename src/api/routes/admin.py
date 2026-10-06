from fastapi import APIRouter
from src.database.ingest import run_ingestion

router = APIRouter(tags=["admin"])

@router.post("/ingest")
def trigger_ingest():
    run_ingestion()
    return {"status": "Ingestão executada com sucesso!"}

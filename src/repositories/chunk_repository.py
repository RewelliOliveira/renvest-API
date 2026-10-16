from typing import Any, Dict, Iterable, List, Optional
from src.core.database import get_supabase_client

PAGE_SIZE = 1000
DELETE_BATCH_SIZE = 200


class ChunkRepository:
    TABLE_NAME = "document_chunks"
    MATCH_FUNCTION = "match_document_chunks"

    @classmethod
    def upsert(cls, rows: List[Dict[str, Any]]) -> None:
        get_supabase_client().table(cls.TABLE_NAME).upsert(rows).execute()

    @classmethod
    def list_hashes(cls) -> Dict[str, Optional[str]]:
        """Mapa id -> hash do chunk gravado (None para chunks gravados antes do controle por hash)."""
        client = get_supabase_client()
        hashes: Dict[str, Optional[str]] = {}
        start = 0
        while True:
            response = (
                client.table(cls.TABLE_NAME)
                .select("id, chunk_hash:metadata->>chunk_hash")
                .order("id")
                .range(start, start + PAGE_SIZE - 1)
                .execute()
            )
            hashes.update((row["id"], row["chunk_hash"]) for row in response.data)
            if len(response.data) < PAGE_SIZE:
                return hashes
            start += PAGE_SIZE

    @classmethod
    def delete_ids(cls, ids: Iterable[str]) -> None:
        client = get_supabase_client()
        pending = sorted(ids)
        for start in range(0, len(pending), DELETE_BATCH_SIZE):
            batch = pending[start:start + DELETE_BATCH_SIZE]
            client.table(cls.TABLE_NAME).delete().in_("id", batch).execute()

    @classmethod
    def match(cls, embedding: List[float], match_count: int, module: Optional[str] = None) -> List[Dict[str, Any]]:
        response = get_supabase_client().rpc(
            cls.MATCH_FUNCTION,
            {"query_embedding": embedding, "match_count": match_count, "filter_module": module},
        ).execute()
        return response.data or []

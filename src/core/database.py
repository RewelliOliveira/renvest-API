from typing import Optional
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Retorna a instância singleton do cliente Supabase usando a chave de serviço (service_role).
    A chave de serviço opera exclusivamente no backend e possui privilégios de escrita seguros no PostgreSQL.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "Credenciais do Supabase não configuradas."
        )

    _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client

def is_supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

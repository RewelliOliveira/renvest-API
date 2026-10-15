import logging
import time
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# Série 432 do SGS/BCB: meta da Taxa Selic definida pelo Copom (% a.a.)
SELIC_META_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
SELIC_CACHE_TTL_SECONDS = 3600
SELIC_KEYWORDS = ("selic", "cdi", "copom", "taxa de juros", "taxa básica", "juros básicos")

_cache = {"value": None, "fetched_at": 0.0}

def mentions_selic(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in SELIC_KEYWORDS)

def get_selic_rate() -> Optional[str]:
    """Retorna a meta atual da Selic em texto (com cache de 1h) ou None se o BCB estiver indisponível."""
    now = time.monotonic()
    if _cache["value"] and now - _cache["fetched_at"] < SELIC_CACHE_TTL_SECONDS:
        return _cache["value"]

    try:
        response = httpx.get(SELIC_META_URL, timeout=5)
        response.raise_for_status()
        latest = response.json()[-1]
        value = (
            f"Meta da Taxa Selic definida pelo Copom: {latest['valor'].replace('.', ',')}% ao ano "
            f"(dado oficial do Banco Central, referência {latest['data']})."
        )
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        logger.warning("Não foi possível consultar a Selic no Banco Central", exc_info=True)
        return None

    _cache.update(value=value, fetched_at=now)
    return value

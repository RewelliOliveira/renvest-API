import threading
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Rate limiter em memória por janela deslizante (estado por processo/worker)."""

    def __init__(self, max_requests: int, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > self.window_seconds:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return False
            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def client_ip(request: Request) -> str:
    # X-Forwarded-For não é lido aqui pois pode ser forjado pelo cliente; atrás de um proxy
    # confiável, rode o uvicorn com --proxy-headers para que request.client reflita o IP real.
    return request.client.host if request.client else "unknown"


def enforce(limiter: SlidingWindowRateLimiter, key: str) -> None:
    if not limiter.hit(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições em pouco tempo. Aguarde um instante e tente novamente.",
        )


def ip_rate_limit(limiter: SlidingWindowRateLimiter, scope: str) -> Callable[[Request], None]:
    """Cria uma dependência FastAPI que limita requisições por IP dentro de um escopo."""

    def dependency(request: Request) -> None:
        enforce(limiter, f"{scope}:{client_ip(request)}")

    return dependency

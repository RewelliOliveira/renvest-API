# Ponto de entrada para a Vercel, que procura uma variável `app` em app.py na raiz do projeto.
# Localmente, a API continua sendo iniciada com `python main.py --serve`.
from src.api.server import app

__all__ = ["app"]

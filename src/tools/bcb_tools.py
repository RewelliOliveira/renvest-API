import requests
from langchain_core.tools import tool

@tool
def get_selic_rate() -> str:
    """Busca a taxa Selic acumulada recente diretamente do Sistema Gerenciador de Séries 
    Temporais (SGS) do Banco Central do Brasil.
    
    Returns:
        str: Dados recentes da taxa Selic formatados.
    """
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/5?formato=json"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return "Não foi possível conectar ao sistema do Banco Central no momento."
            
        data = response.json()
        lines = ["Últimos registros oficiais da Taxa Selic Diária (BCB):"]
        for item in data:
            lines.append(f"- Data: {item.get('data')} | Taxa: {item.get('valor')}% a.a.")
        return "\n".join(lines)
    except Exception as e:
        return f"Erro ao consultar taxa Selic no Banco Central: {str(e)}"

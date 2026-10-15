"""
Script de verificação e teste do fluxo de autenticação e conexão com Supabase.
Execute com:
    python scripts/test_auth_flow.py
"""

# .\venv\Scripts\python.exe scripts/test_auth_flow.py

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import is_supabase_configured, get_supabase_client
from src.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_local_security():
    print("\n--- [1/2] Testando Seguranca Local (bcrypt + PyJWT) ---")
    senha = "MinhaSenhaForte@2026"
    hash_gerado = hash_password(senha)
    print(f"[OK] Senha criptografada com sucesso (formato bcrypt): {hash_gerado[:25]}...")
    
    assert verify_password(senha, hash_gerado) is True, "Falha na validacao da senha correta"
    assert verify_password("senhaErrada", hash_gerado) is False, "Falha na rejeicao de senha incorreta"
    print("[OK] Validacao criptografica de senhas funcionando perfeitamente.")

    token = create_access_token({"sub": "teste-uuid", "email": "usuario@renvest.com.br"})
    payload = decode_access_token(token)
    assert payload is not None and payload["email"] == "usuario@renvest.com.br", "Falha na decodificacao do JWT"
    print("[OK] Geracao e validacao de tokens JWT funcionando perfeitamente.")

def test_supabase_connection():
    print("\n--- [2/2] Testando Conexao com Supabase ---")
    if not is_supabase_configured():
        print("[INFO] Supabase ainda nao configurado no .env")
        print("       Para conectar ao Supabase, preencha no seu arquivo .env:")
        print("       - SUPABASE_URL=https://seu-projeto.supabase.co")
        print("       - SUPABASE_SERVICE_ROLE_KEY=ey...")
        return

    try:
        client = get_supabase_client()
        res = client.table("users").select("count", count="exact").execute()
        print("[OK] Conexao com Supabase estabelecida com sucesso!")
        print(f"[OK] Tabela 'users' encontrada no banco. Total de usuarios registrados: {res.count}")
    except Exception as e:
        print(f"[ERRO] Falha ao comunicar com a tabela 'users' no Supabase: {e}")
        print("       Verifique se executou o script 'scripts/supabase_schema.sql' no SQL Editor do Supabase.")

if __name__ == "__main__":
    print("==================================================")
    print("   Renvest - Teste de Autenticacao e Supabase")
    print("==================================================")
    test_local_security()
    test_supabase_connection()
    print("\n[OK] Concluido com sucesso!\n")

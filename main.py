import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Renvest - RAG Finance Agent Backend")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Executa a indexação dos documentos Markdown no banco vetorial Chroma."
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Envia uma pergunta financeira de teste via CLI."
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Inicia uma sessão interativa de chat contínuo com histórico no terminal."
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Inicia o servidor de API FastAPI (porta 8000)."
    )

    args = parser.parse_args()

    if args.ingest:
        from src.database.ingest import run_ingestion
        run_ingestion()
    elif args.chat:
        from src.agents.assistant import chat_rag
        print("\n" + "=" * 60)
        print("   💬 Chat Interativo com o mascote Rev (Renvest)")
        print("   • Conversa contínua com histórico em memória.")
        print("   • Digite 'sair', 'exit' ou 'q' para encerrar a sessão.")
        print("=" * 60 + "\n")
        history = []
        while True:
            try:
                user_input = input("Você: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nRev: Até logo! Bons estudos e cuide bem do seu bolso! 🚀💰\n")
                break
                
            if not user_input:
                continue
            if user_input.lower() in ["sair", "exit", "q"]:
                print("\nRev: Até mais! Bons estudos e cuide bem do seu bolso! 🚀💰\n")
                break
                
            res = chat_rag(user_input, module="modulo_1", history=history)
            reply = res.get("reply", "")
            print(f"\nRev: {reply}\n")
            
            src = res.get("source")
            if src:
                print(f"   🏛️ [Fonte Oficial: {src.get('institution')} - {src.get('document')}]")
                print(f"   🔗 [Link: {src.get('url')}]\n")
            
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})
    elif args.query:
        from src.agents.assistant import chat_rag
        print(f"\n[Rev] Processando dúvida: '{args.query}'...\n")
        res = chat_rag(args.query, module="modulo_1")
        print("\n--- RESPOSTA DO MASCOTE REV ---")
        print(res.get("reply"))
        src = res.get("source")
        if src:
            print("\n--- FONTE OFICIAL CITADA ---")
            print(f"Documento: {src.get('document')}")
            print(f"Seção: {src.get('section')}")
            print(f"Instituição: {src.get('institution')}")
            print(f"URL: {src.get('url')}\n")
        else:
            print("\n--- NENHUMA FONTE CITADA (Fora de escopo ou conversa geral) ---\n")
    else:
        print("\n🚀 Iniciando servidor FastAPI do Renvest em http://localhost:8000...")
        uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
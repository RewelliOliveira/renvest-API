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
        "--serve",
        action="store_true",
        help="Inicia o servidor de API FastAPI (porta 8000)."
    )

    args = parser.parse_args()

    if args.ingest:
        from src.database.ingest import run_ingestion
        run_ingestion()
    elif args.query:
        from src.agents.assistant import chat_rag
        print(f"\n[Rev] Processando dúvida: '{args.query}'...\n")
        res = chat_rag(args.query, module="modulo_1")
        print("\n--- RESPOSTA DO MASCOTE REV ---")
        print(res.get("reply"))
        print("\n--- FONTE OFICIAL CITADA ---")
        src = res.get("source", {})
        print(f"Documento: {src.get('document')}")
        print(f"Seção: {src.get('section')}")
        print(f"Instituição: {src.get('institution')}")
        print(f"URL: {src.get('url')}\n")
    else:
        print("\n🚀 Iniciando servidor FastAPI do Renvest em http://localhost:8000...")
        uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
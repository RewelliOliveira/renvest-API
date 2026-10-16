-- ==============================================================================
-- RENVEST - Banco vetorial do corpus RAG (Supabase PostgreSQL + pgvector)
-- ==============================================================================
-- Instruções:
-- 1. Abra o painel do projeto no Supabase (o mesmo usado pela tabela de usuários)
-- 2. No menu lateral, acesse "SQL Editor"
-- 3. Cole este script e clique em "Run" (pode ser executado mais de uma vez)
-- ==============================================================================

-- 1. Extensão pgvector (tipo "vector" e operadores de distância)
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- 2. Tabela de chunks: um registro por trecho indexado do corpus
--    id segue o padrão "<doc_id>:<índice>" gerado pela ingestão (reingestão idempotente)
--    embedding com 1536 dimensões = text-embedding-3-small da OpenAI
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    module TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding extensions.vector(1536) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_module ON public.document_chunks (module);
CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id ON public.document_chunks (doc_id);

-- Índice aproximado (HNSW) para distância de cosseno.
-- Com ~10 mil chunks a busca exata (sem índice) é rápida e devolve sempre os vizinhos corretos,
-- o que é desejável na avaliação do TCC. Crie o índice apenas se o corpus crescer muito:
-- CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
--     ON public.document_chunks USING hnsw (embedding extensions.vector_cosine_ops);

-- 3. Row Level Security: sem políticas públicas. Apenas o backend (service_role) lê e grava.
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;

-- 4. Busca por similaridade (distância de cosseno: 0 = idêntico, 1 = sem relação)
--    filter_module NULL busca no corpus inteiro
CREATE OR REPLACE FUNCTION public.match_document_chunks(
    query_embedding extensions.vector(1536),
    match_count INT DEFAULT 3,
    filter_module TEXT DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    doc_id TEXT,
    module TEXT,
    content TEXT,
    metadata JSONB,
    distance DOUBLE PRECISION
)
LANGUAGE sql
STABLE
SET search_path = public, extensions
AS $$
    SELECT c.id, c.doc_id, c.module, c.content, c.metadata,
           c.embedding <=> query_embedding AS distance
    FROM public.document_chunks AS c
    WHERE filter_module IS NULL OR c.module = filter_module
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- A função só pode ser chamada pelo backend (service_role), nunca pela chave pública (anon)
REVOKE EXECUTE ON FUNCTION public.match_document_chunks(extensions.vector, INT, TEXT) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.match_document_chunks(extensions.vector, INT, TEXT) TO service_role;

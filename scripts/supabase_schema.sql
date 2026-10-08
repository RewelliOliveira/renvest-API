-- ==============================================================================
-- RENVEST - Esquema de Banco de Dados para Usuários (Supabase PostgreSQL)
-- ==============================================================================
-- Instruções:
-- 1. Abra o painel do seu projeto no Supabase (https://supabase.com/dashboard)
-- 2. No menu lateral, acesse "SQL Editor"
-- 3. Cole este script e clique em "Run"
-- ==============================================================================

-- 1. Extensão para UUID (caso ainda não esteja ativada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tabela de Usuários Limpa e Otimizada
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT, -- Nulo para usuários autenticados unicamente via Google
    picture TEXT,
    auth_provider TEXT NOT NULL DEFAULT 'local', -- 'local' ou 'google'
    google_id TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. Índices para performance nas consultas de login e identificação
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users (lower(email));
CREATE INDEX IF NOT EXISTS idx_users_google_id ON public.users (google_id);

-- 4. Row Level Security (RLS)
-- Como a autenticação é processada com segurança pelo backend FastAPI (usando a service_role key),
-- ativamos RLS sem políticas públicas para impedir qualquer leitura ou alteração anônima não autorizada.
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- 5. Trigger para atualização automática da coluna updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

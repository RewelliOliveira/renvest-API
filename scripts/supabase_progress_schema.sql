-- ==============================================================================
-- RENVEST - Progresso na trilha e ofensiva (Supabase PostgreSQL)
-- ==============================================================================
-- Instruções:
-- 1. Execute antes o scripts/supabase_schema.sql (tabela public.users)
-- 2. No SQL Editor do Supabase, cole este script e clique em "Run" (pode ser executado mais de uma vez)
-- ==============================================================================

-- 1. Lições concluídas (uma linha por usuário e lição; refazer a lição não duplica)
CREATE TABLE IF NOT EXISTS public.user_lesson_progress (
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    lesson_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (user_id, lesson_id)
);

-- 2. Tentativas do teste final. As questões sorteadas ficam registradas no início da tentativa,
--    e a correção é feita no backend, sem expor o gabarito ao navegador.
CREATE TABLE IF NOT EXISTS public.user_exam_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    module_id TEXT NOT NULL,
    question_ids TEXT[] NOT NULL,
    answers JSONB,
    score NUMERIC(4, 3),
    passed BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    submitted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_user_exam_attempts_user_module ON public.user_exam_attempts (user_id, module_id);

-- 3. Dias com atividade de estudo (base da ofensiva). A data é a do fuso de Brasília.
CREATE TABLE IF NOT EXISTS public.user_activity_days (
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    activity_date DATE NOT NULL,
    PRIMARY KEY (user_id, activity_date)
);

-- 4. Row Level Security: sem políticas públicas. Apenas o backend (service_role) lê e grava.
ALTER TABLE public.user_lesson_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_exam_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_activity_days ENABLE ROW LEVEL SECURITY;

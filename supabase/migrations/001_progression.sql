-- Progress of each learner, one row per session (séance).
-- Run once in the Supabase SQL editor of the parcours-actuariel project (see docs/SUPABASE.md).
-- Row Level Security: every learner can only read and write their own rows.

create table if not exists public.progression (
  user_id    uuid        not null default auth.uid() references auth.users (id) on delete cascade,
  seance_id  text        not null check (seance_id ~ '^[a-z0-9+-]{2,20}/s[0-9]{2}$'),
  etapes     jsonb       not null default '{}'::jsonb check (jsonb_typeof(etapes) = 'object'),
  code       text        check (char_length(code) <= 20000),
  code_at    timestamptz,
  updated_at timestamptz not null default now(),
  primary key (user_id, seance_id)
);

alter table public.progression enable row level security;

drop policy if exists "own rows: select" on public.progression;
drop policy if exists "own rows: insert" on public.progression;
drop policy if exists "own rows: update" on public.progression;
drop policy if exists "own rows: delete" on public.progression;
create policy "own rows: select" on public.progression for select to authenticated using ((select auth.uid()) = user_id);
create policy "own rows: insert" on public.progression for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "own rows: update" on public.progression for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own rows: delete" on public.progression for delete to authenticated using ((select auth.uid()) = user_id);

revoke all on public.progression from anon;
grant select, insert, update, delete on public.progression to authenticated;

-- A learner can delete their own account; their progress goes with it (on delete cascade).
create or replace function public.supprimer_mon_compte()
returns void
language sql
security definer
set search_path = ''
as $$
  delete from auth.users where id = auth.uid();
$$;

revoke all on function public.supprimer_mon_compte() from public, anon;
grant execute on function public.supprimer_mon_compte() to authenticated;

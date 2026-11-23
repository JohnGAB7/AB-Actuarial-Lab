-- Row Level Security test for public.progression: two learners, A and B, and an anonymous visitor.
-- Run after supabase_stub.sql and the migrations, with psql -v ON_ERROR_STOP=1. Any failed check raises an exception.
\set A '11111111-1111-1111-1111-111111111111'
\set B '22222222-2222-2222-2222-222222222222'
insert into auth.users (id, email) values (:'A', 'a@example.com'), (:'B', 'b@example.com');

-- A writes a row.
set role authenticated;
select set_config('request.jwt.claim.sub', :'A', false);
insert into public.progression (seance_id, etapes) values ('a1/s01', '{"0": true}');
do $$ begin
  if (select count(*) from public.progression) <> 1 then raise exception 'A must see their own row'; end if;
end $$;

-- A cannot write a row in B's name.
do $$ begin
  begin
    insert into public.progression (user_id, seance_id) values ('22222222-2222-2222-2222-222222222222', 'a1/s01');
    raise exception 'A was able to insert a row for B';
  exception when insufficient_privilege then null;
  end;
end $$;

-- B sees nothing of A, and cannot change or delete A's row.
select set_config('request.jwt.claim.sub', :'B', false);
do $$
declare n int;
begin
  if (select count(*) from public.progression) <> 0 then raise exception 'B can read A''s rows'; end if;
  update public.progression set etapes = '{}' where seance_id = 'a1/s01';
  get diagnostics n = row_count;
  if n <> 0 then raise exception 'B updated A''s row'; end if;
  delete from public.progression where seance_id = 'a1/s01';
  get diagnostics n = row_count;
  if n <> 0 then raise exception 'B deleted A''s row'; end if;
end $$;

-- A cannot move their row to B.
select set_config('request.jwt.claim.sub', :'A', false);
do $$ begin
  begin
    update public.progression set user_id = '22222222-2222-2222-2222-222222222222';
    raise exception 'A was able to hand a row over to B';
  exception when insufficient_privilege then null;
  end;
end $$;

-- Content checks: bad session id and oversized code are refused.
do $$ begin
  begin
    insert into public.progression (seance_id) values ('../etc');
    raise exception 'invalid seance_id accepted';
  exception when check_violation then null;
  end;
  begin
    insert into public.progression (seance_id, code) values ('a1/s02', repeat('x', 20001));
    raise exception 'oversized code accepted';
  exception when check_violation then null;
  end;
end $$;

-- Anonymous visitors cannot read or write.
reset role;
set role anon;
select set_config('request.jwt.claim.sub', '', false);
do $$ begin
  begin
    perform 1 from public.progression;
    raise exception 'anon can read progression';
  exception when insufficient_privilege then null;
  end;
  begin
    perform public.supprimer_mon_compte();
    raise exception 'anon can call supprimer_mon_compte';
  exception when insufficient_privilege then null;
  end;
end $$;

-- B deletes their own account: A and A's progress are untouched.
reset role;
set role authenticated;
select set_config('request.jwt.claim.sub', :'B', false);
select public.supprimer_mon_compte();
reset role;
do $$ begin
  if exists (select 1 from auth.users where id = '22222222-2222-2222-2222-222222222222') then raise exception 'B still exists'; end if;
  if not exists (select 1 from auth.users where id = '11111111-1111-1111-1111-111111111111') then raise exception 'A was deleted'; end if;
  if (select count(*) from public.progression) <> 1 then raise exception 'A''s progress was touched'; end if;
end $$;

-- A deletes their account: their progress goes with it.
set role authenticated;
select set_config('request.jwt.claim.sub', :'A', false);
select public.supprimer_mon_compte();
reset role;
do $$ begin
  if (select count(*) from public.progression) <> 0 then raise exception 'progress survived account deletion'; end if;
end $$;

select 'RLS OK' as resultat;

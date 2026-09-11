-- AdeImmo, fonctions utilitaires pour le RBAC en base.
-- A executer sur le projet Supabase apres la migration Alembic initiale.

-- Role applicatif de l'utilisateur courant.
-- SECURITY DEFINER : la fonction lit public.users en contournant RLS, ce qui
-- evite une recursion infinie quand elle est appelee depuis une policy de
-- cette meme table.
create or replace function public.app_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select u.role from public.users u where u.id = auth.uid();
$$;

revoke execute on function public.app_role() from anon;
grant execute on function public.app_role() to authenticated;

-- Recopie le role dans le JWT (app_metadata) a chaque creation ou changement.
-- Le JWT n'est utilise que par les policies et le frontend pour afficher ou
-- masquer des actions. L'API, elle, relit toujours public.users.
create or replace function public.sync_user_role_to_auth()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  update auth.users
     set raw_app_meta_data = coalesce(raw_app_meta_data, '{}'::jsonb)
                             || jsonb_build_object('role', new.role)
   where id = new.id;
  return new;
end;
$$;

drop trigger if exists trg_sync_user_role on public.users;
create trigger trg_sync_user_role
  after insert or update of role on public.users
  for each row
  execute function public.sync_user_role_to_auth();

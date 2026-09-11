-- AdeImmo, policies RLS.
-- Deuxieme barriere apres les dependances FastAPI : meme si une requete atteint
-- la base avec un JWT utilisateur, elle reste limitee au perimetre du role.
--
-- admin     : acces total
-- agent     : biens, photos, baux, tickets
-- comptable : paiements, lecture des biens et des baux pour le rapprochement

alter table public.users enable row level security;
alter table public.properties enable row level security;
alter table public.property_photos enable row level security;
alter table public.leases enable row level security;
alter table public.payments enable row level security;
alter table public.maintenance_tickets enable row level security;

-- --- users ----------------------------------------------------------------
drop policy if exists users_select on public.users;
create policy users_select on public.users
  for select to authenticated
  using (id = auth.uid() or public.app_role() = 'admin');

drop policy if exists users_write on public.users;
create policy users_write on public.users
  for all to authenticated
  using (public.app_role() = 'admin')
  with check (public.app_role() = 'admin');

-- --- properties -----------------------------------------------------------
drop policy if exists properties_select on public.properties;
create policy properties_select on public.properties
  for select to authenticated
  using (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists properties_insert on public.properties;
create policy properties_insert on public.properties
  for insert to authenticated
  with check (public.app_role() in ('admin', 'agent'));

drop policy if exists properties_update on public.properties;
create policy properties_update on public.properties
  for update to authenticated
  using (public.app_role() in ('admin', 'agent'))
  with check (public.app_role() in ('admin', 'agent'));

drop policy if exists properties_delete on public.properties;
create policy properties_delete on public.properties
  for delete to authenticated
  using (public.app_role() = 'admin');

-- --- property_photos ------------------------------------------------------
drop policy if exists property_photos_select on public.property_photos;
create policy property_photos_select on public.property_photos
  for select to authenticated
  using (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists property_photos_write on public.property_photos;
create policy property_photos_write on public.property_photos
  for all to authenticated
  using (public.app_role() in ('admin', 'agent'))
  with check (public.app_role() in ('admin', 'agent'));

-- --- leases ---------------------------------------------------------------
drop policy if exists leases_select on public.leases;
create policy leases_select on public.leases
  for select to authenticated
  using (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists leases_write on public.leases;
create policy leases_write on public.leases
  for all to authenticated
  using (public.app_role() in ('admin', 'agent'))
  with check (public.app_role() in ('admin', 'agent'));

-- --- payments -------------------------------------------------------------
drop policy if exists payments_select on public.payments;
create policy payments_select on public.payments
  for select to authenticated
  using (public.app_role() in ('admin', 'comptable'));

drop policy if exists payments_write on public.payments;
create policy payments_write on public.payments
  for all to authenticated
  using (public.app_role() in ('admin', 'comptable'))
  with check (public.app_role() in ('admin', 'comptable'));

-- --- maintenance_tickets --------------------------------------------------
drop policy if exists maintenance_select on public.maintenance_tickets;
create policy maintenance_select on public.maintenance_tickets
  for select to authenticated
  using (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists maintenance_insert on public.maintenance_tickets;
create policy maintenance_insert on public.maintenance_tickets
  for insert to authenticated
  with check (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists maintenance_update on public.maintenance_tickets;
create policy maintenance_update on public.maintenance_tickets
  for update to authenticated
  using (public.app_role() in ('admin', 'agent'))
  with check (public.app_role() in ('admin', 'agent'));

drop policy if exists maintenance_delete on public.maintenance_tickets;
create policy maintenance_delete on public.maintenance_tickets
  for delete to authenticated
  using (public.app_role() = 'admin');

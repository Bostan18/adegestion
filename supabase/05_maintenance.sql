-- AdeImmo, tables et bucket ajoutes par la migration 0003.
-- A executer apres `alembic upgrade head`, une fois la migration 0003 appliquee.

-- --- Prestataires ---------------------------------------------------------
alter table public.contractors enable row level security;

drop policy if exists contractors_select on public.contractors;
create policy contractors_select on public.contractors
  for select to authenticated
  using (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists contractors_write on public.contractors;
create policy contractors_write on public.contractors
  for all to authenticated
  using (public.app_role() in ('admin', 'agent'))
  with check (public.app_role() in ('admin', 'agent'));

-- --- Photos de maintenance ------------------------------------------------
alter table public.maintenance_photos enable row level security;

drop policy if exists maintenance_photos_select on public.maintenance_photos;
create policy maintenance_photos_select on public.maintenance_photos
  for select to authenticated
  using (public.app_role() in ('admin', 'agent', 'comptable'));

drop policy if exists maintenance_photos_write on public.maintenance_photos;
create policy maintenance_photos_write on public.maintenance_photos
  for all to authenticated
  using (public.app_role() in ('admin', 'agent'))
  with check (public.app_role() in ('admin', 'agent'));

-- --- Bucket des photos de maintenance -------------------------------------
-- Bucket distinct de celui des biens : les volumes et la duree de
-- conservation n'ont rien a voir, et les policies pourront diverger.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'maintenance-photos',
  'maintenance-photos',
  false,
  5242880, -- 5 Mo, les images sont compressees par le navigateur avant envoi
  array['image/jpeg', 'image/png', 'image/webp', 'image/avif']
)
on conflict (id) do update
  set public = excluded.public,
      file_size_limit = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists maintenance_photos_read on storage.objects;
create policy maintenance_photos_read on storage.objects
  for select to authenticated
  using (
    bucket_id = 'maintenance-photos'
    and public.app_role() in ('admin', 'agent', 'comptable')
  );

drop policy if exists maintenance_photos_upload on storage.objects;
create policy maintenance_photos_upload on storage.objects
  for all to authenticated
  using (bucket_id = 'maintenance-photos' and public.app_role() in ('admin', 'agent'))
  with check (bucket_id = 'maintenance-photos' and public.app_role() in ('admin', 'agent'));

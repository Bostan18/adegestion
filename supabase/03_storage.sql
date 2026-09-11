-- AdeImmo, bucket des photos de biens.
-- Bucket prive : la lecture passe par des URLs signees generees par l'API.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'property-photos',
  'property-photos',
  false,
  5242880, -- 5 Mo, les images sont compressees par le navigateur avant envoi
  array['image/jpeg', 'image/png', 'image/webp', 'image/avif']
)
on conflict (id) do update
  set public = excluded.public,
      file_size_limit = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists property_photos_read on storage.objects;
create policy property_photos_read on storage.objects
  for select to authenticated
  using (
    bucket_id = 'property-photos'
    and public.app_role() in ('admin', 'agent', 'comptable')
  );

drop policy if exists property_photos_write on storage.objects;
create policy property_photos_write on storage.objects
  for all to authenticated
  using (bucket_id = 'property-photos' and public.app_role() in ('admin', 'agent'))
  with check (bucket_id = 'property-photos' and public.app_role() in ('admin', 'agent'));

# Configuration Supabase

Scripts a executer dans le SQL Editor du projet Supabase, dans cet ordre, apres
avoir applique la migration Alembic (`alembic upgrade head` avec `DATABASE_URL`
pointant sur Supabase).

| Fichier | Role |
|---|---|
| `01_role_helpers.sql` | Fonction `app_role()` et trigger de synchronisation du role vers le JWT |
| `02_rls_policies.sql` | Policies RLS par table et par role |
| `03_storage.sql` | Bucket prive `property-photos` et policies Storage |
| `04_seed_first_admin.sql.example` | Modele pour creer le premier administrateur |

## Ordre complet d'installation

```bash
# 1. Tables
cd backend
DATABASE_URL="postgresql+psycopg://postgres.<ref>:<password>@aws-0-eu-north-1.pooler.supabase.com:5432/postgres" \
  alembic upgrade head

# 2. Scripts SQL 01 a 03 dans le SQL Editor Supabase

# 3. Premier admin : creer le compte dans Authentication > Users,
#    puis executer une copie adaptee de 04_seed_first_admin.sql.example
```

## Note sur les paiements

Les policies `payments_select` et `payments_write` limitent la table aux roles
`admin` et `comptable`, ce qui correspond exactement au RBAC de l'API. Aucune
modification n'est necessaire apres la migration `0002`.

## Pourquoi une double securite

Les dependances FastAPI (`require_roles`) bloquent les appels a l'API. Les
policies RLS protegent la base si une requete l'atteint autrement, par exemple
depuis le client Supabase du navigateur. Les deux lisent la meme source de
verite : la colonne `role` de `public.users`, recopiee dans le JWT par le
trigger `trg_sync_user_role`.

Un changement de role ne prend effet dans le JWT qu'au rafraichissement de la
session. L'API, elle, relit la base a chaque requete et applique donc le
nouveau role immediatement.

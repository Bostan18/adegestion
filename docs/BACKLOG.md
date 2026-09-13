# Backlog AdeImmo

Points identifiés et volontairement reportés. À traiter au moment indiqué,
pas avant.

## À faire avant de clore le module Biens

### Valider le module contre le vrai projet Supabase

**Qui** : Ahmed (nécessite les clés du projet Supabase).
**Pourquoi** : tout a été vérifié en local (tests sur SQLite, migration jouée
sur un PostgreSQL 16, policies RLS testées fonctionnellement, écrans capturés
sur l'application réelle), mais le module n'a jamais tourné contre le vrai
projet Supabase à Stockholm.

Procédure :

1. Créer le projet Supabase, récupérer l'URL, l'anon key, la service role key
   et le JWT secret.
2. `cd backend && DATABASE_URL="<uri Supabase>" alembic upgrade head`
3. Exécuter `supabase/01_role_helpers.sql`, `02_rls_policies.sql` et
   `03_storage.sql` dans le SQL Editor.
4. Créer le compte admin dans Authentication > Users, puis exécuter une copie
   adaptée de `supabase/04_seed_first_admin.sql.example`.
5. Renseigner `backend/.env` et `frontend/.env.local`, puis `docker compose up`.

Points à vérifier en particulier, car ils ne sont pas couverts localement :

- la clé étrangère `public.users.id` vers `auth.users.id`, que la migration
  n'ajoute que si le schéma `auth` existe ;
- le trigger `trg_sync_user_role`, qui recopie le rôle dans le JWT ;
- l'upload réel d'une photo vers le bucket `property-photos`, de bout en bout
  (URL signée, envoi direct depuis le navigateur, URL de lecture signée).

## À faire avant la première mise en ligne sur Render

### Ajouter `sharp` au frontend

Next.js signale son absence au démarrage en production. Sans lui,
l'optimisation des images passe par une implémentation WebAssembly nettement
plus lente, ce qui se voit sur la liste des biens dès qu'il y a des photos.
Une ligne dans `frontend/package.json`, à ajouter en même temps que le reste
de la configuration de déploiement.

### Reprendre le Dockerfile du backend pour la production

Le `backend/Dockerfile` actuel est orienté développement : il installe les
dépendances de test et démarre uvicorn en rechargement automatique via
`docker-compose.yml`. Pour Render, il faut une image sans `[dev]`, un nombre
de workers explicite et le health check branché sur `/health`.

## Idées notées, non planifiées

- Export CSV des paiements par période, pour le rapprochement bancaire
  (mentionné dans `docs/ARCHITECTURE.md` comme à prévoir dès le MVP du module
  Paiements).
- Pagination côté API sur les photos d'un bien, si un bien dépasse la
  vingtaine de photos. Aujourd'hui elles sont toutes chargées d'un coup.

# AdeImmo

Application de gestion immobiliere pour une agence en Cote d'Ivoire.
Backend FastAPI, frontend Next.js 14, base de donnees et authentification Supabase.

Le contexte fonctionnel est dans [`CLAUDE.md`](CLAUDE.md), les choix techniques
dans [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), le schema de reference dans
[`docs/schema.sql`](docs/schema.sql).

## Structure

```
backend/     API FastAPI, modeles SQLAlchemy, migrations Alembic, tests
frontend/    Next.js 14 App Router, TypeScript, Tailwind, shadcn/ui
supabase/    Policies RLS, triggers et configuration du Storage
docs/        Architecture et schema de base de donnees
```

## Demarrage rapide

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# renseigner les cles Supabase dans les deux fichiers

docker compose up --build
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Documentation OpenAPI | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| PostgreSQL local | localhost:5432 |

## Developpement sans Docker

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest              # base SQLite temporaire, aucun appel reseau
ruff check .
```

## Configuration Supabase

Voir [`supabase/README.md`](supabase/README.md) : migration des tables, policies
RLS, bucket de photos et creation du premier administrateur.

## Etat d'avancement

| Module | Etat |
|---|---|
| Auth et roles | Fait |
| Biens (properties) et photos | Fait |
| Baux (leases) | Modele et migration seulement |
| Paiements (payments) | Modele et migration seulement |
| Maintenance (maintenance_tickets) | Modele et migration seulement |

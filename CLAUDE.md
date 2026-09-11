# AdeImmo, contexte projet

## Résumé

AdeImmo est une application web de gestion immobilière destinée à une seule agence immobilière en Côte d'Ivoire (4 à 10 utilisateurs simultanés). Le projet est développé en solo par Ahmed TIMITE, à la fois pour aider un ami (l'agence) et comme vitrine de compétences (Chef de Projet IT en repositionnement, portfolio data/dev).

## Utilisateurs cibles

Une seule agence, avec 3 rôles :
- **admin** : accès total (biens, baux, paiements, utilisateurs)
- **agent** : gestion des biens et des baux
- **comptable** : gestion des paiements uniquement

## Stack technique

- **Backend** : FastAPI (Python)
- **Frontend** : Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Base de données** : Supabase (PostgreSQL), Stockholm (eu-north-1)
- **Auth** : Supabase Auth
- **Storage** : Supabase Storage (photos des biens)
- **Déploiement** : Render

## Conventions de développement

- Langue du code : anglais (noms de tables, colonnes, fonctions, variables)
- Langue de l'interface utilisateur : français
- Commits : conventionnels (`feat:`, `fix:`, `chore:`, `docs:`)
- RBAC appliqué à la fois côté API (dépendances FastAPI) et côté base (policies RLS Supabase), en double sécurité
- Pas de multi-tenant : une seule agence, donc pas de colonne `agency_id`

## Modules fonctionnels (ordre de développement)

1. Auth et gestion des utilisateurs (rôles)
2. Biens immobiliers (properties) + photos
3. Baux (leases)
4. Paiements (payments), avec méthodes espèces, virement, chèque, Mobile Money (Orange, MTN, Moov), Wave
5. Tickets de maintenance (maintenance_tickets)

## Points d'attention spécifiques

- Les paiements par chèque doivent tracer un `reference_number` et permettre un statut `rejete` (chèque sans provision)
- Les photos de biens doivent être compressées à l'upload (éviter de saturer le Storage Supabase)
- Le rapprochement bancaire (virements, chèques) est une fonctionnalité à prévoir même si elle n'est pas prioritaire au MVP

## Ce que Claude Code ne doit pas faire sans validation

- Ne pas introduire de multi-tenant ou de colonne `agency_id` (hors sujet pour ce projet)
- Ne pas choisir une autre base de données que Supabase/PostgreSQL sans en discuter
- Ne pas committer de secrets ou clés API en dur dans le code

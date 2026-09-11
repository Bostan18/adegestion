# AdeImmo, architecture

## Contexte

Application de gestion immobilière pour une seule agence en Côte d'Ivoire. Projet solo, aussi pensé comme vitrine de compétences. 4 à 10 utilisateurs simultanés.

## Style architectural

Client/Server en couches (Layered), monolithe API au départ. Pas de multi-tenant (une seule agence), pas de microservices (sur-ingénierie pour ce contexte).

## Composants

| Composant | Rôle |
|---|---|
| Next.js (App Router) | Frontend : dashboard, fiches biens, gestion des baux et paiements |
| FastAPI | API métier : biens, baux, paiements, RBAC |
| Supabase (PostgreSQL) | Données, Auth, Storage (photos) |

## RBAC

Trois rôles : admin (accès total), agent (biens et baux), comptable (paiements). Appliqué en double sécurité, côté API (dépendances FastAPI) et côté base (policies RLS Supabase).

## Alternatives écartées

- **FastAPI + HTMX + Alpine.js** : plus rapide à développer seul, mais moins adapté à l'objectif de vitrine de compétences (moins impressionnant qu'un stack Next.js/TypeScript pour un portfolio)
- **PostgreSQL auto-hébergé (OVHcloud)** : plus de contrôle, mais plus de charge opérationnelle solo (backups, auth à gérer soi-même). Supabase reste plus rapide à mettre en œuvre pour ce contexte
- **SQLite** : insuffisant pour 4 à 10 utilisateurs avec des écritures concurrentes (paiements, mises à jour de biens en simultané)

## Risques et mitigations

| Risque | Mitigation |
|---|---|
| Confusion entre rôles (comptable qui modifie un bien) | RBAC strict, testé dès le MVP |
| Volumétrie photos | Compression à l'upload |
| Chèques sans provision | Statut `rejete` + `reference_number` traçable dans `payments` |
| Rapprochement bancaire manuel | Prévoir un export (CSV) des paiements par période dès le MVP |

## Ordre de développement recommandé

1. Auth + rôles
2. Biens (properties + photos)
3. Baux (leases)
4. Paiements (payments)
5. Maintenance (maintenance_tickets)

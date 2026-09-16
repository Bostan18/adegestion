# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Une seule agence immobilière, en Côte d'Ivoire, 4 à 10 utilisateurs simultanés.
Il n'y a pas de portail locataire ni de portail propriétaire : tous les
utilisateurs sont des employés de l'agence, et toute donnée saisie l'est par un
employé, jamais par un tiers.

Trois rôles, définis dans `docs/ARCHITECTURE.md` et appliqués deux fois (API et
base) :

- **Administrateur** : accès total, seul à pouvoir supprimer quoi que ce soit
  (bien, bail, paiement, ticket) et à gérer les utilisateurs.
- **Agent** : gère les biens, les baux et le traitement des tickets de
  maintenance. **Aucun accès aux paiements, même en lecture.** L'entrée de
  navigation ne lui est pas proposée.
- **Comptable** : gère les paiements. Ne modifie ni les biens ni les baux.

Le seul geste ouvert aux trois rôles est **la déclaration d'un ticket de
maintenance** : un locataire qui appelle l'agence peut tomber sur n'importe qui,
et refuser la saisie à la personne qui décroche ferait perdre l'information.
Déclarer n'est pas traiter, le traitement reste à l'admin et à l'agent.

Situation d'usage : poste de bureau à l'agence, et téléphone en déplacement
(visite de bien, constat d'un dégât). Le second cas est réel, pas théorique, ce
qui rend le rendu mobile fonctionnel plutôt que cosmétique.

## Product Purpose

Remplacer la tenue d'un parc locatif au carnet et au tableur par un outil unique
où le bien, le bail, le paiement et l'incident sont liés entre eux.

Ce qui compte comme réussite, dans l'ordre :

1. Savoir à tout instant quel bien est loué, à qui, et pour quel loyer.
2. Savoir quel loyer est encaissé, en attente, en retard ou rejeté, et pouvoir
   remettre au locataire une quittance qui fasse foi.
3. Ne pas perdre un incident signalé, et garder trace de ce qu'il a coûté.

Le projet a une seconde finalité, assumée : il sert de vitrine de compétences à
son auteur (Ahmed TIMITE, Chef de Projet IT en repositionnement data/dev). Une
interface bâclée coûte donc deux fois.

## Positioning

Un outil taillé pour **une** agence, et pour la réalité ivoirienne de
l'encaissement.

Deux conséquences concrètes qu'un logiciel de gestion locative généraliste ne
reprend pas telles quelles :

- Les moyens de paiement couvrent Orange Money, MTN Mobile Money, Moov Money et
  Wave au même rang que l'espèce, le virement et le chèque. Le Mobile Money
  n'est pas un mode d'appoint ici, c'est un mode courant.
- Il n'y a **pas** de multi-tenant, pas de colonne `agency_id`, pas de notion
  d'organisation. C'est une décision de produit inscrite dans `CLAUDE.md`, pas
  une dette : elle enlève une jointure et une classe entière de fuite de données
  entre agences.

## Operating Context

Cinq modules, dans leur ordre de construction, tous livrés :

1. **Auth et utilisateurs** : Supabase Auth, le rôle faisant foi en base et non
   dans le jeton.
2. **Biens** (`/biens`) : fiche, photos, statut (disponible, loué, en travaux,
   indisponible).
3. **Baux** (`/baux`) : locataire, période, loyer, dépôt de garantie.
4. **Paiements** (`/paiements`) : saisie manuelle, quittance PDF, export CSV.
5. **Maintenance** (`/maintenance`, `/prestataires`) : tickets, prestataires,
   coûts, photos avant et après.

Enchaînements réels du métier, que l'outil applique tout seul :

- Activer un bail passe le bien en `loue` ; clore le bail le relibère, mais
  seulement s'il était bien `loue`.
- Deux baux actifs ne peuvent pas se chevaucher sur un même bien : le refus est
  explicite et nomme le locataire déjà en place.
- Un paiement au chèque exige une référence, parce qu'un chèque peut revenir
  sans provision et qu'il faut alors pouvoir le passer en `rejete`.
- Un coût réel ne se saisit pas sur une intervention en cours, mais un coût déjà
  engagé survit à la réouverture du ticket : l'argent a bien été dépensé.

Documents qui sortent de l'application et partent chez un tiers :

- **La quittance de loyer** (PDF) est remise au locataire. C'est le seul
  artefact de l'application vu par quelqu'un d'extérieur à l'agence, et le seul
  dont la mise en forme engage l'agence.
- **L'export CSV** des paiements est ouvert dans Excel en français : séparateur
  point-virgule et BOM UTF-8, sans quoi les accents et les colonnes cassent.

## Capabilities and Constraints

**Langue.** Interface en français, code en anglais (tables, colonnes, fonctions,
variables). Toute étiquette visible est en français, accents compris, y compris
dans les PDF et les exports. Les libellés de statut, de moyen de paiement et de
rôle sont centralisés dans `frontend/src/lib/format.ts` : c'est le vocabulaire
du produit, pas de la décoration.

**Montants.** Franc CFA (XOF), formaté `fr-FR`. Pas de centimes à l'affichage.

**Sécurité.** Le RBAC est appliqué deux fois, par dépendances FastAPI et par
policies RLS Supabase. Une règle affichée côté interface (masquer un bouton)
n'est jamais la règle : elle double une garde serveur qui existe déjà.

**Photos.** Compressées dans le navigateur avant envoi (1600 px max, WebP q0.8,
5 Mo plafond) puis déposées directement sur Supabase Storage via une URL signée.
Les buckets sont privés, les images passent par des URL signées.

**Contraintes techniques durables.** FastAPI, Next.js 14 (App Router),
TypeScript, Tailwind, primitives shadcn/ui écrites à la main, Supabase
(PostgreSQL, Auth, Storage) en région Stockholm, déploiement Render. Le choix de
base de données ne se change pas sans discussion préalable.

**Explicitement non décidé, à ne pas inventer :**

- Le **niveau d'accessibilité visé** (WCAG 2.1 AA ou autre) n'a jamais été fixé.
- L'agence a-t-elle un **logo ou une charte existante** à respecter, inconnu.
- « AdeImmo » est le nom du projet. Savoir si l'interface doit porter ce nom ou
  celui de l'agence n'est pas tranché.
- Le **rapprochement bancaire** (virements, chèques) est prévu au backlog, non
  construit.

## Brand Commitments

Le seul élément d'identité posé à ce jour est le nom **AdeImmo**, présent dans
le titre de page, l'en-tête applicatif et l'écran de connexion. Il n'y a ni
logo, ni charte, ni palette imposée par l'agence : la direction visuelle
actuelle est un choix de l'auteur, pas une contrainte reçue. Elle peut donc être
discutée, contrairement à ce qui figure en « Capabilities and Constraints ».

## Evidence on Hand

Réel et vérifiable dans le dépôt :

- `docs/ARCHITECTURE.md` : modèle de données, matrice RBAC, décisions.
- `docs/schema.sql` : schéma de référence, repris en migrations Alembic.
- `docs/BACKLOG.md` : ce qui est sciemment reporté.
- `docs/SKILLS.md` : outillage Claude Code du projet.
- `supabase/01..05_*.sql` : policies RLS, et un jeu de données d'exemple.
- 180 tests backend, dont les règles métier des quatre modules.

Absences à ne pas combler par de la fiction : **aucun** témoignage client,
aucune métrique d'usage, aucun chiffre de parc réel, aucune donnée de production.
L'agence n'utilise pas encore l'application. Les captures d'écran produites
jusqu'ici l'ont été sur un jeu de données inventé pour la démonstration.

## Product Principles

1. **Le refus est une fonctionnalité.** Quand l'outil bloque (chevauchement de
   baux, chèque sans référence, coût réel trop tôt), il dit ce qui bloque et
   quoi faire à la place. Un message d'erreur qui ne propose rien est un bug.
2. **L'historique ne se supprime pas, il se désactive.** Un prestataire
   rattaché à des tickets ne peut pas être effacé. La suppression est partout
   réservée à l'admin.
3. **Une donnée saisie deux fois est une donnée fausse une fois.** Ce que le
   système peut déduire, il le déduit : statut du bien depuis le bail, date de
   résolution depuis le statut du ticket, déclarant depuis la session.
4. **Le rôle décide de ce qui est visible, pas seulement de ce qui est
   cliquable.** Un comptable ne voit pas de bouton grisé sur les biens, il ne
   voit pas la section.
5. **Le téléphone est un poste de travail.** Aucun écran ne demande de
   défilement horizontal, et les informations décisives (loyer, statut, priorité)
   restent visibles sans ouvrir la fiche.

## Accessibility & Inclusion

Aucun niveau de conformité n'a été fixé avec l'auteur, et rien ne doit être
affirmé à ce titre.

Ce qui est vrai de l'implémentation actuelle, et qui ne doit pas régresser :

- Anneau de focus visible sur tous les contrôles interactifs
  (`focus-visible:ring-2 ring-ring`, avec `ring-offset-2`).
- Libellés `<Label>` associés aux champs, et `sr-only` sur les actions à icône
  seule (fermeture de dialogue).
- Le statut n'est jamais porté par la seule couleur : chaque pastille contient
  son libellé en toutes lettres.
- `lang="fr"` sur le document.

Deux points connus, non traités et à ne pas présenter comme réglés : la palette
n'a pas été mesurée au contraste, et le thème sombre est défini en variables
mais aucun sélecteur ne l'active.

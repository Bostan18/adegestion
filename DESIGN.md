---
name: AdeImmo
description: Gestion locative d'une agence ivoirienne, sobre et dense, pensée comme un registre.
colors:
  teal-profond: "hsl(173 80% 26%)"
  teal-clair: "hsl(173 70% 42%)"
  blanc-page: "hsl(0 0% 100%)"
  encre-ardoise: "hsl(222 47% 11%)"
  gris-papier: "hsl(210 40% 96%)"
  gris-legende: "hsl(215 16% 47%)"
  trait-gris: "hsl(214 32% 91%)"
  rouge-rejet: "hsl(0 72% 51%)"
  vert-encaisse-fond: "#d1fae5"
  vert-encaisse-texte: "#065f46"
  ambre-attente-fond: "#fef3c7"
  ambre-attente-texte: "#78350f"
  nuit-page: "hsl(222 47% 8%)"
  nuit-carte: "hsl(222 47% 11%)"
  nuit-surface: "hsl(217 33% 17%)"
  nuit-trait: "hsl(217 33% 20%)"
  nuit-encre: "hsl(210 40% 98%)"
  nuit-legende: "hsl(215 20% 65%)"
  nuit-rouge-rejet: "hsl(0 63% 45%)"
typography:
  headline:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: "2rem"
    letterSpacing: "-0.025em"
  title:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: "1"
    letterSpacing: "-0.025em"
  body:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.25rem"
    letterSpacing: "normal"
  label:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: "1"
    letterSpacing: "normal"
  micro:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: "1rem"
    letterSpacing: "normal"
rounded:
  sm: "5.6px"
  md: "7.6px"
  lg: "9.6px"
  full: "9999px"
spacing:
  xs: "12px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.teal-profond}"
    textColor: "{colors.blanc-page}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "hsl(173 80% 26% / 0.9)"
    textColor: "{colors.blanc-page}"
  button-outline:
    backgroundColor: "{colors.blanc-page}"
    textColor: "{colors.encre-ardoise}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
    height: "40px"
  button-outline-hover:
    backgroundColor: "{colors.gris-papier}"
    textColor: "{colors.encre-ardoise}"
  button-destructive:
    backgroundColor: "{colors.rouge-rejet}"
    textColor: "{colors.blanc-page}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
    height: "40px"
  button-ghost-hover:
    backgroundColor: "{colors.gris-papier}"
    textColor: "{colors.encre-ardoise}"
  card:
    backgroundColor: "{colors.blanc-page}"
    textColor: "{colors.encre-ardoise}"
    rounded: "{rounded.lg}"
    padding: "24px"
  input:
    backgroundColor: "{colors.blanc-page}"
    textColor: "{colors.encre-ardoise}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
    height: "40px"
    width: "100%"
  badge-default:
    backgroundColor: "{colors.teal-profond}"
    textColor: "{colors.blanc-page}"
    typography: "{typography.micro}"
    rounded: "{rounded.full}"
    padding: "2px 10px"
  badge-success:
    backgroundColor: "{colors.vert-encaisse-fond}"
    textColor: "{colors.vert-encaisse-texte}"
    typography: "{typography.micro}"
    rounded: "{rounded.full}"
    padding: "2px 10px"
  badge-warning:
    backgroundColor: "{colors.ambre-attente-fond}"
    textColor: "{colors.ambre-attente-texte}"
    typography: "{typography.micro}"
    rounded: "{rounded.full}"
    padding: "2px 10px"
  badge-destructive:
    backgroundColor: "{colors.rouge-rejet}"
    textColor: "{colors.blanc-page}"
    typography: "{typography.micro}"
    rounded: "{rounded.full}"
    padding: "2px 10px"
  badge-secondary:
    backgroundColor: "{colors.gris-papier}"
    textColor: "{colors.encre-ardoise}"
    typography: "{typography.micro}"
    rounded: "{rounded.full}"
    padding: "2px 10px"
  table-head:
    textColor: "{colors.gris-legende}"
    typography: "{typography.label}"
    height: "44px"
    padding: "0 16px"
  table-cell:
    textColor: "{colors.encre-ardoise}"
    typography: "{typography.body}"
    padding: "16px"
  table-row-hover:
    backgroundColor: "hsl(210 40% 96% / 0.5)"
  dialog:
    backgroundColor: "{colors.blanc-page}"
    textColor: "{colors.encre-ardoise}"
    rounded: "{rounded.lg}"
    padding: "24px"
    width: "100%"
    size: "max-width 32rem"
  nav-link:
    textColor: "{colors.gris-legende}"
    typography: "{typography.body}"
  nav-link-hover:
    textColor: "{colors.encre-ardoise}"
---

# Design System: AdeImmo

## Overview

**Creative North Star: « Le registre de l'agence »**

AdeImmo ressemble à un registre tenu proprement, pas à un tableau de bord qui
cherche à impressionner. Un registre a une autorité particulière : on l'ouvre
pour savoir, pas pour être séduit. Chaque ligne y vaut par sa lisibilité et par
la confiance qu'on lui accorde. C'est la promesse visuelle de cet outil, qui
remplace un carnet et un tableur dans une agence où l'information compte plus
que la mise en scène.

L'interface est donc dense mais aérée, presque entièrement en gris et en blanc,
avec une seule couleur vive qui ne sert qu'à deux choses : désigner l'action
principale, et signaler un état. Il n'y a pas d'image décorative, pas de
dégradé, pas d'illustration. Les seules images de l'application sont les photos
des biens et des interventions, c'est à dire de la donnée, et elles sont
présentées comme telle.

Le vert-bleu profond qui porte la marque est le seul geste d'expressivité assumé.
Il évoque la fiabilité plutôt que l'immobilier de prestige, et il a été choisi
pour ne ressembler ni au bleu bancaire ni au doré des agences haut de gamme.
Aucune autre direction n'a été explicitement rejetée par le commanditaire : ce
qui est écrit ici décrit ce que le code fait aujourd'hui.

**Key Characteristics:**

- Une seule couleur d'accent, un vert-bleu profond, rare à l'écran.
- Texte de travail à 14 px, pas 16 px : la densité est un choix, pas un oubli.
- Surfaces plates au repos, l'ombre ne dit que la profondeur réelle.
- Tout état métier porte un mot, jamais une couleur seule.
- Deux rendus par liste : tableau sur grand écran, cartes en dessous de `lg`.
- Interface intégralement en français, accents compris, jusque dans les PDF.

## Colors

Une palette de gris neutres légèrement bleutés, traversée par un seul accent
vert-bleu, plus deux couleurs d'état empruntées à Tailwind. Toutes les valeurs
sont déclarées en triplets HSL dans `frontend/src/app/globals.css` et consommées
par Tailwind via `hsl(var(--token))` : c'est la source de vérité du projet, et
la raison pour laquelle la notation HSL est conservée ici plutôt que l'hexadécimal.

### Primary

- **Teal Profond** (`hsl(173 80% 26%)`) : la couleur de marque. Elle porte le
  bouton d'action principale, l'icône du logo dans l'en-tête, l'anneau de focus
  et la pastille d'un bien loué. Rien d'autre. En thème sombre elle s'éclaircit
  en **Teal Clair** (`hsl(173 70% 42%)`) pour tenir le contraste sur fond nuit.

### Neutral

- **Blanc Page** (`hsl(0 0% 100%)`) : fond de l'application, des cartes, des
  champs et de l'en-tête. Le blanc est le fond par défaut, pas une surface
  surélevée.
- **Encre Ardoise** (`hsl(222 47% 11%)`) : tout le texte de premier plan. Un
  presque-noir bleuté, jamais un noir pur.
- **Gris Papier** (`hsl(210 40% 96%)`) : surface secondaire unique, partagée par
  `secondary`, `muted` et `accent`. Elle sert de fond aux boutons secondaires,
  aux pastilles neutres, au survol d'un élément de menu et au fond de l'écran de
  connexion (à 40 % d'opacité).
- **Gris Légende** (`hsl(215 16% 47%)`) : texte de second rang, en-têtes de
  colonnes, sous-titres de page, liens de navigation au repos, états vides.
- **Trait Gris** (`hsl(214 32% 91%)`) : toutes les bordures et tous les
  séparateurs, y compris le contour des champs. Une seule valeur de trait dans
  toute l'application.

### Couleurs d'état

Ces trois-là ne décorent rien, elles qualifient une donnée métier. Le mappage
exact vit dans `frontend/src/lib/format.ts`.

- **Rouge Rejet** (`hsl(0 72% 51%)`) : paiement en retard ou rejeté, bail
  résilié, ticket ouvert, priorité urgente, et action destructive.
- **Vert Encaissé** (fond `#d1fae5`, texte `#065f46`) : paiement encaissé, bail
  actif, bien disponible, ticket résolu.
- **Ambre Attente** (fond `#fef3c7`, texte `#78350f`) : paiement en attente,
  bien en travaux, ticket en cours, priorité haute.

### Thème sombre

Un jeu complet de variables existe sous `.dark` (page `hsl(222 47% 8%)`, carte
`hsl(222 47% 11%)`, surface `hsl(217 33% 17%)`, encre `hsl(210 40% 98%)`).
**Aucun sélecteur ne l'active aujourd'hui.** Il est prêt, il n'est pas livré. Ne
pas décrire l'application comme ayant un thème sombre tant qu'aucun bascule
n'existe.

### Named Rules

**La règle de l'accent rare.** Le Teal Profond n'apparaît jamais plus de deux
fois sur un écran au repos : le bouton d'action principale, et le logo. Une
pastille de statut loué peut s'y ajouter dans une liste. Si un troisième usage
décoratif apparaît, c'est l'usage décoratif qui saute, pas la règle.

**La règle du mot avant la couleur.** Aucun état ne se lit à la couleur seule.
Chaque pastille contient son libellé français en toutes lettres (« En retard »,
« Rejeté », « En travaux »). Une pastille vide, une pastille réduite à un point
coloré, ou une ligne de tableau teintée sans texte sont interdites.

## Typography

**Display Font:** aucune. Le projet n'a pas de police de titrage.
**Body Font:** la pile système de Tailwind (`ui-sans-serif, system-ui,
-apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans",
sans-serif`).
**Label/Mono Font:** aucune police distincte.

**Character:** volontairement anonyme. Aucune police n'est chargée, ni par
`next/font` ni par lien externe, ce qui veut dire zéro requête de police, zéro
saut de mise en page au chargement, et un rendu natif sur chaque poste. Toute la
personnalité typographique passe donc par la graisse et la hiérarchie, pas par
le dessin des lettres. C'est cohérent avec le registre : un registre n'a pas de
police de caractère, il a une écriture nette.

### Hierarchy

- **Headline** (600, 1.5rem / 24 px, interligne 2rem, `tracking-tight`) : le
  titre de page, un seul par écran, toujours suivi d'une ligne de contexte en
  Gris Légende (« 12 biens au portefeuille »).
- **Title** (600, 1.125rem / 18 px, interligne 1, `tracking-tight`) : titre de
  carte, titre de dialogue.
- **Body** (400, 0.875rem / 14 px, interligne 1.25rem) : **c'est le corps de
  texte réel de l'application.** Cellules de tableau, descriptions, valeurs de
  fiche, texte des liens de navigation.
- **Label** (500, 0.875rem / 14 px, interligne 1) : étiquettes de champ,
  intitulés de boutons, en-têtes de colonnes.
- **Micro** (600, 0.75rem / 12 px) : pastilles de statut, adresse e-mail dans
  l'en-tête, mentions annexes.

### Named Rules

**La règle des quatorze pixels.** Le texte de travail est à 14 px, pas à 16 px.
La densité est assumée : un gestionnaire compare des lignes, il ne lit pas un
article. Un écran qui repasse son corps de texte à 16 px casse la cohérence avec
tout le reste de l'application.

**La règle du titre accompagné.** Un titre de page n'est jamais seul. Il porte
en dessous une phrase courte en Gris Légende qui compte ou qualifie ce que la
page montre. Cette phrase est en français et s'accorde au pluriel.

## Layout

Une seule colonne centrée, dans le conteneur Tailwind : centré, marge interne de
24 px, plafonné à 1400 px à partir de `2xl`. L'en-tête fait 64 px de haut et la
zone principale respire de 32 px en haut et en bas (`py-8`).

**Rythme d'espacement.** Les blocs d'une page sont séparés de 24 px
(`space-y-6`), les blocs internes d'une carte de 16 px (`space-y-4`), les cartes
d'une grille mobile de 12 px (`gap-3`). La marge interne d'une carte est de
24 px, celle d'une cellule de tableau de 16 px. Un état vide occupe 48 px de
marge interne, centré.

**Formulaires.** Toute page de création ou de modification est bornée à
`max-w-3xl` et centrée. La lecture prend toute la largeur, la saisie non.

**Points de rupture, et ce qu'ils changent vraiment.** Deux seuils portent une
décision, pas un ajustement :

- **`sm` (640 px)** : en dessous, les liens de navigation descendent sur une
  seconde ligne sous l'en-tête. Logo, badge de rôle et bouton de déconnexion
  occupent déjà toute la largeur, et les garder sur une seule ligne faisait
  déborder la page horizontalement.
- **`lg` (1024 px)** : en dessous, **les tableaux deviennent des cartes**. Un
  tableau à sept colonnes n'est pas lisible sur un téléphone : le loyer et le
  statut sortaient du cadre. Les deux rendus coexistent dans le même composant,
  l'un en `lg:hidden`, l'autre en `hidden lg:block`. Entre `sm` et `lg`, les
  cartes passent sur deux colonnes.

### Named Rules

**La règle du zéro défilement horizontal.** Aucun écran ne défile
horizontalement à 390 px de large. Quand une donnée ne rentre pas, on change de
rendu, on ne fait pas défiler. Cette règle a déjà coûté deux correctifs, elle
n'est pas négociable.

## Elevation & Depth

Le système est **plat au repos**. La profondeur est portée par le trait et par la
teinte, pas par l'ombre : une carte se distingue du fond par sa bordure Trait
Gris, pas par un halo. Les trois ombres du système sont structurelles et
signalent un vrai empilement.

### Shadow Vocabulary

- **Repos de carte** (`box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05)`) : presque
  imperceptible, juste de quoi décoller la carte du fond blanc. Sur toutes les
  cartes.
- **Surface flottante** (`box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)`)
  : liste déroulante d'un `Select`, qui sort réellement du flux.
- **Surface modale** (`box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)`)
  : dialogue, au-dessus d'un voile noir à 60 % avec flou d'arrière-plan.

### Named Rules

**La règle de l'ombre méritée.** Une ombre ne se pose que sur un élément qui
flotte vraiment au-dessus du contenu. Un survol ne crée pas d'ombre, il change
une couleur de fond. Une carte ne se soulève pas au passage de la souris.

## Shapes

Le rayon de base est **9,6 px** (`--radius: 0.6rem`), et les deux rayons
inférieurs en dérivent par soustraction : 7,6 px pour les contrôles
(`calc(var(--radius) - 2px)`) et 5,6 px pour les éléments imbriqués
(`calc(var(--radius) - 4px)`). Ce 0.6rem est un écart volontaire au 0.5rem par
défaut de shadcn/ui : légèrement plus doux, sans devenir rond.

Le langage de formes tient en trois cas :

- **Rectangles à coins doux** pour tout ce qui contient : cartes, dialogues,
  panneaux, images de biens.
- **Coins de contrôle** (7,6 px) pour tout ce qui se clique ou se saisit :
  boutons, champs, déclencheurs de liste.
- **Capsule complète** (`9999px`) pour les seules pastilles de statut. C'est la
  seule forme entièrement arrondie de l'application, et c'est ce qui la rend
  reconnaissable au premier coup d'oeil.

Une bordure d'un pixel en Trait Gris est posée par défaut sur tous les éléments
(`* { @apply border-border }`), ce qui veut dire qu'ajouter `border` à un
composant suffit : la couleur est déjà bonne.

### Named Rules

**La règle de la capsule réservée.** Seules les pastilles de statut sont en
capsule. Un bouton en capsule, un champ en capsule ou une carte en capsule
brouillent le seul repère de forme du système.

## Components

### Buttons

- **Shape:** coins de contrôle (7,6 px), hauteur fixe de 40 px en taille par
  défaut, 36 px en `sm`, 44 px en `lg`. Libellé en Label (500, 14 px), jamais en
  capitales, avec 8 px d'écart entre l'icône et le texte.
- **Primary:** fond Teal Profond, texte blanc, 8 px sur 16 px de marge interne.
  Un seul par écran, celui qui crée ou enregistre.
- **Hover / Focus:** le survol baisse l'opacité du fond à 90 %, en transition de
  couleur seule. Le focus clavier pose un anneau de 2 px en Teal Profond, décalé
  de 2 px (`focus-visible:ring-2 ring-ring ring-offset-2`). L'état désactivé
  descend à 50 % d'opacité et coupe les événements de pointeur.
- **Secondary / Outline / Ghost / Link:** `outline` porte une bordure Trait Gris
  sur fond blanc et vire au Gris Papier au survol, c'est la variante des actions
  secondaires d'une fiche. `ghost` n'a ni fond ni bordure au repos et prend le
  Gris Papier au survol, elle est réservée aux actions d'icône dans une ligne.
  `destructive` porte le Rouge Rejet plein, uniquement pour une suppression, et
  uniquement là où le rôle l'autorise.

### Badges

- **Style:** capsule pleine, 12 px, graisse 600, 2 px sur 10 px de marge interne,
  bordure transparente sauf en variante `outline`.
- **State:** six variantes, dont quatre portent un sens métier (`success`,
  `warning`, `destructive`, `secondary`). Le choix de variante n'est jamais fait
  dans le composant d'affichage : il vient d'une table de correspondance dans
  `frontend/src/lib/format.ts`. Ajouter un statut métier veut dire ajouter une
  entrée là, pas écrire une condition dans une page.

### Cards / Containers

- **Corner Style:** 9,6 px.
- **Background:** Blanc Page sur fond Blanc Page. La carte se lit par sa
  bordure.
- **Shadow Strategy:** ombre de repos uniquement, voir Elevation & Depth.
- **Border:** un pixel en Trait Gris.
- **Internal Padding:** 24 px, et 24 px sans reprise en haut pour le contenu qui
  suit un en-tête de carte.

### Inputs / Fields

- **Style:** hauteur 40 px, fond Blanc Page, bordure Trait Gris, coins de
  contrôle (7,6 px), texte à 14 px, marge interne 8 px sur 12 px, largeur
  complète. Le texte indicatif est en Gris Légende.
- **Focus:** anneau de 2 px en Teal Profond décalé de 2 px, contour natif
  supprimé. Le même traitement exactement que sur les boutons, ce qui rend le
  parcours clavier lisible d'un bout à l'autre du formulaire.
- **Error / Disabled:** désactivé à 50 % d'opacité avec curseur interdit. Il n'y
  a pas aujourd'hui de style d'erreur au niveau du champ : les refus métier
  remontent par une notification `sonner` en haut à droite, avec le message du
  serveur.

### Navigation

- En-tête de 64 px, fond Blanc Page, bordure basse Trait Gris, non collant.
- À gauche, le logo : icône `Building2` en Teal Profond (20 px) suivie du mot
  « AdeImmo » en graisse 600.
- Les liens sont en Body (14 px) et en Gris Légende au repos, passant en Encre
  Ardoise au survol, avec 20 px entre eux. Il n'y a **pas d'indicateur de page
  active** aujourd'hui.
- À droite, le nom et l'e-mail de l'utilisateur (masqués sous `sm`), une
  pastille `secondary` portant son rôle, puis la déconnexion.
- **Les entrées de navigation dépendent du rôle.** Un comptable ne voit pas
  d'entrée grisée pour les paiements d'un agent : l'agent n'a simplement pas
  l'entrée « Paiements ». Ce qui est interdit n'est pas affiché.

### Liste à deux rendus (composant signature)

C'est le motif le plus caractéristique du projet, repris à l'identique pour les
biens, les baux, les paiements et les tickets. Un même composant rend :

- une grille de cartes (`grid gap-3 sm:grid-cols-2 lg:hidden`) où chaque carte
  porte l'essentiel, dont toujours le montant et le statut ;
- un tableau (`hidden lg:block`) dans une carte, en-têtes à 44 px en Gris
  Légende, cellules à 16 px, ligne survolée en Gris Papier à 50 % ;
- un état vide qui remplace les deux : une carte à 48 px de marge interne, texte
  centré en Gris Légende, phrase française complète (« Aucun bien ne correspond
  à cette recherche. »).

Les deux rendus affichent les mêmes données décisives. Une colonne qui
n'existerait que dans le tableau est une colonne perdue pour la moitié des
usages.

## Do's and Don'ts

### Do:

- **Do** prendre les libellés et les variantes de pastille dans
  `frontend/src/lib/format.ts`. C'est le vocabulaire du produit, en français et
  accentué, et il est déjà aligné avec les valeurs de la base.
- **Do** écrire tout texte visible en français, accents compris, y compris dans
  les PDF et les exports CSV. Un « Paye » sans accent sur une quittance remise à
  un locataire est un défaut, pas un détail.
- **Do** livrer les deux rendus de liste ensemble, cartes sous `lg` et tableau
  au-dessus, en gardant le montant et le statut visibles dans les deux.
- **Do** accompagner un titre de page d'une ligne de contexte en Gris Légende,
  accordée au pluriel.
- **Do** laisser l'anneau de focus (`ring-2 ring-ring ring-offset-2`) sur tout
  contrôle interactif.
- **Do** masquer entièrement ce qu'un rôle ne peut pas faire, et doubler cette
  décision d'une garde serveur. L'interface n'est jamais la sécurité.
- **Do** formuler les états vides en phrase complète qui dit quoi faire ensuite.

### Don't:

- **Don't** introduire une seconde couleur d'accent, un dégradé ou une police
  chargée. La palette tient en un accent et cinq gris, et aucune police n'est
  téléchargée.
- **Don't** signaler un état par la seule couleur. Le libellé est obligatoire.
- **Don't** laisser un écran défiler horizontalement à 390 px de large.
- **Don't** remonter le corps de texte à 16 px « pour la lisibilité ». Le
  système est à 14 px partout.
- **Don't** poser une ombre au survol ni soulever une carte. Le survol change un
  fond, rien d'autre.
- **Don't** arrondir en capsule autre chose qu'une pastille de statut.
- **Don't** afficher un bouton désactivé pour une action que le rôle n'a pas le
  droit d'accomplir.
- **Don't** décrire l'application comme ayant un thème sombre. Les variables
  existent, la bascule n'existe pas.

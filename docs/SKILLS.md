# Outillage Claude Code du projet

Skills et serveurs MCP installés au niveau du projet. Ils sont disponibles
pour toute session Claude Code ouverte à la racine du dépôt.

## Skills

| Skill | Source | Version | Poids |
|---|---|---|---|
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | commit `15de38f` | 3,6 Mo |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 4.3.1, moteur `0.1.5` | 2,2 Mo |

### Ce qu'elles apportent

**`ui-ux-pro-max`** est une base de connaissances UI/UX interrogeable hors
ligne : 79 styles, 192 palettes produit, 74 associations de polices, 119
règles UX, 105 icônes, 25 types de graphiques et 22 stacks. Elle sert à choisir
une direction visuelle argumentée plutôt qu'au hasard. Recherche directe :

```bash
python .claude/skills/ui-ux-pro-max/scripts/search.py "<requête>" --domain style
python .claude/skills/ui-ux-pro-max/scripts/search.py "<requête>" --design-system
```

**`impeccable`** est un ensemble de playbooks de revue et d'amélioration
d'interface : hiérarchie visuelle, charge cognitive, accessibilité, états
vides et d'erreur, responsive, typographie, motion. Elle s'invoque avec des
sous-commandes (`audit`, `polish`, `clarify`, `harden`, `typeset`, ...).

### Ce qui n'a pas été installé

Le dépôt `ui-ux-pro-max-skill` livre cinq skills satellites de plus :
`banner-design`, `brand`, `design-system`, `slides` et `ui-styling`. Elles
n'ont pas été retenues, le projet n'ayant pas besoin de génération de
bannières ni de présentations.

Il livre aussi une skill nommée `design`, volontairement écartée : elle entre
en collision avec la skill `design` native de Claude Code, qu'elle masquerait
dans ce projet.

### Modification locale, à réappliquer en cas de mise à jour

Le `SKILL.md` de `ui-ux-pro-max` référence ses scripts via
`${CLAUDE_PLUGIN_ROOT}`, une variable définie uniquement en installation
plugin. Elle est vide pour une skill de projet, et les onze chemins concernés
pointaient alors vers la racine du système de fichiers.

Ils ont été réancrés sur la racine du projet :

```
${CLAUDE_PLUGIN_ROOT}/.claude/skills/...  ->  .claude/skills/...
```

En cas de remontée de version depuis l'amont, refaire ce remplacement.

### Téléchargement au premier lancement d'impeccable

Le lanceur `.claude/skills/impeccable/scripts/impeccable` ne contient pas le
moteur : il télécharge un binaire depuis les releases GitHub du projet, à la
version épinglée `engine-v0.1.5`, dans un cache utilisateur hors du dépôt.

Le téléchargement est vérifié par somme SHA256 contre un fichier `.sha256`
publié à côté du binaire, et le lanceur refuse de s'exécuter si la
vérification est impossible. Une machine sans accès réseau ne pourra pas
utiliser cette skill au-delà de ses playbooks en markdown.

Le hook de détection automatique livré par impeccable n'a pas été installé. Il
s'active à la demande avec `/impeccable hooks on`.

## Contexte fourni aux skills de design

Les deux skills de design partent d'une page blanche si on ne leur donne rien,
et proposent alors une direction visuelle prise dans leur base plutôt que celle
du projet. Trois fichiers leur servent de point de départ, écrits à partir du
code existant et non inventés.

| Fichier | Rôle |
|---|---|
| [`PRODUCT.md`](../PRODUCT.md) | Vérité produit durable : utilisateurs, rôles, enchaînements métier, contraintes, ce qui est explicitement non décidé. Aucune décision visuelle. |
| [`DESIGN.md`](../DESIGN.md) | Système visuel **existant** : jetons en frontmatter YAML, puis huit sections au [format DESIGN.md](https://github.com/google-labs-code/design.md). |
| `.impeccable/design.json` | Annexe machine de `DESIGN.md` : rampes tonales, ombres, mouvement, points de rupture, et huit composants en HTML/CSS autonomes que le panneau de prévisualisation sait rendre. |

`DESIGN.md` documente ce qui est déjà codé, il ne propose rien de neuf. Les
valeurs viennent de `frontend/src/app/globals.css`, de `tailwind.config.ts` et
des primitives écrites à la main dans `frontend/src/components/ui/`. Les huit
extraits HTML/CSS de l'annexe ont été rendus dans un navigateur et comparés à
l'application avant d'être figés.

Trois points y sont laissés ouverts, faute de réponse de l'agence : le niveau
d'accessibilité visé, l'existence d'un logo ou d'une charte, et le nom que doit
porter l'interface. Ils sont marqués comme non décidés dans `PRODUCT.md`, ce qui
vaut mieux qu'une réponse inventée qu'une skill reprendrait ensuite pour argent
comptant.

À relire après toute évolution visuelle : un `DESIGN.md` en retard sur le code
est pire que pas de `DESIGN.md` du tout.

## Serveurs MCP

Déclarés dans [`.mcp.json`](../.mcp.json) à la racine.

| Serveur | Paquet | Rôle |
|---|---|---|
| `magicuidesign-mcp` | `@magicuidesign/mcp@latest` | Registre de composants Magic UI (React, Tailwind, animations) |

Trois outils exposés, vérifiés par un handshake MCP réel :

- `listRegistryItems` : liste les composants du registre, avec filtres
- `getRegistryItem` : détail d'un composant
- `searchRegistryItems` : recherche par mot-clé ou cas d'usage

Magic UI se pose sur React et Tailwind, la même base que le frontend, et
complète shadcn/ui côté composants animés. Le serveur ne fait que lire un
registre, il n'écrit rien dans le projet : c'est Claude qui reprend le code
proposé.

### Deux points à connaître

**Le paquet n'est pas épinglé.** `@latest` fait résoudre la dernière version
publiée à chaque démarrage de session, et `npx -y` l'installe sans demander
confirmation. Une régression amont arrive donc sans prévenir. Pour figer,
remplacer `@latest` par une version précise dans `.mcp.json`.

**Le serveur demande une autorisation au premier lancement.** Claude Code
demande de faire confiance aux serveurs MCP déclarés par un projet, la première
fois qu'une session s'ouvre à cette racine. C'est attendu, et ça n'arrive
qu'une fois.

Un serveur MCP n'est chargé qu'au démarrage d'une session : il faut en ouvrir
une nouvelle pour que les outils apparaissent.

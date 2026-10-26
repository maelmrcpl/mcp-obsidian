# Règles d'écriture (rules.py)

Toutes les violations lèvent `RuleError`, dont le message est lu par le modèle. Elles s'appliquent à `create_note`, `update_note` et `append_log`.

## Ordre des contrôles
- `create_note` : `check_path`, `check_content(content)` (frontmatter toujours exigé), page déjà existante, dossier inexistant.
- `update_note` : `check_path`, `check_not_append_only`, `check_content(content, path)`, comparaison de `expected_content`.
- `append_log` : `format_log_entry` (type, titre, secrets dans `details`), puis ajout.

## Chemins (`check_path`)
Les `\` sont convertis en `/` avant contrôle. Vérifications, dans cet ordre :
| Condition | Message |
|---|---|
| commence par `/`, contient `..` ou `:` | `Chemin invalide` |
| commence par `raw/` | `` `raw/` est en lecture seule `` |
| ne commence pas par `wiki/` | ``Ecriture limitée à `wiki/` `` |
| ne finit pas par `md` (casse ignorée) | `Une page doit finir par .md` |
| nom de fichier non conforme à `[a-z0-9]+(-[a-z0-9]+)*\.md` | `Nom en kebab-case attendu : exemple-fichier.md` |

Seul le nom du fichier est contrôlé (kebab-case), pas les dossiers.

## Frontmatter (`check_frontmatter`)
- Bloc `---` ... `---` en tête de page, sinon `Frontmatter manquant`.
- Champs obligatoires : `title`, `type`, `created`, `updated`, `sources`, `tags`. Sinon `Champs manquants : ...`.
- `type` doit appartenir à : `source`, `feature`, `product`, `persona`, `concept`, `style`, `analysis`, `tool`. Sinon `type invalide, attendu : [...]`.
- Seules les clés sont vérifiées, pas le format des valeurs.

## Contenu (`check_content(content, path="")`)
1. Frontmatter vérifié, sauf si `path` est une page de base.
2. `[[wiki/` présent dans le texte → `Lien avec préfixe wiki/ interdit` (valable aussi pour les pages de base). Les liens s'écrivent `[[dossier/nom]]`.
3. Secrets : regex insensible à la casse sur `authorization:`, `bearer <valeur>`, `token=`, `session_id=` / `sessionid=` → `Le contenu ressemble à un secret, écriture refusée`.

## Pages de base
`wiki/index.md`, `wiki/log.md`, `wiki/overview.md`, `wiki/glossary.md` (`BASE_PAGES`).
- `update_note` ne contrôle pas leur frontmatter (format propre). Préfixe `wiki/` et secrets restent contrôlés.
- `create_note` n'a pas cette exemption : une création exige toujours un frontmatter.
- Effet sur le lint : voir `liens.md`.

## Log en ajout seul
- `APPEND_ONLY = {wiki/log.md}` : `update_note` refuse avec `... est en ajout seul : utiliser append_log`, même si `expected_content` est correct.
- `append_log` : `type` dans `ingest`, `query`, `lint`, `maintenance` (sinon `type de log invalide`) ; `title` non vide et sur une seule ligne ; les secrets sont contrôlés dans `details` (pas dans `title`).

## Concurrence de `update_note`
- `expected_content` doit être le contenu actuel, relu juste avant la modification.
- Comparaison via `same_content` : fins de ligne `\r\n` normalisées en `\n` et espaces de début et de fin ignorés.
- Écart → `<path> a changé depuis la dernière lecture : la relire avant de la modifier`.

## Nouveau dossier (`create_note`)
- Le dossier est `path` sans le nom du fichier. S'il n'existe pas (`folder_exists`, basé sur un 404), refus : `Le dossier <dossier> n'existe pas : demander l'accord de l'utilisateur puis passer confirm_new_folder=True`.
- `confirm_new_folder=True` ne se passe qu'après accord explicite de l'utilisateur.

## Secrets
Ne jamais écrire dans le wiki ni dans le log : clés d'API, jetons, en-têtes `Authorization`, identifiants de session. Ne jamais afficher le contenu de `.env`.

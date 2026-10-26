# Liens et lint (links.py)

Fonctions pures : elles reçoivent du texte ou un dictionnaire `{chemin: contenu}`, jamais le client. Le chargement des pages est fait dans `server.py`.

## Format des liens
- Wikilink `[[dossier/nom]]`, relatif à `wiki/`, **sans** préfixe `wiki/` et sans `.md`.
- `resolve("concepts/agile")` → `wiki/concepts/agile.md`. `link_name("wiki/concepts/agile.md")` → `concepts/agile`.
- Un nom seul (`[[agile]]`) n'est pas résolu ; il est valide seulement s'il correspond à une page à la racine de `wiki/`. Quand deux fichiers portent le même nom, il faut qualifier avec le dossier.

## Extraction (`extract_links`)
- Ignore les blocs de code (``` ... ```) et le code inline.
- Prend `!?[[...]]` (les embeds comptent), retire l'alias (`|...`), l'ancre (`#...`) et un `\` final (pipe échappé dans un tableau).
- Sans doublons, dans l'ordre d'apparition.

## Backlinks (`backlinks`)
Pages dont les liens se résolvent vers `path`, triées, sans la page elle-même. L'outil `get_backlinks` pré-filtre par recherche textuelle du `link_name`, donc il ne voit que les pages que la recherche Obsidian renvoie.

## Lint (`lint`)
Rapport avec 6 clés :
| Clé | Contenu |
|---|---|
| `liens_casses` | `{page, lien}` : la cible n'existe pas. |
| `liens_prefixe_wiki` | `{page, lien}` : lien commençant par `wiki/`. |
| `doublons_non_qualifies` | `{page, lien, candidats}` : nom seul introuvable mais porté par plusieurs fichiers. |
| `orphelines` | Pages sans lien entrant autre que celui de `wiki/index.md` (ou sans lien du tout). |
| `absentes_de_lindex` | Pages non liées depuis `wiki/index.md`. |
| `frontmatter_invalide` | `{page, erreur}` issu de `check_frontmatter`. |

- Les liens vers soi-même ne comptent pas comme entrants.
- Pages de base (`BASE_PAGES`, liste dans `regles.md`) : exclues des contrôles orphelines, index et frontmatter, mais leurs liens sont vérifiés (cassés, préfixe, doublons).
- Le lint ne modifie rien.

---
quand_lire: Tu modifies links.py ; tu touches lint_wiki, get_backlinks ou get_outgoing_links ; une question porte sur un lien, une page orpheline ou un doublon de nom
couvre: links.py
---
# Liens et lint (`links.py`)

Fonctions pures sur du texte ou des dictionnaires `{chemin: contenu}`, sans appel réseau.

## Fonctions
- `extract_links(text)` : cibles des `[[...]]` et `![[...]]`, sans alias (`|`) ni ancre (`#`), sans `\` final, hors blocs de code (``` ``` ``` et `` ` ``), sans doublon, dans l'ordre.
- `resolve(link)` : `concepts/agile` → `wiki/concepts/agile.md` (relatif à `wiki/`).
- `link_name(path)` : `wiki/concepts/agile.md` → `concepts/agile`.
- `backlinks(pages, path)` : pages (autres que `path`) dont un lien résolu vaut `path`, triées.

## `lint(pages)`
Renvoie un dictionnaire avec les clés suivantes. Ne modifie rien.
| Clé | Contenu |
|---|---|
| `liens_casses` | Lien dont la cible n'existe pas. |
| `liens_prefixe_wiki` | Lien commençant par `wiki/`. |
| `doublons_non_qualifies` | Lien sans `/` dont le nom correspond à plusieurs fichiers ; donne les `candidats`. |
| `orphelines` | Page (hors pages de base) sans lien entrant autre que `wiki/index.md`. |
| `absentes_de_lindex` | Page (hors pages de base) non citée par `wiki/index.md`. |
| `frontmatter_invalide` | Page dont `check_frontmatter` échoue, avec l'erreur. |

- Un lien d'une page vers elle-même ne compte pas comme lien entrant.
- Les pages de base (`BASE_PAGES` de `rules.py`) sont exclues des contrôles orphelines, index et frontmatter.

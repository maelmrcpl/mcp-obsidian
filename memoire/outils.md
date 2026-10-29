---
quand_lire: Tu ajoutes, modifies ou débogues un outil de server.py ; on te demande ce que fait ou renvoie un outil. Pour create_note, update_note et append_log, lis aussi memoire/regles.md
couvre: server.py
---
# Outils MCP de `server.py`

Le client Obsidian est `server.client` (`ObsidianClient`). Les prompts et la resource sont décrits dans `memoire/architecture.md`.

## Lecture
| Outil | Comportement |
|---|---|
| `search_notes(query)` | Recherche simple ; garde 20 résultats max, 3 extraits chacun. Renvoie `{path, score, matches}`. |
| `read_notes(path)` | Contenu markdown d'une note. |
| `read_many_notes(paths)` | Lit les 20 premiers chemins ; renvoie `{chemin: contenu}`. Au-delà, clé `_avertissement` listant les chemins ignorés. |
| `list_notes(folder="")` | Liste d'un dossier (sous-dossiers finissant par `/`). |
| `search_by_name(name)` | Parcourt tout le vault (`list_all`, récursif) ; renvoie les chemins contenant `name` (insensible à la casse). |
| `get_outgoing_links(path)` | Pour chaque lien `[[...]]` : `{link, path (wiki/<lien>.md), exists}`. |
| `get_backlinks(path)` | Exige un chemin `wiki/....md` (sinon `RuleError`). Cherche `link_name(path)`, lit les pages `wiki/*.md` candidates, renvoie celles qui ont un lien résolu vers `path`. |
| `lint_wiki()` | Lit toutes les pages `wiki/*.md` (`load_wiki`) et renvoie `links.lint(...)` (voir `memoire/liens.md`). Ne modifie rien. |

## Écriture (règles dans `memoire/regles.md`)
| Outil | Comportement |
|---|---|
| `create_note(path, content, confirm_new_folder=False)` | Vérifie chemin et contenu ; refuse si la page existe (« utiliser update_note ») ou si le dossier n'existe pas, sauf `confirm_new_folder=True`. |
| `update_note(path, content, expected_content)` | Vérifie chemin, ajout seul, contenu ; refuse si le contenu actuel diffère de `expected_content` (`same_content`) ; puis remplace la page. |
| `append_log(type, title, details)` | Formate l'entrée (`format_log_entry`, date du jour) et l'ajoute à `wiki/log.md` en garantissant une ligne vide avant. |

## Point d'attention
- `list_all` et `load_wiki` ne sont pas des outils : fonctions internes.

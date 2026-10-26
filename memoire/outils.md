# Outils MCP (server.py)

Les erreurs de règle sont des `RuleError` (message transmis au modèle). Les erreurs réseau sont des `ObsidianError`. Détail des règles : `regles.md`. Détail des liens : `liens.md`.

## Lecture
| Outil | Paramètres | Comportement |
|---|---|---|
| `search_notes` | `query` | Recherche simple Obsidian. Garde 20 résultats max, 3 extraits (`context`) par résultat. Renvoie `{path, score, matches}`. |
| `read_notes` | `path` | Renvoie le markdown de la note. |
| `read_many_notes` | `paths` | Lit au plus 20 notes (`paths[:20]`). Renvoie `{chemin: contenu}`. Au-delà, ajoute la clé `_avertissement` qui liste les chemins ignorés. |
| `list_notes` | `folder=""` | Liste un niveau : fichiers et sous-dossiers (finissent par `/`). |
| `search_by_name` | `name` | Parcourt tout le vault (`list_all`) et garde les chemins contenant `name`, casse ignorée. |

## Liens et contrôle
| Outil | Paramètres | Comportement |
|---|---|---|
| `get_outgoing_links` | `path` | Pour chaque `[[lien]]` de la page : `{link, path, exists}`. |
| `get_backlinks` | `path` | `path` doit être une page `wiki/...md`, sinon `RuleError`. Cherche `link_name(path)` via `search`, ne lit que les candidats `wiki/*.md` (hors la page elle-même), puis filtre avec `links.backlinks`. |
| `lint_wiki` | aucun | Lit toutes les pages de `wiki/` et renvoie le rapport de `links.lint`. Ne modifie rien. |

## Écriture (limitée à `wiki/`)
| Outil | Paramètres | Comportement |
|---|---|---|
| `create_note` | `path, content, confirm_new_folder=False` | Crée la page. Refuse si elle existe déjà (→ `update_note`) ou si le dossier est nouveau sans `confirm_new_folder=True`. Ordre des contrôles : `regles.md`. |
| `update_note` | `path, content, expected_content` | Écrase la page si `expected_content` correspond au contenu actuel. Ordre des contrôles : `regles.md`. |
| `append_log` | `type, title, details` | Ajoute une entrée à `wiki/log.md` avec la date du jour. Le log doit exister (sinon 404). Laisse exactement une ligne vide avant l'entrée. |

Format d'une entrée de log : `## [AAAA-MM-JJ] type | titre`, ligne vide, `details`.

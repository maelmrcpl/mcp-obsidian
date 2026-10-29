---
quand_lire: Tu écris ou modifies du code ; tu dois lancer les tests, le lint ou le build ; tu hésites sur un choix de conception ou de nommage
couvre:
---
# Principes et commandes du projet

## Commandes
Ces commandes servent de critère de succès (voir AGENTS.md §4) : lance-les avant de conclure une tâche de code.
| Action | Commande |
|---|---|
| Tests | `.venv\Scripts\python.exe -m pytest` (69 tests, aucun Obsidian réel requis) |
| Lint / format | `à compléter` (aucune configuration trouvée) |
| Build / lancement | Lancement : `.venv\Scripts\python.exe server.py` (serveur MCP sur stdio, via `mcp.run()`). Build : `à compléter` |

## Principes non négociables
- Aucun secret dans le code : la clé d'API vient du `.env` (`KEY`), jamais lu ni affiché.
- Le serveur n'écrit que dans `wiki/` ; `raw/` est en lecture seule (vérifié par `check_path` dans `rules.py`).
- Toute règle d'écriture ou de lien ajoutée est couverte par un test (voir `memoire/tests.md`).

## Conventions de code
- Python, un outil MCP = une fonction décorée `@mcp.tool()` dans `server.py`, avec une docstring en français qui sert de description.
- Les refus de règle sont des `RuleError` (sous-classe de `ToolError`) dont le message est transmis au modèle ; les erreurs HTTP sont des `ObsidianError`.
- Logique pure (règles, liens) dans `rules.py` et `links.py`, sans appel réseau ; les appels à Obsidian passent par `ObsidianClient`.
- Messages et docstrings en français ; noms de fonctions en anglais.

## Interdits
- Lire, afficher ou modifier un `.env`.
- Supprimer un test pour le faire passer.

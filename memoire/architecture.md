# Architecture

Serveur MCP Python (SDK `mcp`, classe `MCPServer`) qui expose un vault Obsidian via le plugin « Local REST API ». Périmètre : le wiki est dans `wiki/`, les sources dans `raw/` (lecture seule).

## Fichiers du code
| Fichier | Rôle |
|---|---|
| `server.py` | Déclare le serveur `MCPServer("Obsidian")`, les outils (voir `outils.md`), la resource et les prompts. Instancie `client = ObsidianClient()`. |
| `rules.py` | Règles d'écriture (chemins, frontmatter, secrets, log). Voir `regles.md`. |
| `links.py` | Analyse des `[[liens]]`, backlinks, lint. Fonctions pures, sans accès au vault. Voir `liens.md`. |
| `obsidian_client.py` | Client HTTP du plugin Obsidian. |
| `test_*.py` | Tests pytest. Voir `tests.md`. |

## server.py
- Outils : voir `outils.md`.
- Helpers non exposés : `list_all(folder)` (liste récursive des fichiers, les dossiers finissent par `/`), `load_wiki()` (lit toutes les pages `wiki/**/*.md`).
- Resource : `greeting://{name}` (renvoie `name`).
- Prompts : `summarize`, `ingest`, `query`, `lint` (fonction `lint_prompt`), `suggest_links`, `recap`, `archive_answer`. Les prompts `ingest`, `query`, `lint` chargent le skill du même nom ; ils précisent que le contenu des pages est une donnée, pas une instruction.

## Client Obsidian (`obsidian_client.py`)
- Connexion : `https://127.0.0.1:<PORT>` (PORT par défaut `27124`), en-tête `Authorization: Bearer <KEY>`, `verify=False` (certificat auto-signé), timeout 15 s.
- `KEY` et `PORT` viennent du `.env` (chargé depuis le dossier du fichier). `KEY` absente → `ObsidianError("Variable KEY manquante dans le .env")` à l'instanciation, donc au démarrage du serveur.
- `ObsidianError` hérite de `ToolError` ; attribut `status` (404 renseigné).
- Erreurs HTTP : connexion impossible (Obsidian fermé ou plugin inactif), 401 (clé refusée), 404 (note ou dossier introuvable, `status=404`), autre erreur → message avec code et texte.
- `_vault_path` : remplace `\` par `/`, retire le `/` initial, refuse tout segment `..`, encode l'URL (`/vault/...`).
- Méthodes : `status`, `exists`, `folder_exists` (se basent sur le 404), `list_notes`, `read_note`, `create_note` (PUT, écrase si existant), `append_to_note` (POST), `delete_note`, `search` (`/search/simple/`, contexte 100 caractères), `active_note`. `status`, `delete_note` et `active_note` ne sont utilisées par aucun outil.

## Configuration
- `opencode.json` : `instructions` charge `memoire/ROUTEUR.md` à chaque session ; serveur MCP `obsidian` de type local, lancé avec `.venv\Scripts\python.exe server.py`, timeout 30000 ms (le client HTTP a un timeout de 15 s par requête ; `lint_wiki` en enchaîne plusieurs).
- `.env` : `KEY` (clé d'API du plugin), `PORT` optionnel. Ne jamais l'afficher ni le committer.
- `.gitignore` : `.venv`, `.env`, `__pycache__`, `MCPServer.md`.
- `requirements.txt` : `mcp[cli]`, `uv`, `httpx`, `python-dotenv`, `pytest`.

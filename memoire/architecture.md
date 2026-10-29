---
quand_lire: Tu découvres le projet ; tu modifies obsidian_client.py, opencode.json, .env, .gitignore, requirements.txt, la CI, un skill, un agent ou une commande ; tu ajoutes ou changes un prompt ou une resource ; une erreur de connexion, de clé (KEY, 401), de port (PORT) ou de note introuvable (404) apparaît ; tu ajoutes un fichier de mémoire
couvre: obsidian_client.py, opencode.json, .gitignore, requirements.txt, .github/workflows/memoire.yml, .opencode/
---
# Architecture

Serveur MCP Python (SDK `mcp`, classe `MCPServer`) qui donne à un modèle l'accès à un vault Obsidian via le plugin « Local REST API ». Le vault suit une organisation `raw/` (sources, lecture seule) et `wiki/` (pages écrites par le serveur). Le point d'entrée est `server.py` (`main()` appelle `mcp.run()`).

## Fichiers du code
| Fichier | Rôle |
|---|---|
| `server.py` | Déclare les outils, la resource et les prompts (détail des outils : `memoire/outils.md`). |
| `obsidian_client.py` | `ObsidianClient` : client HTTP (`httpx`) du plugin. Méthodes : `status`, `exists`, `folder_exists`, `list_notes`, `read_note`, `create_note` (PUT, écrase si existe), `append_to_note` (POST), `delete_note`, `search`, `active_note`. |
| `rules.py` | Règles d'écriture (`memoire/regles.md`). |
| `links.py` | Liens et lint (`memoire/liens.md`). |
| `test_*.py` | Tests (`memoire/tests.md`). |
| `requirements.txt` | `mcp[cli]`, `uv`, `httpx`, `python-dotenv`, `pytest`. |
| `opencode.json` | Charge `memoire/ROUTEUR.md`, déclare le serveur MCP `obsidian`, bloque la lecture et l'édition des `.env`, demande confirmation avant `git push`, `git reset --hard`, `git clean` et les suppressions. |
| `.github/workflows/memoire.yml` | Lance `scripts/routeur.ps1 -Verifier` à chaque push et pull request. |
| `.opencode/skills/` | Skills `onboard`, `plan`, `review`, `save-session`. |
| `.opencode/agents/reviewer.md` | Sous-agent relecteur en lecture seule. |
| `.opencode/commands/` | Commandes `/onboard`, `/plan`, `/review`, `/save-session`. |

## Connexion à Obsidian
- `obsidian_client.py` charge `.env` (à côté du fichier) avec `python-dotenv` ; variables `KEY` (obligatoire) et `PORT` (défaut `27124`). Ne jamais lire `.env`.
- URL : `https://127.0.0.1:<PORT>`, en-tête `Authorization: Bearer <KEY>`, `verify=False` (certificat auto-signé du plugin), timeout 15 s.
- Chemins : `\` converti en `/`, `..` refusé (`Chemin invalide`), encodage URL.
- Erreurs (`ObsidianError`, sous-classe de `ToolError`) : `KEY` absente ; connexion impossible (Obsidian fermé ou plugin inactif) ; 401 « Clé d'API refusée » ; 404 « Note ou dossier introuvable » (`status=404`) ; autre erreur HTTP avec code et texte.

## Prompts et resource (dans `server.py`)
- Resource `greeting://{name}` renvoie `name`.
- Prompts : `summarize`, `ingest`, `query`, `lint` (fonction `lint_prompt`), `suggest_links`, `recap` (période par défaut « 7 jours »), `archive_answer`. Ceux du wiki renvoient un texte qui demande de charger le skill du même nom ou décrit les étapes ; ils précisent que le contenu des pages est de la donnée.

## Configuration
- `.gitignore` : `.venv`, `.env`, `__pycache__`, `MCPServer.md`, `.pytest_cache/`, `node_modules/`.
- `memoire/_ignore.txt` : fichiers suivis par Git exemptés de la vérification « couvert par la mémoire ».
- `scripts/routeur.ps1` : génère `memoire/ROUTEUR.md` ; seuils de budget en tête de script (`$maxChargeEnPermanence`, `$maxFichierMemoire`).
- Incohérence à noter : `opencode.json` référence `C:\Users\HTTN6172\Documents\mcp-obsidian\` (venv, `server.py`, un second `ROUTEUR.md`), un dossier différent de ce projet (`mcp-obsidian-test`).

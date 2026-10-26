# Tests

Lancer : `.venv\Scripts\python.exe -m pytest` à la racine du projet. Aucun Obsidian réel n'est nécessaire.

| Fichier | Couvre | Méthode |
|---|---|---|
| `test_rules.py` | `check_path` (valides, refusés, message kebab-case), `check_content` (frontmatter manquant, champ manquant, type invalide, préfixe `wiki/`, secret). `check_not_append_only` et `same_content` n'ont pas de test direct : ils sont couverts via `test_server.py`. | Appels directs, `pytest.mark.parametrize` pour les chemins. |
| `test_links.py` | `extract_links` (alias, ancre, embed, code, pipe échappé, doublons), `resolve`, `link_name`, `backlinks`, `lint` (une fonction de test par clé du rapport, pages de base) | Dictionnaires `{chemin: contenu}` en mémoire. |
| `test_server.py` | Outils d'écriture et de lecture (`create_note`, `update_note`, `append_log`, `search_notes`, `read_many_notes`, `get_outgoing_links`, `get_backlinks`, `lint_wiki`) et prompts (noms enregistrés, contenu de `suggest_links`, `recap`, `ingest`, `query`, `lint_prompt`, `archive_answer`) | `FakeClient` remplace `server.client` via `monkeypatch` (fixture `fake`). |

## Conventions
- Une règle ajoutée dans `rules.py` → un test dans `test_rules.py` (fonction pure, sauf pour `check_not_append_only` et `same_content`, testés via `test_server.py`) et un test dans `test_server.py` si l'outil change de comportement.
- Une règle de lien ou de lint ajoutée dans `links.py` → un test dans `test_links.py`.
- Un outil ou un prompt ajouté ou modifié dans `server.py` → un test dans `test_server.py` (le test des prompts vérifie leurs noms enregistrés).
- Un test qui échoue après une modification de code : corriger le code ou le test selon la règle voulue, jamais supprimer le test pour le faire passer.

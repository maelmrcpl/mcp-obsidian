---
quand_lire: Tu écris, lances ou corriges un test_*.py ; tu viens de modifier du code et dois savoir quel test ajouter
couvre: test_rules.py, test_links.py, test_server.py
---
# Tests

Lancer : `.venv\Scripts\python.exe -m pytest` à la racine (69 tests au dernier passage, tous verts). Aucun Obsidian réel n'est nécessaire.

| Fichier | Couvre | Méthode |
|---|---|---|
| `test_rules.py` | `check_path`, `check_content` (frontmatter, champs, type, préfixe `wiki/`, secret). | Appels directs, `pytest.mark.parametrize` pour les chemins. |
| `test_links.py` | `extract_links`, `resolve`, `link_name`, `backlinks`, `lint`. | Dictionnaires `{chemin: contenu}` en mémoire. |
| `test_server.py` | Outils d'écriture et de lecture, prompts. | Classe `FakeClient` qui remplace `server.client` via `monkeypatch` (fixture `fake`). |

## Conventions
- Une règle ajoutée dans `rules.py` → un test dans `test_rules.py` et, si un outil change de comportement, un test dans `test_server.py`.
- Une règle de lien ou de lint ajoutée dans `links.py` → un test dans `test_links.py`.
- Un outil ou un prompt ajouté ou modifié dans `server.py` → un test dans `test_server.py`.
- Un test qui échoue après une modification : corriger le code ou le test selon la règle voulue, jamais supprimer le test pour le faire passer.

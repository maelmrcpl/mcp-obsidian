---
quand_lire: Tu modifies rules.py ; un refus d'écriture apparaît (Chemin invalide, Champs manquants, type invalide, a changé depuis, ajout seul, dossier n'existe pas, secret) ; tu utilises create_note, update_note ou append_log ; on te demande une règle d'écriture appliquée par le serveur. Pour le comportement de l'outil lui-même, lis aussi memoire/outils.md
couvre: rules.py
---
# Règles d'écriture (`rules.py`)

Toute violation lève `RuleError` (sous-classe de `ToolError` et `ValueError`) ; le message est transmis au modèle.

## Chemin (`check_path`)
- Refusé (« Chemin invalide ») : chemin commençant par `/`, contenant `..` ou `:` (`\` converti en `/`).
- `raw/` : « `raw/` est en lecture seule ». Hors `wiki/` : « Ecriture limitée à `wiki/` ».
- Doit finir par `md` (casse ignorée), nom de fichier en kebab-case `[a-z0-9]+(-[a-z0-9]+)*.md`.

## Contenu (`check_content`)
- Frontmatter `---` obligatoire avec les champs `title, type, created, updated, sources, tags` (« Champs manquants : ... »). Types admis : `source, feature, product, persona, concept, style, analysis, tool`.
- Pages de base `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`, `wiki/glossary.md` : pas de contrôle de frontmatter.
- Texte contenant `[[wiki/` refusé (lien avec préfixe).
- Secret probable refusé (`check_secrets`, regex insensible à la casse) : `authorization:`, `bearer <valeur>`, `token=`, `session_id=` / `sessionid=`.

## Autres règles
- `wiki/log.md` est en ajout seul (`check_not_append_only`) : `update_note` le refuse, utiliser `append_log`.
- `same_content(a, b)` : compare après normalisation `\r\n` → `\n` et `strip()` ; sert au contrôle `expected_content` de `update_note`.
- Dossier inexistant pour `create_note` : refus, sauf `confirm_new_folder=True` (contrôlé dans `server.py`).
- Log (`format_log_entry`) : type parmi `ingest, query, lint, maintenance` ; titre non vide sur une seule ligne ; secrets refusés dans `details` ; format `## [AAAA-MM-JJ] type | titre`, ligne vide, détails.

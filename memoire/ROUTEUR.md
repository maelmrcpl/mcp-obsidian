# ROUTEUR DE MÉMOIRE

> Fichier généré par `scripts/routeur.ps1` : ne pas le modifier à la main. Modifier l'en-tête `quand_lire` du fichier concerné, puis relancer le script.

Index de `memoire/` : une ligne par fichier, avec le moment où le lire. Ce fichier ne contient aucune connaissance du projet. Chemins relatifs à la racine.

## 1. Fichiers de mémoire
Lis un fichier quand la tâche correspond à sa colonne « Quand le lire ». Plusieurs peuvent s'appliquer. Un fichier déjà lu dans la session et non modifié depuis ne se relit pas.

| Fichier | Quand le lire |
|---|---|
| `memoire/architecture.md` | Tu découvres le projet ; tu modifies obsidian_client.py, opencode.json, .env, .gitignore, requirements.txt, la CI, un skill, un agent ou une commande ; tu ajoutes ou changes un prompt ou une resource ; une erreur de connexion, de clé (KEY, 401), de port (PORT) ou de note introuvable (404) apparaît ; tu ajoutes un fichier de mémoire |
| `memoire/liens.md` | Tu modifies links.py ; tu touches lint_wiki, get_backlinks ou get_outgoing_links ; une question porte sur un lien, une page orpheline ou un doublon de nom |
| `memoire/outils.md` | Tu ajoutes, modifies ou débogues un outil de server.py ; on te demande ce que fait ou renvoie un outil. Pour create_note, update_note et append_log, lis aussi memoire/regles.md |
| `memoire/principes.md` | Tu écris ou modifies du code ; tu dois lancer les tests, le lint ou le build ; tu hésites sur un choix de conception ou de nommage |
| `memoire/regles.md` | Tu modifies rules.py ; un refus d'écriture apparaît (Chemin invalide, Champs manquants, type invalide, a changé depuis, ajout seul, dossier n'existe pas, secret) ; tu utilises create_note, update_note ou append_log ; on te demande une règle d'écriture appliquée par le serveur. Pour le comportement de l'outil lui-même, lis aussi memoire/outils.md |
| `memoire/tests.md` | Tu écris, lances ou corriges un test_*.py ; tu viens de modifier du code et dois savoir quel test ajouter |

Aucune ligne ne correspond : lis `memoire/architecture.md`, avertis l'utilisateur que la tâche n'est pas couverte par le routeur et n'invente rien.

## 2. Cohérence
- Un fait de la mémoire qui contredit le code est une erreur de la mémoire : corrige-la et signale-la à l'utilisateur.
- Un chemin listé ici qui n'existe pas : signale-le à l'utilisateur.

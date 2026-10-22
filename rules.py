import re

def check_path(path: str):
    path = path.replace("\\", "/")
    if path.startswith("/") or ".." in path or ":" in path:
        raise ValueError("Chemin invalide")
    if path.startswith("raw/"):
        raise ValueError("`raw/` est en lecture seule")
    if not path.startswith("wiki/"):
        raise ValueError("Ecriture limitée à `wiki/`")
    if path[-2:].lower() != "md":
        raise ValueError("Une page doit finir par .md")
    file = path.split("/")[-1]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.md", file):
        raise ValueError("Nom en kebab-base attendu : exemple-fichier.md")

TYPES = {"source", "feature", "product", "persona", "concept", "style", "analysis", "tool"}
FIELDS = ["title", "type", "created", "updated", "sources", "tags"]
SECRETS = re.compile(r"authorization\s*:|bearer\s+\S+|token\s*=|session_?id\s*=", re.I)

def check_content(content: str):
    m = re.match(r"---\r?\n(.*?)\r?\n---", content, re.S)
    if not m:
        raise ValueError("Frontmatter manquant")
    fm = dict(re.findall(r"^(\w+)\s*:\s*(.*)$", m.group(1), re.M))
    missing = [f for f in FIELDS if f not in fm]
    if missing:
        raise ValueError(f"Champs manquants : {', '.join(missing)}")
    if fm["type"].strip() not in TYPES:
        raise ValueError(f"type invalide, attendu : {sorted(TYPES)}")
    if "[[wiki/" in content:
        raise ValueError("Lien avec préfixe wiki/ interdit")
    if SECRETS.search(content):
        raise ValueError("Le contenu ressemble à un secret, écriture refusée")

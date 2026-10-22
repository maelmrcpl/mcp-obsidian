import re
from mcp.server.mcpserver.exceptions import ToolError


class RuleError(ToolError, ValueError):
    "Règle du wiki non respectée (le message est transmis au modèle)"


def check_path(path: str):
    path = path.replace("\\", "/")
    if path.startswith("/") or ".." in path or ":" in path:
        raise RuleError("Chemin invalide")
    if path.startswith("raw/"):
        raise RuleError("`raw/` est en lecture seule")
    if not path.startswith("wiki/"):
        raise RuleError("Ecriture limitée à `wiki/`")
    if path[-2:].lower() != "md":
        raise RuleError("Une page doit finir par .md")
    file = path.split("/")[-1]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.md", file):
        raise RuleError("Nom en kebab-base attendu : exemple-fichier.md")

TYPES = {"source", "feature", "product", "persona", "concept", "style", "analysis", "tool"}
FIELDS = ["title", "type", "created", "updated", "sources", "tags"]
SECRETS = re.compile(r"authorization\s*:|bearer\s+\S+|token\s*=|session_?id\s*=", re.I)

def check_secrets(text: str):
    if SECRETS.search(text):
        raise RuleError("Le contenu ressemble à un secret, écriture refusée")

def check_frontmatter(content: str):
    m = re.match(r"---\r?\n(.*?)\r?\n---", content, re.S)
    if not m:
        raise RuleError("Frontmatter manquant")
    fm = dict(re.findall(r"^(\w+)\s*:\s*(.*)$", m.group(1), re.M))
    missing = [f for f in FIELDS if f not in fm]
    if missing:
        raise RuleError(f"Champs manquants : {', '.join(missing)}")
    if fm["type"].strip() not in TYPES:
        raise RuleError(f"type invalide, attendu : {sorted(TYPES)}")

def check_content(content: str):
    check_frontmatter(content)
    if "[[wiki/" in content:
        raise RuleError("Lien avec préfixe wiki/ interdit")
    check_secrets(content)

LOG_TYPES = {"ingest", "query", "lint", "maintenance"}

def format_log_entry(type: str, title: str, details: str, date: str) -> str:
    if type not in LOG_TYPES:
        raise RuleError(f"type de log invalide, attendu : {sorted(LOG_TYPES)}")
    if not title.strip() or "\n" in title:
        raise RuleError("Le titre doit tenir sur une ligne et ne pas être vide")
    check_secrets(details)
    return f"## [{date}] {type} | {title.strip()}\n\n{details.strip()}\n"

def same_content(a: str, b: str) -> bool:
    norm = lambda s: s.replace("\r\n", "\n").strip()
    return norm(a) == norm(b)

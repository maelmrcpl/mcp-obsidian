from datetime import date

from mcp.server import MCPServer

from obsidian_client import ObsidianClient
from links import backlinks, extract_links, lint, link_name, resolve
from rules import RuleError, check_content, check_path, format_log_entry, same_content

mcp = MCPServer("Obsidian")
client = ObsidianClient()

@mcp.tool()
def search_notes(query: str) -> list:
    "Recherche du texte dans les notes du vault (20 résultats max, 3 extraits chacun)"
    results = client.search(query)[:20]
    return [
        {
            "path": r["filename"],
            "score": r.get("score"),
            "matches": [m["context"] for m in r.get("matches", [])[:3]],
        }
        for r in results
    ]

@mcp.tool()
def read_notes(path: str) -> str:
    "Lis le contenu markdown d'une note"
    return client.read_note(path)

@mcp.tool()
def read_many_notes(paths: list[str]) -> dict:
    "Lis jusqu'à 20 notes en un seul appel"
    return {p: client.read_note(p) for p in paths[:20]}

@mcp.tool()
def list_notes(folder: str = "") -> list:
    "Liste les notes et sous-dossiers"
    return client.list_notes(folder)

def list_all(folder: str = "") -> list:
    files = []
    for entry in client.list_notes(folder):
        if entry.endswith("/"):
            files += list_all(folder + entry)
        else:
            files.append(folder + entry)
    return files

@mcp.tool()
def search_by_name(name: str) -> list:
    "Trouve les notes dont le chemin contient le texte donné"
    return [f for f in list_all() if name.lower() in f.lower()]

@mcp.tool()
def get_outgoing_links(path: str) -> list:
    "Liste les liens [[...]] d'une page, avec le chemin visé et s'il existe"
    return [
        {"link": link, "path": resolve(link), "exists": client.exists(resolve(link))}
        for link in extract_links(client.read_note(path))
    ]

@mcp.tool()
def get_backlinks(path: str) -> list:
    "Liste les pages de wiki/ qui contiennent un lien vers la page donnée (ex: wiki/concepts/agile.md)"
    if not path.startswith("wiki/") or not path.endswith(".md"):
        raise RuleError("Donner un chemin de page de wiki/, ex: wiki/concepts/agile.md")
    found = client.search(link_name(path))
    candidates = {r["filename"] for r in found if r["filename"].startswith("wiki/") and r["filename"].endswith(".md")}
    pages = {p: client.read_note(p) for p in candidates if p != path}
    return backlinks(pages, path)

def load_wiki() -> dict:
    return {p: client.read_note(p) for p in list_all("wiki/") if p.endswith(".md")}

@mcp.tool()
def lint_wiki() -> dict:
    "Contrôle le wiki sans rien modifier : liens cassés, préfixes wiki/, doublons non qualifiés, orphelines, pages absentes de l'index, frontmatter invalide"
    return lint(load_wiki())

@mcp.tool()
def create_note(path: str, content: str, confirm_new_folder: bool = False) -> str:
    "Crée une page dans wiki/ (frontmatter obligatoire). Refuse si elle existe déjà ou si le dossier est nouveau, sauf confirm_new_folder=True après accord de l'utilisateur"
    check_path(path)
    check_content(content)
    if client.exists(path):
        raise RuleError(f"{path} existe déjà : utiliser update_note")
    folder = path.rsplit("/", 1)[0]
    if not confirm_new_folder and not client.folder_exists(folder):
        raise RuleError(f"Le dossier {folder} n'existe pas : demander l'accord de l'utilisateur puis passer confirm_new_folder=True")
    client.create_note(path, content)
    return f"Page {path} créée"

@mcp.tool()
def update_note(path: str, content: str, expected_content: str) -> str:
    "Remplace une page de wiki/. expected_content doit être le contenu actuel (à relire juste avant), sinon l'écriture est refusée"
    check_path(path)
    check_content(content)
    if not same_content(client.read_note(path), expected_content):
        raise RuleError(f"{path} a changé depuis la dernière lecture : la relire avant de la modifier")
    client.create_note(path, content)
    return f"Page {path} mise à jour"

@mcp.tool()
def append_log(type: str, title: str, details: str) -> str:
    "Ajoute une entrée à la fin de wiki/log.md. type : ingest, query, lint ou maintenance. details : corps de l'entrée en texte libre"
    entry = format_log_entry(type, title, details, date.today().isoformat())
    log = client.read_note("wiki/log.md")
    trailing = len(log) - len(log.rstrip("\n"))
    client.append_to_note("wiki/log.md", "\n" * max(0, 2 - trailing) + entry)
    return f"Entrée {type} ajoutée au log"

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    return f"{name}"

@mcp.prompt()
def summarize(text: str) -> str:
    return f"Summarize this text in one or two sentences:\n\n--\n\n{text}"

def main():
    mcp.run()

if __name__=="__main__":
    main()

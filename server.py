from datetime import date

from mcp.server import MCPServer

from obsidian_client import ObsidianClient
from rules import RuleError, check_content, check_path, format_log_entry, same_content

mcp = MCPServer("Obsidian")
client = ObsidianClient()

@mcp.tool()
def search_notes(query: str) -> list:
    "Recherche du texte dans les notes du vault"
    return client.search(query)

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
    client.append_to_note("wiki/log.md", entry)
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

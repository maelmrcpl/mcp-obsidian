from mcp.server import MCPServer
from obsidian_client import ObsidianClient
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
def list_notes(folder: str = "") -> list:
    "Liste les notes et sous-dossiers"
    return client.list_notes(folder)

@mcp.tool()
def create_note(path: str, content: str) -> str:
    "Crée une note (écrase son contenu si elle existe déjà)"
    client.create_note(path, content)
    return f"Note {path} créée"

@mcp.tool()
def append_to_note(path: str, content: str) -> str:
    "Ajoute du texte à la fin d'une note"
    client.append_to_note(path, content)
    return f"Texte ajouté à {path}"

@mcp.tool()
def read_notes(paths: list[str]) -> dict:
    "Lis jusqu'à 20 notes en un 1 appel"
    return {p: client.read_note(p) for p in paths[:20]}

@mcp.tool()
def list_all(folder=""):
    files = []
    for entry in client.list_notes(folder):
        if entry.endswith("/"):
            files += list_all(folder + entry)
        else:
            files.append(folder + entry)
    return files

@mcp.tool()
def search_by_notes(name: str) -> list:
    return [f for f in list_all() if name.lower() in f.lower()]

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
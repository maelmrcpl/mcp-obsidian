from mcp.server import MCPServer

mcp = MCPServer("Obsidian")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a+b

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
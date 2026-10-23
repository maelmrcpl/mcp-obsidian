import re

from rules import BASE_PAGES, RuleError, check_frontmatter
INDEX = "wiki/index.md"
LINK = re.compile(r"!?\[\[([^\]\n]+)\]\]")


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def extract_links(text: str) -> list:
    "Cibles des liens [[...]] d'une page, sans alias ni ancre, hors blocs de code"
    links = []
    for raw in LINK.findall(strip_code(text)):
        target = raw.split("|")[0].split("#")[0].strip().rstrip("\\").strip()
        if target and target not in links:
            links.append(target)
    return links


def resolve(link: str) -> str:
    "[[concepts/agile]] -> wiki/concepts/agile.md (relatif à wiki/, sans nom seul)"
    return f"wiki/{link}.md"


def link_name(path: str) -> str:
    "wiki/concepts/agile.md -> concepts/agile"
    return path[len("wiki/"):-len(".md")]


def backlinks(pages: dict, path: str) -> list:
    return sorted(
        p for p, content in pages.items()
        if p != path and any(resolve(link) == path for link in extract_links(content))
    )


def lint(pages: dict) -> dict:
    "pages : {chemin: contenu} de toutes les pages de wiki/. Ne modifie rien."
    report = {
        "liens_casses": [],
        "liens_prefixe_wiki": [],
        "doublons_non_qualifies": [],
        "orphelines": [],
        "absentes_de_lindex": [],
        "frontmatter_invalide": [],
    }

    names = {}
    for p in pages:
        names.setdefault(p.rsplit("/", 1)[-1][:-3], []).append(p)
    duplicated = {n for n, paths in names.items() if len(paths) > 1}

    inbound = {p: set() for p in pages}
    for page, content in sorted(pages.items()):
        for link in extract_links(content):
            target = resolve(link)
            if link.startswith("wiki/"):
                report["liens_prefixe_wiki"].append({"page": page, "lien": link})
            elif target in pages:
                if target != page:
                    inbound[target].add(page)
            elif "/" not in link and link in duplicated:
                report["doublons_non_qualifies"].append({"page": page, "lien": link, "candidats": sorted(names[link])})
            else:
                report["liens_casses"].append({"page": page, "lien": link})

    for page, content in sorted(pages.items()):
        if page in BASE_PAGES:
            continue
        if not (inbound[page] - {INDEX}):
            report["orphelines"].append(page)
        if INDEX not in inbound[page]:
            report["absentes_de_lindex"].append(page)
        try:
            check_frontmatter(content)
        except RuleError as e:
            report["frontmatter_invalide"].append({"page": page, "erreur": str(e)})

    return report

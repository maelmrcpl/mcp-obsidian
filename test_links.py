from links import backlinks, extract_links, lint, link_name, resolve

FM = "---\ntitle: T\ntype: concept\ncreated: 2026-10-22\nupdated: 2026-10-22\nsources: []\ntags: []\n---\n"


def page(body):
    return FM + body


def test_extract_simple_alias_anchor_embed():
    text = "[[concepts/a]] [[concepts/b|Mon alias]] [[concepts/c#titre]] ![[concepts/d]] [[#local]]"
    assert extract_links(text) == ["concepts/a", "concepts/b", "concepts/c", "concepts/d"]


def test_extract_ignores_code_blocks():
    text = "```\n[[filename]]\n```\net `[[inline]]` puis [[concepts/vrai]]"
    assert extract_links(text) == ["concepts/vrai"]


def test_extract_escaped_pipe_in_table():
    assert extract_links(r"| [[concepts/a\|alias]] |") == ["concepts/a"]


def test_extract_deduplicates():
    assert extract_links("[[concepts/a]] et encore [[concepts/a]]") == ["concepts/a"]


def test_resolve_and_link_name():
    assert resolve("concepts/agile") == "wiki/concepts/agile.md"
    assert link_name("wiki/concepts/agile.md") == "concepts/agile"
    assert link_name("wiki/overview.md") == "overview"


def test_backlinks():
    pages = {
        "wiki/concepts/a.md": page("voir [[concepts/b]]"),
        "wiki/concepts/b.md": page("voir [[concepts/a|alias]] et [[concepts/b]]"),
        "wiki/concepts/c.md": page("mention concepts/b sans lien"),
    }
    assert backlinks(pages, "wiki/concepts/b.md") == ["wiki/concepts/a.md"]
    assert backlinks(pages, "wiki/concepts/a.md") == ["wiki/concepts/b.md"]


def healthy_wiki():
    return {
        "wiki/index.md": "# Index\n- [[concepts/a]]\n- [[concepts/b]]\n```\n[[filename]]\n```\n",
        "wiki/log.md": "# Log\n",
        "wiki/concepts/a.md": page("voir [[concepts/b]]"),
        "wiki/concepts/b.md": page("voir [[concepts/a]]"),
    }


def test_lint_clean_wiki():
    report = lint(healthy_wiki())
    assert all(v == [] for v in report.values()), report


def test_lint_broken_link():
    pages = healthy_wiki()
    pages["wiki/concepts/a.md"] = page("voir [[concepts/fantome]]")
    report = lint(pages)
    assert report["liens_casses"] == [{"page": "wiki/concepts/a.md", "lien": "concepts/fantome"}]


def test_lint_orphan_and_missing_from_index():
    pages = healthy_wiki()
    pages["wiki/concepts/seule.md"] = page("personne ne me lie")
    report = lint(pages)
    assert report["orphelines"] == ["wiki/concepts/seule.md"]
    assert report["absentes_de_lindex"] == ["wiki/concepts/seule.md"]


def test_lint_page_only_in_index_is_not_orphan_but_listed():
    pages = healthy_wiki()
    pages["wiki/concepts/c.md"] = page("liée seulement par l'index")
    pages["wiki/index.md"] += "- [[concepts/c]]\n"
    report = lint(pages)
    assert report["orphelines"] == ["wiki/concepts/c.md"]
    assert report["absentes_de_lindex"] == []


def test_lint_page_linked_but_not_in_index():
    pages = healthy_wiki()
    pages["wiki/concepts/c.md"] = page("liée par a")
    pages["wiki/concepts/a.md"] = page("voir [[concepts/b]] et [[concepts/c]]")
    report = lint(pages)
    assert report["orphelines"] == []
    assert report["absentes_de_lindex"] == ["wiki/concepts/c.md"]


def test_lint_invalid_frontmatter():
    pages = healthy_wiki()
    pages["wiki/concepts/a.md"] = "pas de frontmatter [[concepts/b]]"
    report = lint(pages)
    assert report["frontmatter_invalide"] == [{"page": "wiki/concepts/a.md", "erreur": "Frontmatter manquant"}]


def test_lint_wiki_prefix_link():
    pages = healthy_wiki()
    pages["wiki/concepts/a.md"] = page("voir [[wiki/concepts/b]]")
    report = lint(pages)
    assert report["liens_prefixe_wiki"] == [{"page": "wiki/concepts/a.md", "lien": "wiki/concepts/b"}]
    assert report["liens_casses"] == []


def test_lint_unqualified_duplicate_name():
    pages = healthy_wiki()
    pages["wiki/sources/a.md"] = page("source")
    pages["wiki/index.md"] += "- [[sources/a]]\n"
    pages["wiki/concepts/b.md"] = page("voir [[a]]")
    report = lint(pages)
    assert report["doublons_non_qualifies"] == [
        {"page": "wiki/concepts/b.md", "lien": "a", "candidats": ["wiki/concepts/a.md", "wiki/sources/a.md"]}
    ]
    assert report["liens_casses"] == []


def test_lint_base_pages_are_exempt_from_page_checks():
    report = lint(healthy_wiki())
    assert report["orphelines"] == []
    assert report["absentes_de_lindex"] == []
    assert report["frontmatter_invalide"] == []


def test_lint_base_pages_still_checked_for_broken_links():
    pages = healthy_wiki()
    pages["wiki/index.md"] += "- [[concepts/disparue]]\n"
    assert lint(pages)["liens_casses"] == [{"page": "wiki/index.md", "lien": "concepts/disparue"}]

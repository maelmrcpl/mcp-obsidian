import os

os.environ.setdefault("KEY", "test")

import pytest

import server
from rules import RuleError

PAGE = """---
title: Scrum
type: concept
created: 2026-10-22
updated: 2026-10-22
sources: [raw/agile.md]
tags: [agile]
---
Corps.
"""

LOG = "# Wiki Log\n\n## [2026-10-21] lint | Ancien\n\nIssues found: aucun\n"


class FakeClient:
    def __init__(self, files=None):
        self.files = dict(files or {})

    def exists(self, path):
        return path in self.files

    def folder_exists(self, folder):
        return any(p.startswith(folder + "/") for p in self.files)

    def read_note(self, path):
        return self.files[path]

    def create_note(self, path, content):
        self.files[path] = content

    def append_to_note(self, path, content):
        self.files[path] += content

    def list_notes(self, folder=""):
        prefix = folder.strip("/") + "/" if folder.strip("/") else ""
        entries = set()
        for p in self.files:
            if p.startswith(prefix):
                rest = p[len(prefix):]
                entries.add(rest.split("/")[0] + ("/" if "/" in rest else ""))
        return sorted(entries)

    def search(self, query):
        return [
            {"filename": f"wiki/p{i}.md", "score": -1, "matches": [{"context": f"c{j}"} for j in range(5)]}
            for i in range(30)
        ]


@pytest.fixture
def fake(monkeypatch):
    f = FakeClient({
        "raw/source.md": "intouchable",
        "wiki/log.md": LOG,
        "wiki/concepts/kanban.md": PAGE,
    })
    monkeypatch.setattr(server, "client", f)
    return f


def test_create_in_raw_refused(fake):
    with pytest.raises(RuleError, match="raw/"):
        server.create_note("raw/nouveau.md", PAGE)
    assert "raw/nouveau.md" not in fake.files


def test_create_outside_vault_refused(fake):
    with pytest.raises(RuleError):
        server.create_note("wiki/../hors.md", PAGE)


def test_create_without_frontmatter_refused(fake):
    with pytest.raises(RuleError, match="Frontmatter"):
        server.create_note("wiki/concepts/scrum.md", "texte")
    assert "wiki/concepts/scrum.md" not in fake.files


def test_create_valid(fake):
    server.create_note("wiki/concepts/scrum.md", PAGE)
    assert fake.files["wiki/concepts/scrum.md"] == PAGE


def test_create_existing_refused(fake):
    with pytest.raises(RuleError, match="existe déjà"):
        server.create_note("wiki/concepts/kanban.md", PAGE)


def test_create_new_folder_needs_confirmation(fake):
    with pytest.raises(RuleError, match="confirm_new_folder"):
        server.create_note("wiki/features/panier.md", PAGE)
    assert "wiki/features/panier.md" not in fake.files
    server.create_note("wiki/features/panier.md", PAGE, confirm_new_folder=True)
    assert "wiki/features/panier.md" in fake.files


def test_update_requires_matching_expected_content(fake):
    new = PAGE.replace("Corps.", "Nouveau corps.")
    with pytest.raises(RuleError, match="a changé"):
        server.update_note("wiki/concepts/kanban.md", new, "autre contenu")
    assert fake.files["wiki/concepts/kanban.md"] == PAGE
    server.update_note("wiki/concepts/kanban.md", new, PAGE)
    assert fake.files["wiki/concepts/kanban.md"] == new


def test_update_ignores_line_endings(fake):
    new = PAGE.replace("Corps.", "Nouveau corps.")
    server.update_note("wiki/concepts/kanban.md", new, PAGE.replace("\n", "\r\n"))
    assert fake.files["wiki/concepts/kanban.md"] == new


def test_update_in_raw_refused(fake):
    with pytest.raises(RuleError, match="raw/"):
        server.update_note("raw/source.md", PAGE, "intouchable")
    assert fake.files["raw/source.md"] == "intouchable"


def test_append_log_keeps_existing_entries(fake):
    server.append_log("ingest", "Ma source", "Pages created: concepts/scrum")
    log = fake.files["wiki/log.md"]
    assert log.startswith(LOG)
    assert "## [" in log.split("Ancien")[1]
    assert "] ingest | Ma source\n\nPages created: concepts/scrum\n" in log


def test_append_log_when_log_has_no_final_newline(fake):
    fake.files["wiki/log.md"] = LOG.rstrip("\n")
    server.append_log("query", "Question", "Réponse archivée")
    log = fake.files["wiki/log.md"]
    assert "aucun\n\n## [" in log
    assert log.startswith(LOG.rstrip("\n"))


@pytest.mark.parametrize("trailing_newlines", [0, 1, 2, 3])
def test_append_log_always_leaves_exactly_one_blank_line(fake, trailing_newlines):
    base = LOG.rstrip("\n")
    fake.files["wiki/log.md"] = base + "\n" * trailing_newlines
    server.append_log("query", "Question", "Réponse archivée")
    log = fake.files["wiki/log.md"]
    before = log[: log.rindex("## [")]
    if trailing_newlines <= 2:
        assert before == base + "\n\n"
    else:
        assert before == base + "\n\n\n"
    assert log.endswith("] query | Question\n\nRéponse archivée\n")


def test_append_log_invalid_type_refused(fake):
    with pytest.raises(RuleError, match="type de log"):
        server.append_log("blabla", "Titre", "x")
    assert fake.files["wiki/log.md"] == LOG


def test_append_log_secret_refused(fake):
    with pytest.raises(RuleError, match="secret"):
        server.append_log("query", "Titre", "Authorization: Bearer abc")
    assert fake.files["wiki/log.md"] == LOG


def test_search_notes_is_limited(fake):
    results = server.search_notes("x")
    assert len(results) == 20
    assert len(results[0]["matches"]) == 3
    assert results[0]["path"] == "wiki/p0.md"


def test_get_outgoing_links(fake):
    fake.files["wiki/concepts/a.md"] = PAGE + "[[concepts/kanban]] [[concepts/absente|alias]]"
    assert server.get_outgoing_links("wiki/concepts/a.md") == [
        {"link": "concepts/kanban", "path": "wiki/concepts/kanban.md", "exists": True},
        {"link": "concepts/absente", "path": "wiki/concepts/absente.md", "exists": False},
    ]


def test_get_backlinks_reads_only_search_candidates(fake):
    fake.files["wiki/concepts/a.md"] = PAGE + "[[concepts/kanban]]"
    fake.files["wiki/concepts/b.md"] = PAGE + "mention concepts/kanban sans lien"
    fake.search = lambda q: [
        {"filename": "wiki/concepts/a.md"},
        {"filename": "wiki/concepts/b.md"},
        {"filename": "raw/source.md"},
    ]
    assert server.get_backlinks("wiki/concepts/kanban.md") == ["wiki/concepts/a.md"]


def test_get_backlinks_outside_wiki_refused(fake):
    with pytest.raises(RuleError):
        server.get_backlinks("raw/source.md")


def test_lint_wiki_reads_all_pages_and_changes_nothing(fake):
    fake.files["wiki/index.md"] = "# Index\n[[concepts/kanban]]\n"
    before = dict(fake.files)
    report = server.lint_wiki()
    assert set(report) == {
        "liens_casses", "liens_prefixe_wiki", "doublons_non_qualifies",
        "orphelines", "absentes_de_lindex", "frontmatter_invalide",
    }
    assert fake.files == before

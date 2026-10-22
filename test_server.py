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


def test_append_log_invalid_type_refused(fake):
    with pytest.raises(RuleError, match="type de log"):
        server.append_log("blabla", "Titre", "x")
    assert fake.files["wiki/log.md"] == LOG


def test_append_log_secret_refused(fake):
    with pytest.raises(RuleError, match="secret"):
        server.append_log("query", "Titre", "Authorization: Bearer abc")
    assert fake.files["wiki/log.md"] == LOG

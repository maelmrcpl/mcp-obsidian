import pytest

from rules import check_content, check_path

VALID = """---
title: Scrum
type: concept
created: 2026-10-22
updated: 2026-10-22
sources: [raw/agile.md]
tags: [agile]
---
Corps de la page, voir [[concepts/kanban]].
"""


def test_path_valid():
    check_path("wiki/concepts/scrum.md")


@pytest.mark.parametrize("path", [
    "raw/article.md",
    "wiki/../secret.md",
    "/etc/x.md",
    "C:/x.md",
    "notes/scrum.md",
    "wiki/concepts/scrum.txt",
    "wiki/concepts/Mon Concept.md",
])
def test_path_refused(path):
    with pytest.raises(ValueError):
        check_path(path)


def test_path_bad_filename_message_says_kebab_case():
    with pytest.raises(ValueError, match="kebab-case"):
        check_path("wiki/concepts/Mon Concept.md")


def test_content_valid():
    check_content(VALID)


def test_content_without_frontmatter():
    with pytest.raises(ValueError, match="Frontmatter"):
        check_content("Juste du texte")


def test_content_missing_field():
    with pytest.raises(ValueError, match="title"):
        check_content(VALID.replace("title: Scrum\n", ""))


def test_content_invalid_type():
    with pytest.raises(ValueError, match="type invalide"):
        check_content(VALID.replace("type: concept", "type: banane"))


def test_content_wiki_prefix_link():
    with pytest.raises(ValueError, match="wiki/"):
        check_content(VALID + "\n[[wiki/concepts/x]]")


def test_content_secret():
    with pytest.raises(ValueError, match="secret"):
        check_content(VALID + "\nAuthorization: Bearer abc123")

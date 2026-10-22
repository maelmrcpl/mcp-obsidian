import os
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class ObsidianError(Exception):
    pass


class ObsidianClient:
    """Client pour le plugin Obsidian « Local REST API »."""

    def __init__(self, key=None, port=None, host="127.0.0.1", timeout=15.0):
        key = key or os.getenv("KEY")
        port = port or os.getenv("PORT", "27124")
        if not key:
            raise ObsidianError("Variable KEY manquante dans le .env")
        self._client = httpx.Client(
            base_url=f"https://{host}:{port}",
            headers={"Authorization": f"Bearer {key}"},
            verify=False,  # certificat auto-signé du plugin
            timeout=timeout,
        )

    @staticmethod
    def _vault_path(path: str) -> str:
        path = path.replace("\\", "/").lstrip("/")
        if any(part == ".." for part in path.split("/")):
            raise ObsidianError("Chemin invalide : '..' interdit")
        return "/vault/" + quote(path, safe="/")

    def _request(self, method, url, **kwargs) -> httpx.Response:
        try:
            response = self._client.request(method, url, **kwargs)
        except httpx.ConnectError as e:
            raise ObsidianError(
                "Impossible de joindre Obsidian (ouvert ? plugin Local REST API actif ?)"
            ) from e
        if response.status_code == 401:
            raise ObsidianError("Clé d'API refusée (401)")
        if response.status_code == 404:
            raise ObsidianError("Note ou dossier introuvable (404)")
        if response.is_error:
            raise ObsidianError(f"Erreur Obsidian {response.status_code}: {response.text}")
        return response

    def status(self) -> dict:
        return self._request("GET", "/").json()

    def list_notes(self, folder: str = "") -> list[str]:
        url = self._vault_path(folder).rstrip("/") + "/" if folder else "/vault/"
        return self._request("GET", url).json()["files"]

    def read_note(self, path: str) -> str:
        return self._request(
            "GET", self._vault_path(path), headers={"Accept": "text/markdown"}
        ).text

    def create_note(self, path: str, content: str) -> None:
        """Crée la note, ou écrase son contenu si elle existe."""
        self._request(
            "PUT",
            self._vault_path(path),
            content=content.encode("utf-8"),
            headers={"Content-Type": "text/markdown"},
        )

    def append_to_note(self, path: str, content: str) -> None:
        self._request(
            "POST",
            self._vault_path(path),
            content=content.encode("utf-8"),
            headers={"Content-Type": "text/markdown"},
        )

    def delete_note(self, path: str) -> None:
        self._request("DELETE", self._vault_path(path))

    def search(self, query: str, context_length: int = 100) -> list[dict]:
        return self._request(
            "POST",
            "/search/simple/",
            params={"query": query, "contextLength": context_length},
        ).json()

    def active_note(self) -> str:
        return self._request("GET", "/active/", headers={"Accept": "text/markdown"}).text

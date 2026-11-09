"""Cross-platform smoke tests for Aetheris.

Run with:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import app as appmod
import store


class AetherisSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._old_dir = store.DATA_DIR
        self._old_path = store.DB_PATH
        store.DATA_DIR = Path(self._tmp.name)
        store.DB_PATH = store.DATA_DIR / "db.json"

        appmod.app.config.update(
            TESTING=True,
            SITE_URL="https://example.org",
            SECRET_KEY="test-secret",
        )
        self.client = appmod.app.test_client()

    def tearDown(self) -> None:
        store.DATA_DIR = self._old_dir
        store.DB_PATH = self._old_path
        self._tmp.cleanup()

    def get(self, path: str, status: int = 200) -> str:
        response = self.client.get(path)
        self.assertEqual(response.status_code, status, path)
        body = response.get_data(as_text=True)
        response.close()
        return body

    def test_public_pages(self) -> None:
        for path in ("/", "/courses", "/learn", "/session/12345678"):
            body = self.get(path)
            self.assertIn("Aetheris", body)

        self.assertIn('"status":"ok"', self.get("/healthz"))
        self.assertIn('id="lessons-data"', self.get("/learn"))
        self.assertIn("flask-basics", self.get("/learn"))

    def test_admin_pages(self) -> None:
        for path in (
            "/admin",
            "/admin/posts",
            "/admin/posts/new",
            "/admin/posts/1/edit",
            "/admin/users",
            "/admin/settings",
        ):
            self.get(path)

    def test_seo_endpoints(self) -> None:
        self.assertIn("Sitemap:", self.get("/robots.txt"))
        self.assertIn("<urlset", self.get("/sitemap.xml"))

        html = self.get("/courses")
        self.assertIn('href="https://example.org/courses"', html)
        self.assertIn('property="og:title"', html)
        self.assertIn("application/ld+json", html)

    def test_static_assets(self) -> None:
        self.assertIn(".glass-card", self.get("/static/css/main.css"))
        self.assertIn("scroll-progress", self.get("/static/js/site.js"))
        self.assertIn("aetheris.lessons.v1", self.get("/static/js/learn.js"))
        self.assertIn("<svg", self.get("/static/img/logo.svg"))
        self.assertIn("Aetheris", self.get("/static/site.webmanifest"))

    def test_not_found(self) -> None:
        self.get("/session/12", status=404)
        self.get("/does-not-exist", status=404)

    def test_attendance_update(self) -> None:
        response = self.client.post(
            "/session/12345678/update",
            data={"present_1": "1", "approval_1": "approved"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Attendance updated.", response.get_data(as_text=True))

    def test_post_crud(self) -> None:
        self.client.post(
            "/admin/posts/new",
            data={
                "title": "Smoke Test Post",
                "author": "Tester",
                "category": "Testing",
                "status": "Published",
                "body": "hello",
            },
            follow_redirects=True,
        )
        data = json.loads(store.DB_PATH.read_text(encoding="utf-8"))
        post = next(p for p in data["posts"] if p["title"] == "Smoke Test Post")

        edited = self.client.post(
            f"/admin/posts/{post['id']}/edit",
            data={"title": "Smoke Test Post Edited", "status": "Draft"},
            follow_redirects=True,
        )
        self.assertIn("Post updated.", edited.get_data(as_text=True))

        deleted = self.client.post(
            f"/admin/posts/{post['id']}/delete",
            follow_redirects=True,
        )
        self.assertIn("Post deleted.", deleted.get_data(as_text=True))

        data = json.loads(store.DB_PATH.read_text(encoding="utf-8"))
        self.assertFalse(any(p["id"] == post["id"] for p in data["posts"]))

    def test_user_crud(self) -> None:
        self.client.post(
            "/admin/users",
            data={"name": "Smoke User", "email": "smoke@example.com", "role": "Contributor"},
            follow_redirects=True,
        )
        data = json.loads(store.DB_PATH.read_text(encoding="utf-8"))
        user = next(u for u in data["users"] if u["name"] == "Smoke User")

        removed = self.client.post(
            f"/admin/users/{user['id']}/delete",
            follow_redirects=True,
        )
        self.assertIn("User removed.", removed.get_data(as_text=True))

    def test_settings_save(self) -> None:
        response = self.client.post(
            "/admin/settings",
            data={"site_title": "Aetheris", "tagline": "Test tagline", "robots": "User-agent: *\nAllow: /"},
            follow_redirects=True,
        )
        self.assertIn("Settings saved.", response.get_data(as_text=True))

        data = json.loads(store.DB_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["settings"]["tagline"], "Test tagline")


if __name__ == "__main__":
    unittest.main()

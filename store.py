"""Small JSON-backed data store for Aetheris.

The project is intentionally dependency-light: all demo data lives in a single
JSON document (``data/db.json``) which is created and seeded on first run.
This keeps the app cross-platform and easy to run with only Flask installed.

Swap :func:`load` / :func:`save` for a real database layer when you are ready
to move beyond the demo.
"""

from __future__ import annotations

import json
import os
import random
import threading
from datetime import date
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent

# Vercel (and most serverless platforms) mount the project read-only, so the
# JSON store must live in /tmp there. Local runs keep using ./data.
_env_data_dir = os.environ.get("AETHERIS_DATA_DIR")
if _env_data_dir:
    DATA_DIR = Path(_env_data_dir)
elif os.environ.get("VERCEL"):
    DATA_DIR = Path("/tmp") / "aetheris"
else:
    DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "db.json"

_LOCK = threading.Lock()

DEFAULT_SETTINGS: dict[str, Any] = {
    "site_title": "Aetheris",
    "tagline": "Open learning, attendance, and publishing in one place.",
    "description": (
        "Aetheris is a free, open-source platform for interactive courses, "
        "attendance tracking, and content management. Runs anywhere Python runs."
    ),
    "keywords": "aetheris, free, open source, learning platform, flask, attendance, scorm",
    "social_handle": "@aetheris",
    "robots": "User-agent: *\nDisallow: /admin\nAllow: /",
}

DEFAULT_POSTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Welcome to Aetheris",
        "slug": "welcome-to-aetheris",
        "author": "Omonire",
        "category": "Announcements",
        "status": "Published",
        "date": "2026-01-08",
        "views": 4201,
        "body": (
            "Aetheris brings interactive lessons, attendance sessions, and a "
            "lightweight content manager together in a single, dependency-light "
            "Flask app. It is free and open source under the MIT license."
        ),
    },
    {
        "id": 2,
        "title": "Styling with FSCSS",
        "slug": "styling-with-fscss",
        "author": "Omonire",
        "category": "Engineering",
        "status": "Published",
        "date": "2026-02-14",
        "views": 2890,
        "body": (
            "Every Aetheris screen is styled with FSCSS (Figured Shorthand CSS), "
            "compiled ahead of time to plain CSS. Try editing static/fscss/main.fscss "
            "and recompiling with the build script."
        ),
    },
    {
        "id": 3,
        "title": "Roadmap: what's next",
        "slug": "roadmap-whats-next",
        "author": "Omonire",
        "category": "Product",
        "status": "Draft",
        "date": "2026-03-02",
        "views": 0,
        "body": "Planned: real database models, authentication, and per-course enrollment.",
    },
]

DEFAULT_USERS: list[dict[str, Any]] = [
    {"id": 1, "name": "Omonire", "email": "owner@aetheris.dev", "role": "Admin"},
    {"id": 2, "name": "Mara Chen", "email": "mara@aetheris.dev", "role": "Editor"},
    {"id": 3, "name": "Sam Rivera", "email": "sam@aetheris.dev", "role": "Contributor"},
]


def _seed_sessions() -> dict[str, Any]:
    """Create deterministic demo attendance sessions for a few IDs."""
    sessions: dict[str, Any] = {}
    names = [
        "Ada Lovelace",
        "Grace Hopper",
        "Alan Turing",
        "Katherine Johnson",
        "Linus Torvalds",
        "Margaret Hamilton",
        "Dennis Ritchie",
    ]
    for attendance_id in ("12345678", "87654321"):
        rng = random.Random(int(attendance_id))
        students = []
        for i, name in enumerate(names, start=1):
            present = rng.choice([True, False])
            approval = rng.choice(["pending", "approved", "rejected"])
            if approval == "approved":
                present = True
            elif approval == "rejected":
                present = False
            students.append(
                {
                    "student_id": f"S{i:03d}",
                    "name": name,
                    "present": present,
                    "approval": approval,
                }
            )
        sessions[attendance_id] = {"attendance_id": attendance_id, "students": students}
    return sessions


def seed() -> dict[str, Any]:
    """Return a fresh seeded database document."""
    return {
        "settings": dict(DEFAULT_SETTINGS),
        "posts": [dict(p) for p in DEFAULT_POSTS],
        "users": [dict(u) for u in DEFAULT_USERS],
        "sessions": _seed_sessions(),
    }


def _ensure_seeded() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        save(seed())


def load() -> dict[str, Any]:
    """Load the database, creating and seeding it if needed."""
    _ensure_seeded()
    with _LOCK:
        try:
            with DB_PATH.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            data = seed()
            with DB_PATH.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
    # Backfill any missing top-level keys from the seed.
    base = seed()
    for key, value in base.items():
        data.setdefault(key, value)
    return data


def save(data: dict[str, Any]) -> None:
    """Persist the database document."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        tmp = DB_PATH.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, DB_PATH)


def next_id(items: list[dict[str, Any]]) -> int:
    return max((int(item.get("id", 0)) for item in items), default=0) + 1


def slugify(value: str) -> str:
    out = []
    for ch in value.strip().lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "post"


def today_iso() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Post helpers
# ---------------------------------------------------------------------------
def get_posts(data: dict[str, Any]) -> list[dict[str, Any]]:
    posts = data.get("posts", [])
    return sorted(posts, key=lambda p: p.get("date", ""), reverse=True)


def get_post(data: dict[str, Any], post_id: int) -> dict[str, Any] | None:
    for post in data.get("posts", []):
        if int(post.get("id", -1)) == post_id:
            return post
    return None


# ---------------------------------------------------------------------------
# Attendance helpers
# ---------------------------------------------------------------------------
def ensure_session(data: dict[str, Any], attendance_id: str) -> dict[str, Any]:
    sessions = data.setdefault("sessions", {})
    if attendance_id not in sessions:
        rng = random.Random(int(attendance_id))
        names = ["Student One", "Student Two", "Student Three", "Student Four", "Student Five"]
        students = []
        for i, name in enumerate(names, start=1):
            present = rng.choice([True, False])
            approval = rng.choice(["pending", "approved", "rejected"])
            students.append(
                {
                    "student_id": f"S{i:03d}",
                    "name": name,
                    "present": present,
                    "approval": approval,
                }
            )
        sessions[attendance_id] = {"attendance_id": attendance_id, "students": students}
    return sessions[attendance_id]

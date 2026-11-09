"""Aetheris - a free, open-source learning, attendance, and publishing app.

Run locally:
    python app.py

The app is intentionally small and dependency-light (Flask only). Demo data is
stored in ``data/db.json`` and seeded automatically on first launch.
"""

from __future__ import annotations

import os
from datetime import date

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    Response,
)

import store
from content import COURSES, LESSONS, lesson_by_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("AETHERIS_SECRET", "dev-only-change-me")
app.config["SITE_URL"] = os.environ.get("AETHERIS_SITE_URL", "").rstrip("/")

VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Context + helpers
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    data = store.load()
    settings = data.get("settings", {})
    site_url = app.config.get("SITE_URL") or request.url_root.rstrip("/")
    canonical_url = (site_url + request.path).rstrip("/") or site_url
    return {
        "site": settings,
        "site_url": site_url,
        "canonical_url": canonical_url,
        "current_year": date.today().year,
        "app_version": VERSION,
        "is_admin": request.path.startswith("/admin"),
    }


def _validate_attendance_id(attendance_id: str) -> bool:
    return attendance_id.isdigit() and len(attendance_id) == 8


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    data = store.load()
    posts = [p for p in store.get_posts(data) if p.get("status") == "Published"][:3]
    return render_template(
        "index.html",
        active_page="home",
        page_title="Aetheris - Free & open-source learning platform",
        page_description=(
            "Aetheris is a free, open-source platform for interactive courses, "
            "attendance tracking, and lightweight content publishing. Runs anywhere Python runs."
        ),
        featured_posts=posts,
        courses=COURSES,
    )


@app.route("/courses")
def courses():
    return render_template(
        "courses.html",
        active_page="courses",
        page_title="Courses - Aetheris",
        page_description="Browse interactive courses on Flask, FSCSS design systems, and attendance tooling.",
        courses=COURSES,
        lessons=LESSONS,
    )


@app.route("/learn")
def learn():
    return render_template(
        "learn.html",
        active_page="learn",
        page_title="Interactive Lessons - Aetheris",
        page_description="Take interactive lessons with quizzes. Your progress is saved locally in your browser.",
        lessons=LESSONS,
    )


@app.route("/session/<attendance_id>")
def session_view(attendance_id: str):
    if not _validate_attendance_id(attendance_id):
        abort(404)
    data = store.load()
    session = store.ensure_session(data, attendance_id)
    store.save(data)
    return render_template(
        "session.html",
        active_page="session",
        page_title=f"Attendance Session {attendance_id} - Aetheris",
        page_description=f"Live attendance view for session {attendance_id}.",
        attendance_id=attendance_id,
        students=session["students"],
    )


@app.route("/session/<attendance_id>/update", methods=["GET", "POST"])
def session_update(attendance_id: str):
    if not _validate_attendance_id(attendance_id):
        abort(404)
    data = store.load()
    session = store.ensure_session(data, attendance_id)

    if request.method == "POST":
        for student in session["students"]:
            sid = student["student_id"]
            present_val = request.form.get(f"present_{sid}")
            approval_val = request.form.get(f"approval_{sid}")
            if present_val is not None:
                student["present"] = present_val == "1"
            if approval_val in {"approved", "rejected", "pending"}:
                student["approval"] = approval_val
        store.save(data)
        flash("Attendance updated.", "success")
        return redirect(url_for("session_view", attendance_id=attendance_id))

    return render_template(
        "session_update.html",
        active_page="session",
        page_title=f"Update Attendance {attendance_id} - Aetheris",
        page_description=f"Update attendance and approvals for session {attendance_id}.",
        attendance_id=attendance_id,
        students=session["students"],
    )


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
@app.route("/admin")
def admin_dashboard():
    data = store.load()
    posts = store.get_posts(data)
    users = data.get("users", [])
    published = [p for p in posts if p.get("status") == "Published"]
    drafts = [p for p in posts if p.get("status") == "Draft"]
    total_views = sum(int(p.get("views", 0)) for p in posts)
    stats = {
        "posts": len(posts),
        "published": len(published),
        "drafts": len(drafts),
        "views": total_views,
        "users": len(users),
    }
    return render_template(
        "admin/dashboard.html",
        active_page="dashboard",
        page_title="Dashboard - Aetheris Admin",
        page_description="Aetheris admin dashboard.",
        stats=stats,
        posts=posts[:5],
    )


@app.route("/admin/posts")
def admin_posts():
    data = store.load()
    return render_template(
        "admin/posts.html",
        active_page="posts",
        page_title="Posts - Aetheris Admin",
        page_description="Manage blog posts.",
        posts=store.get_posts(data),
    )


@app.route("/admin/posts/new", methods=["GET", "POST"])
def admin_post_new():
    if request.method == "POST":
        data = store.load()
        title = (request.form.get("title") or "").strip()
        if not title:
            flash("A title is required.", "error")
            return redirect(url_for("admin_post_new"))
        slug = (request.form.get("slug") or "").strip() or store.slugify(title)
        data.setdefault("posts", []).append(
            {
                "id": store.next_id(data.get("posts", [])),
                "title": title,
                "slug": store.slugify(slug),
                "author": (request.form.get("author") or "Omonire").strip(),
                "category": (request.form.get("category") or "General").strip(),
                "status": request.form.get("status") if request.form.get("status") in {"Published", "Draft"} else "Draft",
                "date": (request.form.get("date") or store.today_iso()),
                "views": 0,
                "body": (request.form.get("body") or "").strip(),
            }
        )
        store.save(data)
        flash("Post created.", "success")
        return redirect(url_for("admin_posts"))

    return render_template(
        "admin/post_form.html",
        active_page="posts",
        page_title="New Post - Aetheris Admin",
        page_description="Create a post.",
        post=None,
        form_action=url_for("admin_post_new"),
    )


@app.route("/admin/posts/<int:post_id>/edit", methods=["GET", "POST"])
def admin_post_edit(post_id: int):
    data = store.load()
    post = store.get_post(data, post_id)
    if post is None:
        abort(404)

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        if not title:
            flash("A title is required.", "error")
            return redirect(url_for("admin_post_edit", post_id=post_id))
        post["title"] = title
        post["slug"] = store.slugify((request.form.get("slug") or "").strip() or title)
        post["author"] = (request.form.get("author") or post.get("author", "")).strip()
        post["category"] = (request.form.get("category") or "General").strip()
        status = request.form.get("status")
        if status in {"Published", "Draft"}:
            post["status"] = status
        post["date"] = request.form.get("date") or post.get("date", store.today_iso())
        post["body"] = (request.form.get("body") or "").strip()
        store.save(data)
        flash("Post updated.", "success")
        return redirect(url_for("admin_posts"))

    return render_template(
        "admin/post_form.html",
        active_page="posts",
        page_title=f"Edit {post['title']} - Aetheris Admin",
        page_description="Edit a post.",
        post=post,
        form_action=url_for("admin_post_edit", post_id=post_id),
    )


@app.route("/admin/posts/<int:post_id>/delete", methods=["POST"])
def admin_post_delete(post_id: int):
    data = store.load()
    posts = [p for p in data.get("posts", []) if int(p.get("id", -1)) != post_id]
    data["posts"] = posts
    store.save(data)
    flash("Post deleted.", "success")
    return redirect(url_for("admin_posts"))


@app.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    data = store.load()
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        role = request.form.get("role") or "Contributor"
        if not name or not email:
            flash("Name and email are required.", "error")
        else:
            data.setdefault("users", []).append(
                {"id": store.next_id(data.get("users", [])), "name": name, "email": email, "role": role}
            )
            store.save(data)
            flash("User added.", "success")
        return redirect(url_for("admin_users"))

    return render_template(
        "admin/users.html",
        active_page="users",
        page_title="Users - Aetheris Admin",
        page_description="Manage team members.",
        users=data.get("users", []),
    )


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
def admin_user_delete(user_id: int):
    data = store.load()
    data["users"] = [u for u in data.get("users", []) if int(u.get("id", -1)) != user_id]
    store.save(data)
    flash("User removed.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    data = store.load()
    if request.method == "POST":
        settings = data.setdefault("settings", {})
        for key in ("site_title", "tagline", "description", "keywords", "social_handle", "robots"):
            if key in request.form:
                settings[key] = request.form.get(key, "").strip()
        store.save(data)
        flash("Settings saved.", "success")
        return redirect(url_for("admin_settings"))

    return render_template(
        "admin/settings.html",
        active_page="settings",
        page_title="Settings - Aetheris Admin",
        page_description="Configure site identity and SEO.",
        settings=data.get("settings", {}),
    )


# ---------------------------------------------------------------------------
# SEO + health endpoints
# ---------------------------------------------------------------------------
@app.route("/robots.txt")
def robots_txt():
    data = store.load()
    body = data.get("settings", {}).get("robots", "User-agent: *\nAllow: /")
    sitemap_url = url_for("sitemap_xml", _external=True)
    body = f"{body.rstrip()}\n\nSitemap: {sitemap_url}\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    pages = [
        ("index", 1.0, "weekly"),
        ("courses", 0.8, "weekly"),
        ("learn", 0.8, "weekly"),
    ]
    lastmod = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for endpoint, priority, changefreq in pages:
        loc = url_for(endpoint, _external=True)
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return Response("\n".join(lines), mimetype="application/xml")


@app.route("/healthz")
def healthz():
    return {"status": "ok", "version": VERSION}


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_error):
    return (
        render_template(
            "error.html",
            active_page=None,
            page_title="Page not found - Aetheris",
            page_description="The page you are looking for could not be found.",
            code=404,
            message="We could not find that page.",
        ),
        404,
    )


@app.errorhandler(500)
def server_error(_error):
    return (
        render_template(
            "error.html",
            active_page=None,
            page_title="Something went wrong - Aetheris",
            page_description="An unexpected error occurred.",
            code=500,
            message="Something went wrong on our side.",
        ),
        500,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

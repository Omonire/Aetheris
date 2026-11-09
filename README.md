# Aetheris

A free, open-source learning platform built with Flask and styled with **FSCSS**
(Figured Shorthand CSS). Aetheris ships interactive lessons with quizzes, a
course catalog, a JSON-backed content admin, and SEO-ready public pages.

- **Free forever** — MIT licensed, no accounts, no paywalls, no trackers.
- **Cross-platform** — runs on Windows, macOS, Linux, and Docker.
- **Local progress** — lesson scores are stored in the browser, not on a server.
- **SEO-ready** — canonical URLs, Open Graph/Twitter meta, JSON-LD, sitemap,
  robots.txt, and a web manifest.
- **Small footprint** — one Flask dependency at runtime; the compiled CSS is
  committed, so FSCSS is only needed when editing styles.

## Features

- Marketing-style landing page with animated hero, feature grid, and course preview
- Course catalog with availability states
- Interactive `/learn` experience: lesson outline, content, quizzes, best score,
  progress bar, and reset — all client-side with `localStorage`
- Admin area for posts, users, and site settings (JSON persistence)
- Error pages, `/healthz` endpoint, and accessible navigation
- Responsive layout with reduced-motion support

## Quick start

### Windows

```bat
run.bat
```

### macOS / Linux

```bash
chmod +x run.sh
./run.sh
```

Both scripts create a virtual environment, install `requirements.txt`, and start
the app at <http://127.0.0.1:5000>.

### Manual setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Set `PORT` to change the port and `FLASK_DEBUG=0` to disable the debugger.

### Docker

```bash
docker build -t aetheris .
docker run --rm -p 5000:5000 -v "$PWD/data:/app/data" aetheris
```

The `data` volume persists posts, users, and settings between runs.

## Styling with FSCSS

Aetheris is styled with [FSCSS](https://fscss.devtem.org/docs) by Omonire/Figsh.
The source lives in `static/fscss/main.fscss` and compiles to
`static/css/main.css`, which is committed so production needs only Flask.

To rebuild the CSS after editing the source:

```bash
pip install -r requirements-dev.txt   # installs the fscss compiler
python build_css.py
```

`fscss` requires Node.js 20+ on PATH.

The stylesheet uses FSCSS variables (`$token` / `$token!`), shorthands (`bg`,
`rounded`, `py`, `px`, `stack`, `shadow`, `fs`, `fw`, `op`, `pos`, `ta`), and a
reusable `@define cardpad(...)`. FSCSS is not SCSS: selectors are written flat,
without nesting.

## Project structure

```text
app.py               Flask routes, SEO endpoints, error handlers
store.py             JSON persistence and first-run seed data
content.py           Courses and interactive lesson data
build_css.py         Compile main.fscss -> main.css
run.bat / run.sh     Cross-platform launchers
templates/           Jinja templates (public + admin)
static/fscss/        FSCSS source
static/css/          Compiled CSS (committed)
static/js/           site.js (UI) and learn.js (lessons)
static/img/          Logo, Open Graph image
data/db.json         Created automatically; gitignored
```

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Landing page |
| `/courses` | Course catalog |
| `/learn` | Interactive lessons and quizzes |
| `/admin` | Content admin dashboard |
| `/admin/posts` | Create, edit, and delete posts |
| `/admin/users` | Manage demo users |
| `/admin/settings` | Edit site metadata |
| `/session/<id>` | Demo attendance session |
| `/robots.txt`, `/sitemap.xml` | SEO endpoints |
| `/healthz` | Health check |

## Notes

- **Admin has no authentication.** It is intentionally open for demo purposes.
  Put it behind a reverse proxy or add auth before deploying publicly.
- Admin pages are marked `noindex, nofollow` and are excluded from the sitemap.
- Content is stored in `data/db.json` and seeded on first run. Delete the file to
  reset to the defaults.
- Set a production `AETHERIS_SITE_URL` environment variable so canonical and
  social URLs match your domain, and `AETHERIS_SECRET` to a long random value.

## License

MIT — see [LICENSE](LICENSE). Made by Omonire Oghene-Ovie and Aetheris
contributors.

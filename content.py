"""Static learning content for Aetheris courses and interactive lessons.

Keeping lesson content in Python lets the same data drive the course catalog,
the /learn experience, and the JSON payload embedded for the client.
"""

from __future__ import annotations

COURSES: list[dict] = [
    {
        "slug": "flask-foundations",
        "title": "Flask Foundations",
        "level": "Beginner",
        "icon": "terminal",
        "summary": "Routes, Jinja templates, forms, and request handling with a tiny Flask app.",
        "lesson_ids": ["flask-basics", "templates-jinja", "client-js"],
        "available": True,
    },
    {
        "slug": "design-systems",
        "title": "Design Systems with FSCSS",
        "level": "Intermediate",
        "icon": "palette",
        "summary": "Tokens, reusable @define blocks, and shorthands that compile to plain CSS.",
        "lesson_ids": [],
        "available": False,
    },
    {
        "slug": "attendance-tools",
        "title": "Building Attendance Tools",
        "level": "Intermediate",
        "icon": "fact_check",
        "summary": "Model sessions, approvals, and exports for real-world classrooms.",
        "lesson_ids": [],
        "available": False,
    },
]

LESSONS: list[dict] = [
    {
        "id": "flask-basics",
        "title": "Flask Basics",
        "desc": "Learn routes, templates, and request handling.",
        "badge": "Lesson 1",
        "content": [
            "<b>Routes:</b> URLs mapped to Python functions via <code>@app.route</code>.",
            "<b>Templates:</b> Render HTML with variables using Jinja2, e.g. <code>{{ '{{ user }}' }}</code>.",
            "<b>Request data:</b> Read query params and form fields from <code>request</code>.",
        ],
        "quiz": [
            {
                "q": "Which decorator maps a URL to a Flask view function?",
                "options": ["@app.route", "@app.map", "@route", "@url"],
                "answerIndex": 0,
            },
            {
                "q": "Jinja2 templates use which syntax for variables?",
                "options": ["{% var %}", "{{ var }}", "<% var %>", "${var}"],
                "answerIndex": 1,
            },
            {
                "q": "What do you use to read form fields in Flask?",
                "options": ["request.form", "forms.get", "req.data", "body.form"],
                "answerIndex": 0,
            },
        ],
    },
    {
        "id": "templates-jinja",
        "title": "Templates & Jinja2",
        "desc": "Make your pages dynamic with loops and conditions.",
        "badge": "Lesson 2",
        "content": [
            "<b>Loops:</b> Iterate over lists using <code>{% for item in items %}</code>.",
            "<b>Conditions:</b> Show or hide UI with <code>{% if ... %}</code>.",
            "<b>Filters:</b> Format data, for example <code>|lower</code> or <code>|length</code>.",
        ],
        "quiz": [
            {
                "q": "How do you write an if statement in a Jinja template?",
                "options": ["{% if condition %}", "{if condition}", "<% if condition %>", "@if condition"],
                "answerIndex": 0,
            },
            {
                "q": "Which tag is used to iterate in Jinja2?",
                "options": ["{% each %}", "{% loop %}", "{% for %}", "{% repeat %}"],
                "answerIndex": 2,
            },
            {
                "q": "Where do Jinja variables typically appear?",
                "options": ["In code only", "In the HTML output with {{ ... }}", "Only in CSS", "Only in Python"],
                "answerIndex": 1,
            },
        ],
    },
    {
        "id": "client-js",
        "title": "Client-side Interactivity",
        "desc": "Use JavaScript to make learning feel responsive.",
        "badge": "Lesson 3",
        "content": [
            "<b>DOM updates:</b> Change text and HTML based on user actions.",
            "<b>State:</b> Store progress using <code>localStorage</code>.",
            "<b>Event handling:</b> Add listeners for clicks and form submits.",
        ],
        "quiz": [
            {
                "q": "Which browser API stores key/value data locally?",
                "options": ["sessionStorage", "localStorage", "cookies", "filesystem"],
                "answerIndex": 1,
            },
            {
                "q": "Which event fires when a form is submitted?",
                "options": ["onchange", "submit", "keyup", "load"],
                "answerIndex": 1,
            },
            {
                "q": "How do you select elements in vanilla JS by id?",
                "options": ["getElement", "querySelector", "getElementById", "selectById"],
                "answerIndex": 2,
            },
        ],
    },
]


def lesson_by_id(lesson_id: str) -> dict | None:
    return next((lesson for lesson in LESSONS if lesson["id"] == lesson_id), None)

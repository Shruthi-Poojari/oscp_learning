#!/usr/bin/env python3
"""Small Flask viewer for the OSCP notes repository.

Serves every Markdown file in the repo root (one level up from this folder)
with a grouped sidebar, rendered tables, and syntax-highlighted code blocks.
Read-only; discovers files dynamically so new notes appear automatically.
"""
import os
from pathlib import Path

import markdown
from flask import Flask, abort, redirect, render_template, url_for
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

# Repo root = parent of the webapp/ directory.
CONTENT_ROOT = Path(__file__).resolve().parent.parent
IGNORE_DIRS = {"webapp", ".git", ".venv", "node_modules", "__pycache__"}

GROUP_LABELS = {
    "": "General",
    "Notes": "Notes",
    "HTB": "HTB Machines",
    "HTB/samples": "Samples",
}

# Set this to your repo URL after you push (tomorrow) to show a GitHub link in the header.
REPO_URL = ""

MD_EXTENSIONS = ["fenced_code", "tables", "codehilite", "toc", "sane_lists"]
PYGMENTS_CSS = HtmlFormatter(style="monokai").get_style_defs(".codehilite")


def discover():
    """Return {slug: {path, title, group}} for every markdown file in the repo."""
    pages = {}
    for md in sorted(CONTENT_ROOT.rglob("*.md")):
        rel = md.relative_to(CONTENT_ROOT)
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        group_key = str(rel.parent) if str(rel.parent) != "." else ""
        group = GROUP_LABELS.get(group_key, group_key or "General")
        pages[rel.as_posix()] = {
            "path": md,
            "title": extract_title(md, rel.stem),
            "group": group,
        }
    return pages


def extract_title(md_path, fallback):
    try:
        in_fence = False
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence and line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return fallback


def grouped_nav(pages):
    order = ["General", "Notes", "HTB Machines", "Samples"]
    nav = {}
    for slug, meta in pages.items():
        nav.setdefault(meta["group"], []).append((slug, meta["title"]))
    ordered = {g: sorted(nav[g], key=lambda x: x[1]) for g in order if g in nav}
    for g in nav:  # any unexpected groups last
        if g not in ordered:
            ordered[g] = sorted(nav[g], key=lambda x: x[1])
    return ordered


@app.route("/")
def index():
    pages = discover()
    if not pages:
        return "No markdown notes found.", 404
    first = next(iter(grouped_nav(pages).values()))[0][0]
    return redirect(url_for("view", slug=first))


@app.route("/view/<path:slug>")
def view(slug):
    pages = discover()
    meta = pages.get(slug)
    if not meta:
        abort(404)
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    html = md.convert(meta["path"].read_text(encoding="utf-8"))
    toc = getattr(md, "toc", "")
    return render_template(
        "page.html",
        content=html,
        toc=toc,
        nav=grouped_nav(pages),
        current=slug,
        title=meta["title"],
        group=meta["group"],
        repo_url=REPO_URL,
        pygments_css=PYGMENTS_CSS,
    )


if __name__ == "__main__":
    # Bind to localhost only — these are personal notes, not meant to be exposed.
    port = int(os.environ.get("PORT", 8000))
    app.run(host="127.0.0.1", port=port, debug=True)

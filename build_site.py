#!/usr/bin/env python3
"""Build static HTML pages for GitHub Pages deployment."""
import os
import shutil
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent
IGNORE_DIRS = {"webapp", ".git", ".venv", "node_modules", "__pycache__", "dist", "_site", ".github"}

GROUP_LABELS = {
    "": "General",
    "Notes": "Notes",
    "HTB": "HTB Machines",
    "HTB/samples": "Samples",
}

REPO_URL = "https://github.com/Shruthi-Poojari/oscp_learning"
MD_EXTENSIONS = ["fenced_code", "tables", "codehilite", "toc", "sane_lists"]
PYGMENTS_CSS = HtmlFormatter(style="monokai").get_style_defs(".codehilite")


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


def discover():
    pages = {}
    for md in sorted(ROOT.rglob("*.md")):
        rel = md.relative_to(ROOT)
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


def grouped_nav(pages):
    order = ["General", "Notes", "HTB Machines", "Samples"]
    nav = {}
    for slug, meta in pages.items():
        nav.setdefault(meta["group"], []).append((slug, meta["title"]))
    ordered = {g: sorted(nav[g], key=lambda x: x[1]) for g in order if g in nav}
    for g in nav:
        if g not in ordered:
            ordered[g] = sorted(nav[g], key=lambda x: x[1])
    return ordered


def build(output_dir="dist", base_url=""):
    out = ROOT / output_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # Copy static assets
    static_dst = out / "static"
    shutil.copytree(ROOT / "webapp" / "static", static_dst)

    # Copy HTB assets if present
    htb_assets = ROOT / "HTB" / "assets"
    if htb_assets.exists():
        shutil.copytree(htb_assets, out / "HTB" / "assets", dirs_exist_ok=True)

    # Set up Jinja environment with url_for mock
    def static_url_for(endpoint, **values):
        b = base_url.rstrip("/")
        prefix = f"{b}" if b else ""
        if endpoint == "static":
            return f"{prefix}/static/{values.get('filename', '')}"
        if endpoint == "index":
            return f"{prefix}/index.html" if prefix else "index.html"
        if endpoint == "view":
            slug = values.get("slug", "")
            return f"{prefix}/{slug}.html"
        return f"{prefix}/"

    jinja_env = Environment(loader=FileSystemLoader(ROOT / "webapp" / "templates"))
    jinja_env.globals["url_for"] = static_url_for
    template = jinja_env.get_template("page.html")

    pages = discover()
    nav = grouped_nav(pages)

    # Generate each page
    for slug, meta in pages.items():
        md = markdown.Markdown(extensions=MD_EXTENSIONS)
        content_html = md.convert(meta["path"].read_text(encoding="utf-8"))
        toc = getattr(md, "toc", "")

        rendered = template.render(
            content=content_html,
            toc=toc,
            nav=nav,
            current=slug,
            title=meta["title"],
            group=meta["group"],
            repo_url=REPO_URL,
            pygments_css=PYGMENTS_CSS,
            base_url=base_url,
            is_static=True,
        )

        out_file = out / f"{slug}.html"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(rendered, encoding="utf-8")

    # Create root index.html redirecting / mirroring OSCP-Methodology.md.html
    methodology_path = out / "OSCP-Methodology.md.html"
    if methodology_path.exists():
        shutil.copy(methodology_path, out / "index.html")

    # Also add a .nojekyll file to prevent GitHub Pages from ignoring files
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(pages)} static pages into {out}")


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else ""
    build(base_url=base)

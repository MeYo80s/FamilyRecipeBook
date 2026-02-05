#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "RECIPE_BOOK.md"
INDEX = ROOT / "RECIPE_INDEX.md"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_index_sections(index_text: str) -> list[dict[str, list[Path] | str]]:
    sections: list[dict[str, list[Path] | str]] = []
    current: dict[str, list[Path] | str] | None = None
    for line in index_text.splitlines():
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "paths": []}
            sections.append(current)
            continue
        m = re.search(r"\((recipes/[^)]+\.md)\)", line)
        if m and current is not None:
            current["paths"].append(ROOT / m.group(1))
    return sections


def read_recipe(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Missing title heading in {path}")
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:]).strip()
    body = fix_links(body, path)
    return title, body


def fix_links(body: str, recipe_path: Path) -> str:
    link_re = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")

    def repl(match: re.Match[str]) -> str:
        pre, target, post = match.groups()
        target = target.strip()
        if target.startswith(("http://", "https://", "#", "/")):
            return match.group(0)
        rel = target.split(maxsplit=1)[0].strip("<>")
        resolved = (recipe_path.parent / rel).resolve()
        try:
            fixed = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            return match.group(0)
        return f"{pre}{fixed}{post}"

    return link_re.sub(repl, body)


def main() -> None:
    idx = INDEX.read_text(encoding="utf-8")
    sections = parse_index_sections(idx)
    recipes: list[tuple[str, str]] = []
    toc_sections: list[tuple[str, list[tuple[int, str]]]] = []
    counter = 1
    for section in sections:
        section_title = str(section["title"])
        section_entries: list[tuple[int, str]] = []
        for path in section["paths"]:
            if not path.exists():
                continue
            title, body = read_recipe(path)
            recipes.append((title, body))
            section_entries.append((counter, title))
            counter += 1
        toc_sections.append((section_title, section_entries))

    lines: list[str] = [
        "# Family Favorite Recipe Book",
        "",
        "A collection of our favorite family recipes and stories.",
        "",
        "## Table of Contents",
        "- [How to Use This Book](#how-to-use-this-book)",
    ]

    lines.append("")
    lines.append("| Category | Category |")
    lines.append("| --- | --- |")

    def format_cell(section_title: str, section_entries: list[tuple[int, str]]) -> str:
        parts = [f"**{section_title}**"]
        if not section_entries:
            parts.append("_Coming soon_")
            return "<br>".join(parts)
        parts.extend(
            f"[{number}) {title}](#{number}-{slugify(title)})"
            for number, title in section_entries
        )
        return "<br>".join(parts)

    for i in range(0, len(toc_sections), 2):
        left_title, left_entries = toc_sections[i]
        left_cell = format_cell(left_title, left_entries)
        right_cell = ""
        if i + 1 < len(toc_sections):
            right_title, right_entries = toc_sections[i + 1]
            right_cell = format_cell(right_title, right_entries)
        lines.append(f"| {left_cell} | {right_cell} |")

    lines.extend([
        "",
        "## How to Use This Book",
        "- Add/edit recipes in `recipes/`.",
        "- Keep `RECIPE_INDEX.md` updated with links to each recipe.",
        "- Regenerate this file with `python3 scripts/generate_recipe_book.py`.",
        "",
        "---",
    ])

    for i, (title, body) in enumerate(recipes, start=1):
        lines.extend([
            "",
            f"## {i}) {title}",
            body,
            "",
            "---",
        ])

    if lines[-1] == "---":
        lines.pop()

    BOOK.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

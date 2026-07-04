from __future__ import annotations

import re
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin


GENERATED_MARKER = "<!-- generated: thinking-handbook -->"
CHAPTER_RE = re.compile(r"^chapter-(?P<number>\d+)-(?P<slug>.+)$")


class ThinkingHandbookPlugin(BasePlugin):
    """Generate homepage, chapter indexes, and nav from chapter directories."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        docs_dir = Path(config["docs_dir"])
        docs_dir.mkdir(parents=True, exist_ok=True)

        chapters = _discover_chapters(docs_dir)
        _write_homepage(docs_dir / "index.md", chapters)

        nav = [{"Home": "index.md"}]
        for chapter in chapters:
            _write_chapter_index(chapter)
            entries = [str(chapter.index_path.relative_to(docs_dir))]
            entries.extend(str(page.path.relative_to(docs_dir)) for page in chapter.pages)
            nav.append({chapter.title: entries})

        config["nav"] = nav
        return config


class Chapter:
    def __init__(self, path: Path, title: str, pages: list["PageInfo"]) -> None:
        self.path = path
        self.title = title
        self.pages = pages
        self.index_path = path / "index.md"


class PageInfo:
    def __init__(self, path: Path, title: str) -> None:
        self.path = path
        self.title = title


def _discover_chapters(docs_dir: Path) -> list[Chapter]:
    chapters: list[Chapter] = []
    for chapter_dir in sorted(docs_dir.glob("chapter-*")):
        if not chapter_dir.is_dir():
            continue

        pages = [
            PageInfo(path=page, title=_extract_title(page))
            for page in sorted(chapter_dir.glob("*.md"))
            if page.name != "index.md"
        ]
        chapters.append(Chapter(chapter_dir, _chapter_title(chapter_dir, pages), pages))
    return chapters


def _chapter_title(chapter_dir: Path, pages: list[PageInfo]) -> str:
    match = CHAPTER_RE.match(chapter_dir.name)
    if not match:
        return _title_from_slug(chapter_dir.name)

    number = int(match.group("number"))
    for page in pages:
        metadata = _extract_front_matter(page.path)
        if metadata.get("chapter_title"):
            return f"Chapter {number} - {metadata['chapter_title']}"

    label = _title_from_slug(match.group("slug"))
    return f"Chapter {number} - {label}"


def _title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


def _extract_title(path: Path) -> str:
    metadata = _extract_front_matter(path)
    if metadata.get("title"):
        return metadata["title"]

    in_front_matter = False
    first_line = True
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if first_line and line == "---":
            in_front_matter = True
            first_line = False
            continue
        first_line = False

        if in_front_matter:
            if line == "---":
                in_front_matter = False
            continue

        if line.startswith("# "):
            return line[2:].strip()

    return _title_from_slug(path.stem)


def _extract_front_matter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")
    return metadata


def _write_homepage(index_path: Path, chapters: list[Chapter]) -> None:
    _ensure_generated_or_missing(index_path)

    lines = [
        GENERATED_MARKER,
        "",
        "# Thinking in English: A Hindi to Natural Spoken English Handbook",
        "",
        "A static documentation website for the handbook Markdown files.",
        "",
        "## Chapters",
        "",
    ]
    if chapters:
        for chapter in chapters:
            rel = chapter.index_path.relative_to(index_path.parent).as_posix()
            lines.append(f"- [{chapter.title}]({rel})")
    else:
        lines.append("No chapters have been added yet.")

    lines.extend(
        [
            "",
            "## Search",
            "",
            "Use the search box at the top of the page to find handbook pages by keyword.",
            "",
        ]
    )
    index_path.write_text("\n".join(lines), encoding="utf-8")


def _write_chapter_index(chapter: Chapter) -> None:
    _ensure_generated_or_missing(chapter.index_path)

    lines = [
        GENERATED_MARKER,
        "",
        f"# {chapter.title}",
        "",
        "## Pattern Families",
        "",
    ]

    if chapter.pages:
        for number, page in enumerate(chapter.pages, start=1):
            lines.append(f"{number}. [{page.title}]({page.path.name})")
            lines.append("")
    else:
        lines.append("No pattern families have been added yet.")
        lines.append("")

    chapter.index_path.write_text("\n".join(lines), encoding="utf-8")


def _ensure_generated_or_missing(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if text.startswith(GENERATED_MARKER):
        return
    raise RuntimeError(
        f"{path} already exists and is not marked as generated. "
        "Refusing to overwrite handbook content."
    )

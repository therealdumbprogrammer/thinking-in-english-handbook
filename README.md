# Thinking in English Handbook

Static documentation website for the Hindi to Natural Spoken English handbook.

## License

This repository is proprietary and all rights are reserved. The handbook
content, lesson data, generated documentation, scripts, templates,
configuration, images, and other assets may not be copied, redistributed,
scraped, bulk downloaded, used to create datasets, or used to train AI or
machine learning systems without prior written permission.

See [LICENSE](LICENSE) for the full terms.

The handbook Markdown files under `docs/chapter-*` are treated as immutable content. The site automation generates only homepage, chapter index, and navigation infrastructure.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000/`.

## Build

```bash
mkdocs build --strict
```

The generated static site is written to `site/`.

## GitHub Pages

```bash
mkdocs gh-deploy --strict
```

The MkDocs plugin scans `docs/chapter-*` on every serve/build, generates chapter indexes, and builds navigation automatically. Add new handbook Markdown files to the correct chapter directory; no manual navigation edits are required.

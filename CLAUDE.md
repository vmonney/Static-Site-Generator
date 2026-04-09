# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Requires **Python 3.13+** (see `.python-version`). Use **uv** so the pinned interpreter and dev tools match the lockfile (`uv sync` after clone).

- **Run the main script:** `bash main.sh` (uses `uv run python src/main.py`)
- **Run all tests:** `bash test.sh` (uses `uv run python -m unittest discover -s src`)
- **Run a single test file:** `uv run python -m unittest src/test_textnode.py` or `uv run python -m unittest src/test_htmlnode.py`

## Architecture

This is a Python static site generator that converts Markdown content to HTML. The pipeline flows: raw text → `TextNode` (intermediate representation) → `HTMLNode` (HTML tree) → rendered HTML files written to `public/`.

### Core abstractions

- **[src/textnode.py](src/textnode.py)** — `TextNode` represents an inline text segment with a `TextType` enum (`TEXT`, `BOLD`, `ITALIC`, `CODE`, `LINK`, `IMAGE`) and an optional URL. This is the intermediate format between Markdown parsing and HTML rendering.
- **[src/htmlnode.py](src/htmlnode.py)** — `HTMLNode` is the base class for an HTML element tree. `LeafNode` (subclass) renders a tag with a text value and no children. A `ParentNode` subclass (to be added) will handle elements with children.
- **[src/main.py](src/main.py)** — Entry point. Will orchestrate reading content, converting to nodes, and writing output to `public/`.

### Output

Static files are served from `public/` (`index.html`, `styles.css`).
# About This Site

This website is both a Tolkien-themed blog and a live demonstration of my Python static site generator.

## Project snapshot

- Repository: [Static-Site-Generator](https://github.com/vmonney/Static-Site-Generator)
- Language: `Python 3.13`
- Tooling: `uv`, Ruff, `unittest`
- Deployment target: GitHub Pages from the `docs/` folder

## Supported Markdown features

The generator currently supports:

1. Headings (`#`, `##`, `###`)
2. **Bold**, _italic_, and `inline code`
3. Code blocks
4. Links and images
5. Blockquotes
6. Ordered and unordered lists

### Example code block

```python
def build_site(basepath: str = "/") -> None:
    print(f"Building site with basepath={basepath}")
```

### Example quote

> "Not all those who wander are lost."
>
> -- J.R.R. Tolkien

## How generation works

The pipeline turns Markdown text into HTML using intermediate nodes:

```text
Markdown (.md files in content/)
    -> inline/block parsing
    -> TextNode representation
    -> HTMLNode tree
    -> rendered HTML in docs/
```

Core implementation is in `src/main.py` with support modules in `src/`.

## Commands I use

- Local build and preview: `bash main.sh`
- Run tests: `bash test.sh`
- GitHub Pages build: `./build.sh`

If you want to browse the generated pages directly, open [Home](/) or [Contact](/contact/).

# Static-Site-Generator

A small static site generator that converts Markdown files into HTML pages using a shared template.

## Recipe: Generate a Website from Markdown

### 1) Add your content

- Put `.md` files in `content/`.
- Nested folders are supported and become nested routes.
- Each page should include an H1 (`# Title`) because it is used for `{{ Title }}`.

Example:

```text
content/
  index.md
  contact/
    index.md
  blog/
    first-post.md
```

### 2) Define the HTML template

Edit `template.html` and include both placeholders:

- `{{ Title }}` for the page title
- `{{ Content }}` for generated HTML content

Example skeleton:

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{{ Title }}</title>
    <link rel="stylesheet" href="/index.css" />
  </head>
  <body>
    {{ Content }}
  </body>
</html>
```

### 3) Add static assets

- Put CSS, images, and other static files in `static/`.
- They are copied to the build output directory during generation.

### 4) Build locally (default basepath)

```bash
uv run python src/main.py
```

This generates the site into `docs/` with basepath `/`.

### 5) Build for GitHub Pages

Use the production build script:

```bash
./build.sh
```

`build.sh` currently runs:

```bash
python3 src/main.py "/Static-Site-Generator/"
```

If your repository name is different, update the basepath in `build.sh` to:

```bash
python3 src/main.py "/YOUR_REPO_NAME/"
```

### 6) Preview locally

```bash
bash main.sh
```

Then open: `http://localhost:8888`.

### 7) Deploy with GitHub Pages

1. Commit and push your changes (including `docs/`).
2. In GitHub: **Settings -> Pages**
3. Source: **Deploy from a branch**
4. Branch: **main**
5. Folder: **/docs**

Your site URL will be:

`https://USERNAME.github.io/REPO_NAME/`

## Notes

- Root-relative links in generated HTML are rewritten using the selected basepath:
  - `href="/..."`
  - `src="/..."`
- Local builds default to `/`; production builds should use your repo basepath.
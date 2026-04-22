import os

from copystatic import copy_files_recursive
from inline_markdown import markdown_to_html_node

STATIC_DIR = "static"
PUBLIC_DIR = "public"
CONTENT_DIR = "content"
TEMPLATE_FILE = "template.html"


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[1:].strip()
    raise Exception("No h1 header found")


def generate_pages(content_dir: str, template_path: str, public_dir: str) -> None:
    generate_pages_recursive(content_dir, template_path, public_dir)


def generate_pages_recursive(
    dir_path_content: str, template_path: str, dest_dir_path: str
) -> None:
    for entry in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, entry)
        if os.path.isfile(source_path):
            if not source_path.endswith(".md"):
                continue
            destination_file = f"{os.path.splitext(entry)[0]}.html"
            destination_path = os.path.join(dest_dir_path, destination_file)
            generate_page(source_path, template_path, destination_path)
            continue

        destination_dir = os.path.join(dest_dir_path, entry)
        generate_pages_recursive(source_path, template_path, destination_dir)


def generate_page(from_path: str, template_path: str, dest_path: str) -> None:
    print(
        f"Generating page from {from_path} to {dest_path} using {template_path}"
    )

    with open(from_path) as markdown_file:
        markdown = markdown_file.read()

    with open(template_path) as template_file:
        template = template_file.read()

    content_html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    full_html = template.replace("{{ Title }}", title).replace(
        "{{ Content }}", content_html
    )

    destination_dir = os.path.dirname(dest_path)
    if destination_dir != "":
        os.makedirs(destination_dir, exist_ok=True)

    with open(dest_path, "w") as output_file:
        output_file.write(full_html)


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_source_path = os.path.join(project_root, STATIC_DIR)
    public_dest_path = os.path.join(project_root, PUBLIC_DIR)
    content_path = os.path.join(project_root, CONTENT_DIR)
    template_path = os.path.join(project_root, TEMPLATE_FILE)

    print(f"Copying static files from {static_source_path} to {public_dest_path}")
    copy_files_recursive(static_source_path, public_dest_path)
    generate_pages_recursive(content_path, template_path, public_dest_path)


if __name__ == "__main__":
    main()

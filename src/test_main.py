import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from main import extract_title, generate_pages_recursive


class TestExtractTitle(unittest.TestCase):
    def test_extracts_h1_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_strips_title_whitespace(self):
        self.assertEqual(extract_title("#   Hello World   "), "Hello World")

    def test_raises_when_no_h1(self):
        with self.assertRaises(Exception):
            extract_title("## Not h1\nSome text")


class TestGeneratePagesRecursive(unittest.TestCase):
    def test_generates_html_for_nested_markdown_files(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            content_dir = temp_path / "content"
            nested_dir = content_dir / "blog"
            public_dir = temp_path / "public"
            template_path = temp_path / "template.html"

            nested_dir.mkdir(parents=True)
            public_dir.mkdir()

            (content_dir / "index.md").write_text("# Home\nWelcome")
            (nested_dir / "about.md").write_text("# About\nAll about this site")
            template_path.write_text(
                "<html><head><title>{{ Title }}</title></head><body>{{ Content }}</body></html>"
            )

            generate_pages_recursive(
                str(content_dir), str(template_path), str(public_dir)
            )

            root_output = public_dir / "index.html"
            nested_output = public_dir / "blog" / "about.html"

            self.assertTrue(root_output.exists())
            self.assertTrue(nested_output.exists())
            self.assertIn("<title>Home</title>", root_output.read_text())
            self.assertIn("<title>About</title>", nested_output.read_text())


if __name__ == "__main__":
    unittest.main()

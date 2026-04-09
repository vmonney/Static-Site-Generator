import unittest

from inline_markdown import split_nodes_delimiter
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_delimiter_example(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold_delimiter(self):
        node = TextNode(
            "This is text with a **bolded phrase** in the middle", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
        )

    def test_italic_single_underscore(self):
        node = TextNode("Some _italic_ words here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Some ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" words here", TextType.TEXT),
            ],
        )

    def test_no_delimiter_in_text(self):
        node = TextNode("plain text only", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("plain text only", TextType.TEXT)])

    def test_multiple_pairs_same_string(self):
        node = TextNode("a **b** c **d** e", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("a ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
                TextNode(" c ", TextType.TEXT),
                TextNode("d", TextType.BOLD),
                TextNode(" e", TextType.TEXT),
            ],
        )

    def test_non_text_nodes_pass_through_unchanged(self):
        bold = TextNode("already bold", TextType.BOLD)
        text = TextNode("plain **split** me", TextType.TEXT)
        link = TextNode("link", TextType.LINK, "https://example.com")
        new_nodes = split_nodes_delimiter([bold, text, link], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("already bold", TextType.BOLD),
                TextNode("plain ", TextType.TEXT),
                TextNode("split", TextType.BOLD),
                TextNode(" me", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_empty_delimited_segment(self):
        node = TextNode("before `` after", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("", TextType.CODE),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_unclosed_delimiter_raises(self):
        node = TextNode("only `open", TextType.TEXT)
        with self.assertRaises(ValueError) as ctx:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("closing delimiter", str(ctx.exception).lower())

    def test_unclosed_bold_raises(self):
        node = TextNode("start **no end", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_odd_number_of_delimiters_raises(self):
        node = TextNode("**a** extra **", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_preserves_url_on_text_nodes(self):
        node = TextNode("a `b` c", TextType.TEXT, "https://ignored-for-text")
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        for n in new_nodes:
            self.assertEqual(n.url, "https://ignored-for-text")

    def test_does_not_split_inside_non_text_types(self):
        """Underscores inside BOLD are left as literal (no nested inline)."""
        nodes = [
            TextNode("before ", TextType.TEXT),
            TextNode("_not_italic_", TextType.BOLD),
            TextNode(" after", TextType.TEXT),
        ]
        out = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertEqual(out, nodes)

    def test_chained_code_then_bold_on_plain_text_segments(self):
        node = TextNode("say `x` then **y**", TextType.TEXT)
        after_code = split_nodes_delimiter([node], "`", TextType.CODE)
        after_bold = split_nodes_delimiter(after_code, "**", TextType.BOLD)
        self.assertEqual(
            after_bold,
            [
                TextNode("say ", TextType.TEXT),
                TextNode("x", TextType.CODE),
                TextNode(" then ", TextType.TEXT),
                TextNode("y", TextType.BOLD),
                TextNode("", TextType.TEXT),
            ],
        )


if __name__ == "__main__":
    unittest.main()

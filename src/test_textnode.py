import unittest
from textnode import TextNode, TextType, text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("click me", TextType.LINK, "https://example.com")
        node2 = TextNode("click me", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)

    def test_not_equal_different_text(self):
        node = TextNode("hello", TextType.TEXT)
        node2 = TextNode("goodbye", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_not_equal_different_type(self):
        node = TextNode("same words", TextType.BOLD)
        node2 = TextNode("same words", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_equal_different_url(self):
        node = TextNode("link", TextType.LINK, "https://a.com")
        node2 = TextNode("link", TextType.LINK, "https://b.com")
        self.assertNotEqual(node, node2)

    def test_not_equal_url_none_vs_set(self):
        node = TextNode("link", TextType.LINK)
        node2 = TextNode("link", TextType.LINK, "https://example.com")
        self.assertNotEqual(node, node2)

    def test_eq_both_urls_none(self):
        node = TextNode("plain", TextType.TEXT)
        node2 = TextNode("plain", TextType.TEXT, None)
        self.assertEqual(node, node2)

    def test_not_equal_none_url_vs_empty_string_url(self):
        node = TextNode("alt", TextType.IMAGE)
        node2 = TextNode("alt", TextType.IMAGE, "")
        self.assertNotEqual(node, node2)

    def test_not_equal_same_text_and_url_different_text_type(self):
        shared_text = "same"
        shared_url = "https://example.com/asset.png"
        link = TextNode(shared_text, TextType.LINK, shared_url)
        image = TextNode(shared_text, TextType.IMAGE, shared_url)
        self.assertNotEqual(link, image)

    def test_not_equal_text_vs_code_same_string(self):
        node = TextNode("x = 1", TextType.TEXT)
        node2 = TextNode("x = 1", TextType.CODE)
        self.assertNotEqual(node, node2)

    def test_eq_empty_text(self):
        node = TextNode("", TextType.TEXT)
        node2 = TextNode("", TextType.TEXT, None)
        self.assertEqual(node, node2)

    def test_eq_code_and_italic(self):
        self.assertEqual(
            TextNode("`x`", TextType.CODE),
            TextNode("`x`", TextType.CODE),
        )
        self.assertEqual(
            TextNode("emphasis", TextType.ITALIC),
            TextNode("emphasis", TextType.ITALIC),
        )

    def test_eq_image_with_url(self):
        node = TextNode("alt text", TextType.IMAGE, "https://cdn.example.com/p.png")
        node2 = TextNode("alt text", TextType.IMAGE, "https://cdn.example.com/p.png")
        self.assertEqual(node, node2)

    def test_repr(self):
        bold = TextNode("hello", TextType.BOLD)
        self.assertEqual(repr(bold), "TextNode(hello, bold, None)")
        link = TextNode("go", TextType.LINK, "https://a.org")
        self.assertEqual(repr(link), "TextNode(go, link, https://a.org)")

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold text")

    def test_italic(self):
        node = TextNode("italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italic text")

    def test_code(self):
        node = TextNode("x = 1", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "x = 1")

    def test_link(self):
        node = TextNode("click me", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "click me")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode("alt text", TextType.IMAGE, "https://cdn.example.com/img.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props["src"], "https://cdn.example.com/img.png")
        self.assertEqual(html_node.props["alt"], "alt text")

    def test_text_to_html_renders(self):
        node = TextNode("hello", TextType.BOLD)
        self.assertEqual(text_node_to_html_node(node).to_html(), "<b>hello</b>")

    def test_invalid_type_raises(self):
        from unittest.mock import MagicMock
        node = TextNode("x", TextType.TEXT)
        node.text_type = MagicMock()
        node.text_type.__class__ = type(TextType.TEXT)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()
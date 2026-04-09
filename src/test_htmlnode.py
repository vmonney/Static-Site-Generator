import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_none(self):
        node = HTMLNode(props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty_dict(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_attribute(self):
        node = HTMLNode(props={"href": "https://www.google.com"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com"')

    def test_props_to_html_multiple_attributes(self):
        node = HTMLNode(
            props={
                "href": "https://www.google.com",
                "target": "_blank",
            }
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_repr_shows_fields(self):
        node = HTMLNode(tag="p", value="hi", children=None, props={"class": "x"})
        r = repr(node)
        self.assertIn("p", r)
        self.assertIn("hi", r)
        self.assertIn("class", r)

    def test_to_html_raises(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com">Click me!</a>',
        )

    def test_leaf_to_html_no_tag_returns_raw_value(self):
        node = LeafNode(None, "plain text")
        self.assertEqual(node.to_html(), "plain text")

    def test_leaf_to_html_raises_when_value_is_none(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_repr_omits_children(self):
        node = LeafNode("span", "x", {"class": "y"})
        r = repr(node)
        self.assertIn("LeafNode", r)
        self.assertIn("span", r)
        self.assertIn("x", r)
        self.assertIn("class", r)
        self.assertNotIn("children", r)


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_with_props(self):
        node = ParentNode("a", [LeafNode(None, "click")], {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">click</a>')

    def test_to_html_deeply_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "section",
                    [
                        ParentNode("p", [LeafNode("b", "deep")]),
                    ],
                )
            ],
        )
        self.assertEqual(node.to_html(), "<div><section><p><b>deep</b></p></section></div>")

    def test_to_html_mixed_parent_and_leaf_children(self):
        node = ParentNode(
            "ul",
            [
                ParentNode("li", [LeafNode("b", "first")]),
                ParentNode("li", [LeafNode(None, "second")]),
            ],
        )
        self.assertEqual(node.to_html(), "<ul><li><b>first</b></li><li>second</li></ul>")

    def test_raises_without_tag(self):
        node = ParentNode(None, [LeafNode("span", "x")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_raises_with_empty_children(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_raises_with_none_children(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()


if __name__ == "__main__":
    unittest.main()
